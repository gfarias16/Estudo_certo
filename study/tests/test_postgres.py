import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from io import StringIO
from unittest import skipUnless

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import close_old_connections, connection, connections
from django.test import TestCase, TransactionTestCase
from rest_framework.test import APIClient

from study.database_security import check_privacy, data_api_roles, harden
from study.models import Attempt, Question


@skipUnless(connection.vendor == "postgresql", "Requer PostgreSQL; executado na CI de integração.")
class PostgresPrivacyTests(TestCase):
    def test_data_api_access_is_revoked_and_verified(self):
        if not data_api_roles(connection):
            self.skipTest("Funções da Data API não existem neste banco de teste.")
        with connection.cursor() as cursor:
            cursor.execute("GRANT SELECT ON TABLE study_attempt TO anon")
        with self.assertRaises(CommandError):
            check_privacy(connection)
        harden(connection)
        self.assertTrue(check_privacy(connection))


@skipUnless(connection.vendor == "postgresql", "Concorrência real exige PostgreSQL.")
class PostgresConcurrencyTests(TransactionTestCase):
    def test_simultaneous_identical_submissions_create_one_attempt(self):
        call_command("import_catalog", stdout=StringIO())
        user = get_user_model().objects.create_user(username="concorrencia", password="isolated-test-only")
        question = Question.objects.first()
        request_id = str(uuid.uuid4())
        barrier = threading.Barrier(2)

        def submit():
            close_old_connections()
            try:
                client = APIClient()
                client.force_login(user)
                barrier.wait(timeout=10)
                response = client.post("/api/v1/attempts/", {
                    "question_id": question.pk,
                    "selected_choice": question.correct_choice,
                    "request_id": request_id,
                }, format="json")
                return response.status_code
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: submit(), range(2)))
        self.assertEqual(sorted(results), [200, 201])
        self.assertEqual(Attempt.objects.count(), 1)
