import hashlib
from datetime import date
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from content.statute import DOCUMENTS, EXCERPTS, QUESTIONS, TOPICS
from study.models import Discipline, Document, Excerpt, Question, Topic


class Command(BaseCommand):
    help = "Importa o catálogo autoral conferido, de forma idempotente e sem apagar tentativas."

    def add_arguments(self, parser):
        parser.add_argument("--verify-sources", action="store_true", help="Confere o SHA-256 dos PDFs locais antes da importação.")
        parser.add_argument("--dry-run", action="store_true", help="Valida tudo e reverte a transação sem persistir.")

    @transaction.atomic
    def handle(self, *args, **options):
        if options["verify_sources"]:
            for definition in DOCUMENTS:
                path = Path(settings.BASE_DIR) / "docs" / definition["filename"]
                if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != definition["sha256"]:
                    raise CommandError(f"Documento ausente ou diferente da versão conferida: {definition['filename']}")
        documents = {}
        for definition in DOCUMENTS:
            definition = dict(definition)
            slug = definition.pop("slug")
            documents[slug], _ = Document.objects.update_or_create(slug=slug, defaults=definition)
        discipline, _ = Discipline.objects.get_or_create(slug="estatuto-gms", defaults={"name": "Estatuto GMS"})
        topics = {}
        for position, (slug, name) in enumerate(TOPICS):
            topics[slug], _ = Topic.objects.update_or_create(slug=slug, defaults={"discipline": discipline, "name": name, "position": position})
        excerpts = {}
        for key, (page, reference, text) in EXCERPTS.items():
            values = {"document": documents["estatuto-gms-2026"], "page": page, "reference": reference, "text": text}
            excerpt = Excerpt.objects.filter(key=key).first()
            if excerpt and excerpt.questions.filter(attempts__isnull=False).exists():
                if any(getattr(excerpt, field) != value for field, value in values.items()):
                    raise CommandError(f"Trecho com histórico alterado: {key}. Crie nova referência.")
            excerpt, _ = Excerpt.objects.update_or_create(key=key, defaults=values)
            excerpt.full_clean()
            excerpts[key] = excerpt
        created = 0
        for number, (topic, source, style, prompt, alternatives, explanation) in enumerate(QUESTIONS, 1):
            source_keys = (source,) if isinstance(source, str) else source
            shift = (number - 1) % 4
            rotated = alternatives[-shift:] + alternatives[:-shift] if shift else alternatives
            values = {
                "topic": topics[topic], "prompt": prompt, "style": style,
                "options": [{"text": text, "explanation": comment} for text, comment in rotated],
                "correct_choice": shift, "explanation": explanation,
                "status": Question.Status.REVIEWED, "reviewed_on": date(2026, 10, 15 if number <= 60 else 16),
                "review_note": "Conferência técnica do recorte e do gabarito no PDF fornecido. Enunciado autoral, sem atribuição à banca.",
            }
            question, new = Question.objects.get_or_create(key=f"gms-{number:03}", revision=1, defaults=values)
            for field, value in values.items():
                setattr(question, field, value)
            question.full_clean()
            if question.pk and question.attempts.exists() and set(question.excerpts.values_list("key", flat=True)) != set(source_keys):
                raise CommandError(f"Referência de questão com histórico alterada: {question.key}. Crie nova revisão.")
            question.save()
            question.excerpts.set([excerpts[key] for key in source_keys])
            created += new
        if options["dry_run"]:
            transaction.set_rollback(True)
        self.stdout.write(self.style.SUCCESS(f"{len(QUESTIONS)} questões validadas; {created} novas. " + ("Simulação: nenhuma alteração persistida." if options["dry_run"] else "Importação concluída.")))
