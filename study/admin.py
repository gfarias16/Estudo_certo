from django import forms
from django.contrib import admin

from .models import Attempt, Discipline, Document, Excerpt, Question, StudyProfile, Topic

admin.site.site_header = "Projeto Questões · Conteúdo"
admin.site.site_title = "Projeto Questões"
admin.site.index_title = "Administração do estudo"


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = "__all__"

    def clean(self):
        data = super().clean()
        if data.get("status") == Question.Status.REVIEWED and "excerpts" in data and not data["excerpts"]:
            self.add_error("excerpts", "Questão conferida exige ao menos um trecho de referência.")
        return data


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    form = QuestionForm
    list_display = ("key", "revision", "topic", "style", "status", "reviewed_on")
    list_filter = ("status", "topic", "style")
    search_fields = ("key", "prompt")
    filter_horizontal = ("excerpts",)

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.attempts.exists():
            return ("key", "revision", "topic", "prompt", "options", "correct_choice", "explanation", "excerpts")
        return ()

@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "question", "selected_choice", "is_correct", "created_at")
    list_filter = ("user", "is_correct")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Excerpt)
class ExcerptAdmin(admin.ModelAdmin):
    list_display = ("reference", "document", "page")
    search_fields = ("reference", "text")

    def has_change_permission(self, request, obj=None):
        if obj and obj.questions.filter(attempts__isnull=False).exists():
            return False
        return super().has_change_permission(request, obj)


admin.site.register([Discipline, Topic, Document, StudyProfile])
