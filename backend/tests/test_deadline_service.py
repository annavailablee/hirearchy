from datetime import datetime, timedelta, timezone

from app.services.deadline_service import (
    compute_priority,
    priority_rank,
    within_attention_window,
)

NOW = datetime(2026, 6, 1, 12, 0, tzinfo=timezone.utc)


def test_completed():
    assert compute_priority(NOW - timedelta(days=1), NOW, now=NOW) == "COMPLETED"


def test_overdue():
    assert compute_priority(NOW - timedelta(hours=1), None, now=NOW) == "OVERDUE"


def test_urgent_within_24h():
    assert compute_priority(NOW + timedelta(hours=8), None, now=NOW) == "URGENT"
    assert compute_priority(NOW + timedelta(hours=23), None, now=NOW) == "URGENT"


def test_high_within_72h():
    assert compute_priority(NOW + timedelta(hours=48), None, now=NOW) == "HIGH"
    assert compute_priority(NOW + timedelta(hours=71), None, now=NOW) == "HIGH"


def test_normal_within_week():
    assert compute_priority(NOW + timedelta(days=5), None, now=NOW) == "NORMAL"


def test_later_beyond_week():
    assert compute_priority(NOW + timedelta(days=14), None, now=NOW) == "LATER"


def test_priority_rank_orders_correctly():
    ranks = [priority_rank(p) for p in ["OVERDUE", "URGENT", "HIGH", "NORMAL", "LATER", "COMPLETED"]]
    assert ranks == sorted(ranks)


def test_attention_window_includes_overdue():
    assert within_attention_window(NOW - timedelta(days=3), None, now=NOW) is True


def test_attention_window_includes_soon():
    assert within_attention_window(NOW + timedelta(days=3), None, now=NOW) is True


def test_attention_window_excludes_far():
    assert within_attention_window(NOW + timedelta(days=30), None, now=NOW) is False


def test_attention_window_excludes_completed():
    assert within_attention_window(NOW, NOW, now=NOW) is False