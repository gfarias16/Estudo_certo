from collections import defaultdict
from datetime import timedelta

from django.db.models import Exists, OuterRef, Subquery
from django.utils import timezone

from .models import Attempt, Question, StudyProfile, Topic


def active_questions():
    return Question.objects.filter(
        status=Question.Status.REVIEWED,
        reviewed_on__isnull=False,
        excerpts__isnull=False,
    ).distinct()


def question_queryset(user, mode="all", topic=None):
    # A revisão mais nova representa a pergunta no catálogo; versões antigas preservam o histórico.
    newer = Question.objects.filter(key=OuterRef("key"), revision__gt=OuterRef("revision"), status=Question.Status.REVIEWED)
    questions = active_questions().annotate(has_newer=Exists(newer)).filter(has_newer=False)
    latest = Attempt.objects.filter(user=user, question__key=OuterRef("key")).order_by("-created_at", "-id")
    questions = questions.annotate(
        last_correct=Subquery(latest.values("is_correct")[:1]),
        last_answered_at=Subquery(latest.values("created_at")[:1]),
    )
    if mode == "errors":
        questions = questions.filter(last_correct=False)
    elif mode == "unseen":
        questions = questions.filter(last_correct__isnull=True)
    if topic:
        questions = questions.filter(topic__slug=topic)
    return questions.select_related("topic", "topic__discipline").prefetch_related("excerpts__document")


def accuracy(attempts):
    return round(sum(a.is_correct for a in attempts) * 100 / len(attempts), 1) if attempts else None


def overview(user, period="7"):
    all_attempts = list(
        Attempt.objects.filter(user=user).select_related("question__topic").order_by("created_at", "id")
    )
    now = timezone.localdate()
    days = None if period == "all" else int(period)
    cutoff = now - timedelta(days=days - 1) if days else None
    attempts = [a for a in all_attempts if not cutoff or timezone.localdate(a.created_at) >= cutoff]
    questions = list(question_queryset(user))
    active_keys = {q.key for q in questions}
    first, latest = {}, {}
    for attempt in all_attempts:
        first.setdefault(attempt.question.key, attempt)
        latest[attempt.question.key] = attempt
    pending_keys = {key for key, a in latest.items() if key in active_keys and not a.is_correct}
    by_topic = defaultdict(list)
    for attempt in attempts:
        by_topic[attempt.question.topic_id].append(attempt)
    topic_rows = []
    for topic in Topic.objects.all():
        available = [q for q in questions if q.topic_id == topic.id]
        topic_attempts = by_topic[topic.id]
        topic_rows.append({
            "slug": topic.slug, "name": topic.name, "position": topic.position,
            "available": len(available),
            "answered": len({q.key for q in available if q.key in latest}),
            "attempts": len(topic_attempts),
            "accuracy": accuracy(topic_attempts),
            "pending_errors": sum(q.key in pending_keys for q in available),
            "insufficient_sample": len({a.question.key for a in topic_attempts}) < 5,
        })
    daily = defaultdict(list)
    for attempt in attempts:
        daily[timezone.localdate(attempt.created_at).isoformat()].append(attempt)
    if cutoff:
        for i in range(days):
            daily.setdefault((cutoff + timedelta(days=i)).isoformat(), [])
    first_in_period = [a for a in first.values() if not cutoff or timezone.localdate(a.created_at) >= cutoff]
    profile, _ = StudyProfile.objects.get_or_create(user=user)
    priority = sorted(
        (t for t in topic_rows if t["available"]),
        key=lambda t: (-t["pending_errors"], t["answered"] > 0, t["accuracy"] if t["accuracy"] is not None else 101, t["position"]),
    )
    recommendation = priority[0] if priority else None
    return {
        "period": period,
        "total_attempts": len(attempts),
        "correct": sum(a.is_correct for a in attempts),
        "incorrect": sum(not a.is_correct for a in attempts),
        "accuracy": accuracy(attempts),
        "first_accuracy": accuracy(first_in_period),
        "answered_unique": sum(key in active_keys for key in latest),
        "available_questions": len(questions),
        "pending_errors": len(pending_keys),
        "today_attempts": sum(timezone.localdate(a.created_at) == now for a in all_attempts),
        "daily_minutes": profile.daily_minutes,
        "topics": topic_rows,
        "daily": [{"date": date, "attempts": len(items), "accuracy": accuracy(items)} for date, items in sorted(daily.items())],
        "recommendation": {
            "topic_slug": recommendation["slug"],
            "topic_name": recommendation["name"],
            "mode": "errors" if recommendation["pending_errors"] else "unseen" if recommendation["answered"] < recommendation["available"] else "all",
            "reason": "Retome os erros deste tema e releia os artigos indicados." if recommendation["pending_errors"] else "Avance na cobertura deste tema, conferindo cada comentário.",
        } if recommendation else None,
    }
