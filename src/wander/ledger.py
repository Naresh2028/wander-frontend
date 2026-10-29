"""Local spend ledger with a hard cap. Every paid call is checked before and recorded after."""

from __future__ import annotations

import json
import threading
import time
from collections import defaultdict
from pathlib import Path


class BudgetExceeded(RuntimeError):
    """Raised before a call that would push local spend over the cap."""


class Ledger:
    """Append-only JSONL ledger. Survives restarts so the cap covers the whole week.

    This is an *estimate* built from documented prices and API usage fields. The Billing
    page on dev.meta.ai remains the source of truth.
    """

    def __init__(self, path: str | Path, cap_usd: float) -> None:
        self.path = Path(path)
        self.cap_usd = float(cap_usd)
        self._lock = threading.Lock()
        self._total = 0.0
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.is_file():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    self._total += float(json.loads(line).get("usd", 0.0))

    @property
    def total(self) -> float:
        return self._total

    @property
    def remaining(self) -> float:
        return max(0.0, self.cap_usd - self._total)

    def check(self, estimate_usd: float, label: str = "call") -> None:
        """Raise BudgetExceeded if spending `estimate_usd` more would pass the cap."""
        with self._lock:
            if self._total + estimate_usd > self.cap_usd:
                raise BudgetExceeded(
                    f"Refusing {label}: ${self._total:.3f} spent + ${estimate_usd:.3f} "
                    f"estimated would exceed the ${self.cap_usd:.2f} cap."
                )

    def record(self, kind: str, model: str, usd: float, detail: str = "") -> None:
        entry = {"ts": round(time.time(), 1), "kind": kind, "model": model, "usd": round(usd, 6), "detail": detail}
        with self._lock:
            self._total += usd
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")

    def summary(self) -> dict[str, float]:
        """Spend per kind (text / image / sam / voice) plus the grand total."""
        by_kind: dict[str, float] = defaultdict(float)
        if self.path.is_file():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    e = json.loads(line)
                    by_kind[e["kind"]] += float(e["usd"])
        out = {k: round(v, 4) for k, v in by_kind.items()}
        out["total"] = round(self._total, 4)
        out["cap"] = self.cap_usd
        return out
