import pytest

from wander.cache import DiskCache
from wander.ledger import BudgetExceeded, Ledger


def test_ledger_persists_across_instances_and_enforces_cap(tmp_path):
    path = tmp_path / "ledger.jsonl"
    a = Ledger(path, cap_usd=1.00)
    a.record("image", "muse-image-1.0", 0.40)
    a.record("text", "muse-spark-1.3", 0.35)

    b = Ledger(path, cap_usd=1.00)  # a restart must not reset the budget
    assert b.total == pytest.approx(0.75)
    b.check(0.25)  # exactly at the cap is allowed
    with pytest.raises(BudgetExceeded):
        b.check(0.26)
    assert b.summary() == {"image": 0.4, "text": 0.35, "total": 0.75, "cap": 1.0}


def test_cache_key_is_stable_and_sensitive(tmp_path):
    k1 = DiskCache.key("a", {"x": 1, "y": 2})
    assert k1 == DiskCache.key("a", {"y": 2, "x": 1})
    assert k1 != DiskCache.key("a", {"x": 1, "y": 3})


def test_cache_roundtrip(tmp_path):
    c = DiskCache(tmp_path)
    assert c.get_bytes("img", "k", "webp") is None
    c.put_bytes("img", "k", "webp", b"abc")
    assert c.get_bytes("img", "k", "webp") == b"abc"
    c.put_text("chat", "k", "{}")
    assert c.get_text("chat", "k") == "{}"
