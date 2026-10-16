from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import Attempt, Document, Excerpt, Question, StudyProfile, Topic


class UserSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ("username", "display_name", "is_staff")

    def get_display_name(self, user) -> str:
        return user.first_name or user.username


class SessionSerializer(serializers.Serializer):
    user = UserSerializer(allow_null=True)
    csrf_token = serializers.CharField()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, trim_whitespace=False, max_length=256)


class PasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True, trim_whitespace=False, max_length=256)
    new_password = serializers.CharField(write_only=True, trim_whitespace=False, max_length=256)


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ("slug", "title", "filename", "version", "pages", "kind", "notes")


class ExcerptSerializer(serializers.ModelSerializer):
    document = DocumentSerializer()

    class Meta:
        model = Excerpt
        fields = ("reference", "page", "text", "document")


class TopicSerializer(serializers.ModelSerializer):
    discipline = serializers.CharField(source="discipline.name")

    class Meta:
        model = Topic
        fields = ("slug", "name", "discipline", "position")


class PublicOptionSerializer(serializers.Serializer):
    text = serializers.CharField()


class ExplainedOptionSerializer(PublicOptionSerializer):
    explanation = serializers.CharField()


class QuestionSerializer(serializers.ModelSerializer):
    topic = TopicSerializer()
    options = serializers.SerializerMethodField()
    last_correct = serializers.BooleanField(read_only=True, allow_null=True)
    source_label = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ("id", "key", "revision", "topic", "prompt", "options", "style", "last_correct", "source_label")

    def get_source_label(self, question) -> str:
        return "Questão autoral · Estatuto GMS" if question.topic.discipline.slug == "estatuto-gms" else "Questão autoral"

    @extend_schema_field(PublicOptionSerializer(many=True))
    def get_options(self, question):
        return [{"text": option["text"]} for option in question.options]


class SubmissionSerializer(serializers.Serializer):
    question_id = serializers.IntegerField(min_value=1)
    selected_choice = serializers.IntegerField(min_value=0, max_value=3)
    request_id = serializers.UUIDField()


class CorrectionSerializer(serializers.ModelSerializer):
    correct_choice = serializers.IntegerField(source="question.correct_choice")
    explanation = serializers.CharField(source="question.explanation")
    options = ExplainedOptionSerializer(source="question.options", many=True)
    excerpts = ExcerptSerializer(source="question.excerpts", many=True)

    class Meta:
        model = Attempt
        fields = ("id", "request_id", "selected_choice", "is_correct", "correct_choice", "explanation", "options", "excerpts", "created_at")


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyProfile
        fields = ("daily_minutes",)


class TopicStatsSerializer(serializers.Serializer):
    slug = serializers.CharField()
    name = serializers.CharField()
    position = serializers.IntegerField()
    available = serializers.IntegerField()
    answered = serializers.IntegerField()
    attempts = serializers.IntegerField()
    accuracy = serializers.FloatField(allow_null=True)
    pending_errors = serializers.IntegerField()
    insufficient_sample = serializers.BooleanField()


class DailyStatsSerializer(serializers.Serializer):
    date = serializers.DateField()
    attempts = serializers.IntegerField()
    accuracy = serializers.FloatField(allow_null=True)


class RecommendationSerializer(serializers.Serializer):
    topic_slug = serializers.CharField()
    topic_name = serializers.CharField()
    mode = serializers.ChoiceField(choices=["all", "unseen", "errors"])
    reason = serializers.CharField()


class OverviewSerializer(serializers.Serializer):
    period = serializers.CharField()
    total_attempts = serializers.IntegerField()
    correct = serializers.IntegerField()
    incorrect = serializers.IntegerField()
    accuracy = serializers.FloatField(allow_null=True)
    first_accuracy = serializers.FloatField(allow_null=True)
    answered_unique = serializers.IntegerField()
    available_questions = serializers.IntegerField()
    pending_errors = serializers.IntegerField()
    today_attempts = serializers.IntegerField()
    daily_minutes = serializers.IntegerField()
    topics = TopicStatsSerializer(many=True)
    daily = DailyStatsSerializer(many=True)
    recommendation = RecommendationSerializer(allow_null=True)


class MessageSerializer(serializers.Serializer):
    detail = serializers.CharField()
