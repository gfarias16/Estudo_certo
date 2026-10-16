import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q


class Discipline(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField("nome", max_length=160)

    def __str__(self):
        return self.name


class Topic(models.Model):
    discipline = models.ForeignKey(Discipline, on_delete=models.PROTECT, related_name="topics")
    slug = models.SlugField(unique=True)
    name = models.CharField("nome", max_length=160)
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["position", "id"]

    def __str__(self):
        return self.name


class Document(models.Model):
    class Kind(models.TextChoices):
        LAW = "law", "Fonte normativa"
        REFERENCE = "reference", "Prova de referência"

    slug = models.SlugField(unique=True)
    title = models.CharField("título", max_length=200)
    filename = models.CharField(max_length=200)
    version = models.CharField("versão", max_length=120)
    sha256 = models.CharField(max_length=64)
    pages = models.PositiveSmallIntegerField()
    kind = models.CharField(max_length=15, choices=Kind.choices)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.title


class Excerpt(models.Model):
    document = models.ForeignKey(Document, on_delete=models.PROTECT, related_name="excerpts")
    key = models.SlugField(unique=True)
    reference = models.CharField("artigo/referência", max_length=160)
    page = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    text = models.TextField("trecho conferido")

    def clean(self):
        if self.document_id and self.page > self.document.pages:
            raise ValidationError({"page": "Página fora do documento."})

    def __str__(self):
        return f"{self.reference} · p. {self.page}"


class Question(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Rascunho"
        REVIEWED = "reviewed", "Conferida tecnicamente"
        ARCHIVED = "archived", "Arquivada"

    class Style(models.TextChoices):
        LITERAL = "literal", "Texto da lei"
        CASE = "case", "Situação prática"
        COMPARISON = "comparison", "Comparação de regras"

    key = models.SlugField()
    revision = models.PositiveSmallIntegerField(default=1)
    topic = models.ForeignKey(Topic, on_delete=models.PROTECT, related_name="questions")
    prompt = models.TextField("enunciado")
    options = models.JSONField("alternativas e comentários")
    correct_choice = models.PositiveSmallIntegerField(validators=[MaxValueValidator(3)])
    explanation = models.TextField("explicação geral")
    excerpts = models.ManyToManyField(Excerpt, related_name="questions")
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.DRAFT)
    style = models.CharField(max_length=15, choices=Style.choices, default=Style.LITERAL)
    reviewed_on = models.DateField(null=True, blank=True)
    review_note = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["key", "revision"], name="unique_question_revision"),
            models.CheckConstraint(condition=Q(correct_choice__lte=3), name="choice_between_zero_three"),
        ]
        ordering = ["topic__position", "key", "revision"]

    def clean(self):
        options = self.options
        valid = isinstance(options, list) and len(options) == 4
        if valid:
            valid = all(
                isinstance(option, dict)
                and isinstance(option.get("text"), str) and option["text"].strip()
                and isinstance(option.get("explanation"), str) and option["explanation"].strip()
                for option in options
            ) and len({option["text"].strip().casefold() for option in options}) == 4
        if not valid:
            raise ValidationError({"options": "Informe quatro alternativas distintas, com texto e comentário."})
        if self.status == self.Status.REVIEWED and (not self.reviewed_on or not self.review_note.strip()):
            raise ValidationError("Registre data e método da conferência técnica antes de publicar.")
        if self.pk and self.attempts.exists():
            previous = type(self).objects.get(pk=self.pk)
            immutable = ("key", "revision", "topic_id", "prompt", "options", "correct_choice", "explanation")
            if any(getattr(previous, field) != getattr(self, field) for field in immutable):
                raise ValidationError("Questão já respondida: crie nova revisão e arquive a anterior.")

    def __str__(self):
        return f"{self.key} · revisão {self.revision}"

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class Attempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="study_attempts")
    question = models.ForeignKey(Question, on_delete=models.PROTECT, related_name="attempts")
    request_id = models.UUIDField(default=uuid.uuid4)
    selected_choice = models.PositiveSmallIntegerField(validators=[MaxValueValidator(3)])
    is_correct = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]
        indexes = [models.Index(fields=["user", "created_at"]), models.Index(fields=["user", "question"])]
        constraints = [
            models.UniqueConstraint(fields=["user", "request_id"], name="unique_user_submission"),
            models.CheckConstraint(condition=Q(selected_choice__lte=3), name="attempt_choice_between_zero_three"),
        ]


class StudyProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    daily_minutes = models.PositiveSmallIntegerField(default=30, validators=[MinValueValidator(10), MaxValueValidator(120)])


class LoginWindow(models.Model):
    """Identificador opaco: não persiste endereço IP ou nome do usuário em claro."""

    key = models.CharField(max_length=64, primary_key=True)
    started_at = models.DateTimeField()
    count = models.PositiveIntegerField(default=0)
