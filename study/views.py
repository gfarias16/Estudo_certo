import hashlib
import hmac
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import F
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.views.decorators.http import require_GET
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Attempt, Document, LoginWindow, Question, StudyProfile, Topic
from .serializers import (
    CorrectionSerializer,
    DocumentSerializer,
    LoginSerializer,
    MessageSerializer,
    OverviewSerializer,
    PasswordSerializer,
    ProfileSerializer,
    QuestionSerializer,
    SessionSerializer,
    SubmissionSerializer,
    TopicSerializer,
    UserSerializer,
)
from .services import overview, question_queryset


@require_GET
def health(request):
    return JsonResponse({"status": "ok"})


def session_data(request):
    return {"user": UserSerializer(request.user).data if request.user.is_authenticated else None, "csrf_token": get_token(request)}


@method_decorator(ensure_csrf_cookie, name="dispatch")
class SessionView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(responses=SessionSerializer)
    def get(self, request):
        return Response(session_data(request))


@method_decorator(csrf_protect, name="dispatch")
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=LoginSerializer, responses={200: SessionSerializer, 400: MessageSerializer, 429: MessageSerializer})
    def post(self, request):
        data = LoginSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        now = timezone.now()
        identifiers = [
            "ip:" + request.META.get("REMOTE_ADDR", ""),
            "user:" + data.validated_data["username"].casefold(),
        ]
        keys = [hmac.new(settings.SECRET_KEY.encode(), value.encode(), hashlib.sha256).hexdigest() for value in identifiers]
        # Limpeza oportunista evita crescimento ilimitado e dispensa um serviço de cache.
        LoginWindow.objects.filter(started_at__lt=now - timedelta(days=1)).delete()
        for key in keys:
            bucket, _ = LoginWindow.objects.get_or_create(key=key, defaults={"started_at": now})
            LoginWindow.objects.filter(pk=key, started_at__lt=now - timedelta(minutes=15)).update(started_at=now, count=0)
            updated = LoginWindow.objects.filter(pk=key, count__lt=10).update(count=F("count") + 1)
            if not updated:
                return Response({"detail": "Muitas tentativas. Aguarde 15 minutos para tentar novamente."}, status=429)
        user = authenticate(request, **data.validated_data)
        if not user:
            return Response({"detail": "Usuário ou senha inválidos."}, status=400)
        login(request, user)
        LoginWindow.objects.filter(pk=keys[1]).delete()
        return Response(session_data(request))


class LogoutView(APIView):
    @extend_schema(request=None, responses=MessageSerializer)
    def post(self, request):
        logout(request)
        return Response({"detail": "Sessão encerrada."})


class PasswordView(APIView):
    @extend_schema(request=PasswordSerializer, responses=MessageSerializer)
    def post(self, request):
        data = PasswordSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        if not request.user.check_password(data.validated_data["current_password"]):
            return Response({"detail": "A senha atual está incorreta."}, status=400)
        try:
            validate_password(data.validated_data["new_password"], request.user)
        except ValidationError as exc:
            return Response({"detail": " ".join(exc.messages)}, status=400)
        request.user.set_password(data.validated_data["new_password"])
        request.user.save(update_fields=["password"])
        update_session_auth_hash(request, request.user)
        return Response({"detail": "Senha atualizada."})


class QuestionListView(generics.ListAPIView):
    serializer_class = QuestionSerializer

    @extend_schema(parameters=[
        OpenApiParameter("mode", str, enum=["all", "unseen", "errors"]),
        OpenApiParameter("topic", str),
    ])
    def get(self, request, *args, **kwargs):
        if request.query_params.get("mode", "all") not in {"all", "unseen", "errors"}:
            return Response({"detail": "Filtro de questões inválido."}, status=400)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return question_queryset(self.request.user, self.request.query_params.get("mode", "all"), self.request.query_params.get("topic"))


class SubmissionView(APIView):
    @extend_schema(request=SubmissionSerializer, responses={201: CorrectionSerializer, 200: CorrectionSerializer, 409: MessageSerializer})
    def post(self, request):
        serializer = SubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        existing = Attempt.objects.filter(user=request.user, request_id=data["request_id"]).select_related("question").first()
        if existing:
            return self.replay(existing, data)
        try:
            with transaction.atomic():
                question = Question.objects.select_for_update().filter(
                    pk=data["question_id"], status=Question.Status.REVIEWED,
                    reviewed_on__isnull=False, excerpts__isnull=False,
                ).first()
                if not question:
                    return Response({"detail": "Questão indisponível. Atualize a lista."}, status=409)
                if Question.objects.filter(key=question.key, revision__gt=question.revision, status=Question.Status.REVIEWED).exists():
                    return Response({"detail": "Há uma nova revisão desta questão. Atualize a lista."}, status=409)
                attempt = Attempt.objects.create(
                    user=request.user, question=question, request_id=data["request_id"],
                    selected_choice=data["selected_choice"],
                    is_correct=data["selected_choice"] == question.correct_choice,
                )
        except IntegrityError:
            # O savepoint já foi encerrado: a transação segue utilizável no PostgreSQL.
            existing = Attempt.objects.filter(user=request.user, request_id=data["request_id"]).select_related("question").first()
            if existing:
                return self.replay(existing, data)
            raise
        return Response(CorrectionSerializer(attempt).data, status=status.HTTP_201_CREATED)

    @staticmethod
    def replay(existing, data):
        if existing.question_id != data["question_id"] or existing.selected_choice != data["selected_choice"]:
            return Response({"detail": "Este envio já foi utilizado para outra resposta."}, status=409)
        return Response(CorrectionSerializer(existing).data)


class OverviewView(APIView):
    @extend_schema(parameters=[OpenApiParameter("period", str, enum=["7", "30", "all"])], responses=OverviewSerializer)
    def get(self, request):
        period = request.query_params.get("period", "7")
        if period not in {"7", "30", "all"}:
            return Response({"detail": "Período inválido."}, status=400)
        return Response(OverviewSerializer(overview(request.user, period)).data)


class TopicListView(generics.ListAPIView):
    queryset = Topic.objects.select_related("discipline").all()
    serializer_class = TopicSerializer
    pagination_class = None


class DocumentListView(generics.ListAPIView):
    queryset = Document.objects.order_by("kind", "id")
    serializer_class = DocumentSerializer
    pagination_class = None


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    http_method_names = ["get", "patch", "head", "options"]

    def get_object(self):
        return StudyProfile.objects.get_or_create(user=self.request.user)[0]
