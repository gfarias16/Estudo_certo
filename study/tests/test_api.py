import uuid
from datetime import timedelta
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from study.models import Attempt, Excerpt, Question, StudyProfile
from study.services import overview, question_queryset


class StudyApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("import_catalog", stdout=StringIO())
        cls.user = get_user_model().objects.create_user(username="estudante", password="only-used-in-isolated-tests")
        cls.other = get_user_model().objects.create_user(username="outra-conta", password="only-used-in-isolated-tests")

    def setUp(self):
        self.client = APIClient()
        self.client.force_login(self.user)
        self.question = Question.objects.first()

    def submit(self, choice=None, request_id=None):
        return self.client.post("/api/v1/attempts/", {
            "question_id": self.question.id,
            "selected_choice": self.question.correct_choice if choice is None else choice,
            "request_id": str(request_id or uuid.uuid4()),
        }, format="json")

    def test_catalog_has_three_hundred_valid_questions_and_eight_topics(self):
        self.assertEqual(Question.objects.count(), 300)
        self.assertEqual(Question.objects.values("topic").distinct().count(), 8)
        for question in Question.objects.all():
            question.full_clean()
            self.assertTrue(question.excerpts.exists())
            self.assertEqual(question.excerpts.first().document.kind, "law")
        positions = [Question.objects.filter(correct_choice=i).count() for i in range(4)]
        self.assertEqual(positions, [75, 75, 75, 75])

    def test_api_requires_authentication(self):
        self.client.logout()
        for path in ["questions/", "topics/", "documents/", "overview/", "profile/"]:
            self.assertEqual(self.client.get("/api/v1/" + path).status_code, 403)

    def test_questions_do_not_leak_answer_or_comments(self):
        response = self.client.get("/api/v1/questions/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 300)
        question = response.data["results"][0]
        for key in ("correct_choice", "explanation", "excerpts"):
            self.assertNotIn(key, question)
        self.assertEqual(set(question["options"][0]), {"text"})

    def test_submission_is_graded_on_server(self):
        response = self.submit()
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data["is_correct"])
        self.assertIn("text", response.data["excerpts"][0])
        self.assertEqual(response.data["correct_choice"], self.question.correct_choice)
        self.assertEqual(Attempt.objects.get().user, self.user)

    def test_assertion_question_returns_both_sources_and_survives_reimport(self):
        self.question = Question.objects.get(key="gms-181")
        public = self.client.get("/api/v1/questions/?topic=fundamentos&page=2")
        self.assertEqual(public.status_code, 200)
        for question in public.data["results"]:
            self.assertNotIn("excerpts", question)
            self.assertNotIn("correct_choice", question)
        response = self.submit()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.data["excerpts"]), 2)
        sources = set(self.question.excerpts.values_list("key", flat=True))
        call_command("import_catalog", stdout=StringIO())
        self.assertEqual(set(self.question.excerpts.values_list("key", flat=True)), sources)
        self.assertEqual(Attempt.objects.count(), 1)

    def test_invalid_choice_does_not_create_attempt(self):
        self.assertEqual(self.submit(choice=4).status_code, 400)
        self.assertFalse(Attempt.objects.exists())

    def test_duplicate_request_is_idempotent(self):
        request_id = uuid.uuid4()
        first = self.submit(request_id=request_id)
        second = self.submit(request_id=request_id)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.data["id"], second.data["id"])
        self.assertEqual(Attempt.objects.count(), 1)

    def test_request_id_cannot_be_reused_for_different_choice(self):
        request_id = uuid.uuid4()
        self.submit(request_id=request_id)
        response = self.submit(choice=(self.question.correct_choice + 1) % 4, request_id=request_id)
        self.assertEqual(response.status_code, 409)
        self.assertEqual(Attempt.objects.count(), 1)

    def test_error_is_resolved_without_erasing_first_answer(self):
        self.submit(choice=(self.question.correct_choice + 1) % 4)
        self.assertEqual(question_queryset(self.user, "errors").count(), 1)
        self.submit()
        self.assertFalse(question_queryset(self.user, "errors").exists())
        result = overview(self.user)
        self.assertEqual(result["first_accuracy"], 0)
        self.assertEqual(result["accuracy"], 50)
        self.assertEqual(result["answered_unique"], 1)
        self.assertEqual(result["pending_errors"], 0)
        self.assertEqual(Attempt.objects.count(), 2)

    def test_answers_are_isolated_between_users(self):
        self.submit(choice=(self.question.correct_choice + 1) % 4)
        result = overview(self.other)
        self.assertEqual(result["total_attempts"], 0)
        self.assertEqual(result["pending_errors"], 0)
        self.assertEqual(question_queryset(self.other, "unseen").count(), 300)

    def test_period_does_not_erase_current_error(self):
        self.submit(choice=(self.question.correct_choice + 1) % 4)
        Attempt.objects.update(created_at=timezone.now() - timedelta(days=40))
        recent = overview(self.user, "7")
        self.assertEqual(recent["total_attempts"], 0)
        self.assertEqual(recent["pending_errors"], 1)
        self.assertIsNone(recent["accuracy"])
        self.assertEqual(overview(self.user, "all")["incorrect"], 1)

    def test_small_sample_is_explicit(self):
        self.submit()
        result = overview(self.user)
        topic = next(t for t in result["topics"] if t["slug"] == self.question.topic.slug)
        self.assertTrue(topic["insufficient_sample"])

    def test_archived_and_draft_are_not_exposed(self):
        self.question.status = Question.Status.ARCHIVED
        self.question.save()
        self.assertEqual(self.client.get("/api/v1/questions/").data["count"], 299)
        self.assertEqual(self.submit().status_code, 409)

    def test_answered_question_cannot_be_edited_in_place(self):
        self.submit()
        self.question.prompt = "Mudança incompatível com o histórico"
        with self.assertRaises(ValidationError):
            self.question.save()

    def test_latest_revision_is_selected_and_inherits_pending_error(self):
        self.submit(choice=(self.question.correct_choice + 1) % 4)
        previous_id = self.question.id
        references = list(self.question.excerpts.all())
        self.question.pk = None
        self.question.revision = 2
        self.question.save()
        self.question.excerpts.set(references)
        active = list(question_queryset(self.user, "errors"))
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0].revision, 2)
        self.assertEqual(question_queryset(self.user).count(), 300)
        result = self.client.post("/api/v1/attempts/", {"question_id": previous_id, "selected_choice": 0, "request_id": str(uuid.uuid4())})
        self.assertEqual(result.status_code, 409)

    def test_catalog_reimport_preserves_attempts(self):
        self.submit()
        call_command("import_catalog", stdout=StringIO())
        self.assertEqual(Question.objects.count(), 300)
        self.assertEqual(Attempt.objects.count(), 1)

    def test_catalog_dry_run_does_not_persist_changes(self):
        Excerpt.objects.filter(key="art-1").update(text="rascunho")
        call_command("import_catalog", dry_run=True, stdout=StringIO())
        self.assertEqual(Excerpt.objects.get(key="art-1").text, "rascunho")

    def test_profile_validation(self):
        self.assertEqual(self.client.patch("/api/v1/profile/", {"daily_minutes": 5}, format="json").status_code, 400)
        self.assertEqual(self.client.patch("/api/v1/profile/", {"daily_minutes": 60}, format="json").status_code, 200)
        self.assertEqual(StudyProfile.objects.get(user=self.user).daily_minutes, 60)

    def test_invalid_filters_return_400(self):
        self.assertEqual(self.client.get("/api/v1/overview/?period=invalid").status_code, 400)
        self.assertEqual(self.client.get("/api/v1/questions/?mode=invalid").status_code, 400)

    def test_sensitive_api_is_not_cacheable(self):
        response = self.client.get("/api/v1/overview/")
        self.assertIn("no-store", response["Cache-Control"])
        self.assertEqual(response["X-Robots-Tag"], "noindex, nofollow")

    def test_csrf_required_for_login_and_mutations(self):
        client = APIClient(enforce_csrf_checks=True)
        response = client.post("/api/v1/login/", {"username": "estudante", "password": "only-used-in-isolated-tests"})
        self.assertEqual(response.status_code, 403)
        token = client.get("/api/v1/session/").data["csrf_token"]
        response = client.post("/api/v1/login/", {"username": "estudante", "password": "only-used-in-isolated-tests"}, HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(client.patch("/api/v1/profile/", {"daily_minutes": 60}).status_code, 403)

    def test_login_is_rate_limited(self):
        client = APIClient()
        client.get("/api/v1/session/")
        token = client.cookies["csrftoken"].value
        for _ in range(10):
            response = client.post("/api/v1/login/", {"username": "desconhecido", "password": "not-a-real-password"}, HTTP_X_CSRFTOKEN=token)
            self.assertEqual(response.status_code, 400)
        response = client.post("/api/v1/login/", {"username": "desconhecido", "password": "not-a-real-password"}, HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 429)

    def test_schema_is_staff_only(self):
        self.assertEqual(self.client.get("/api/schema/").status_code, 403)

    def test_change_password_keeps_session(self):
        result = self.client.post("/api/v1/password/", {"current_password": "only-used-in-isolated-tests", "new_password": "new-pass-only-for-testing-742!"}, format="json")
        self.assertEqual(result.status_code, 200)
        self.assertEqual(self.client.get("/api/v1/overview/").status_code, 200)
