"""Run this FIRST. It makes 1 text call and 2 image calls (about $0.03 in total) and tells you
exactly which part of the Meta Model API setup works, before you build anything on top of it.

    python scripts/smoke_test.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pydantic import BaseModel  # noqa: E402

from wander.cache import DiskCache  # noqa: E402
from wander.client import MetaClient  # noqa: E402
from wander.config import Settings  # noqa: E402
from wander.ledger import Ledger  # noqa: E402


class Ping(BaseModel):
    ok: bool
    note: str


def main() -> int:
    s = Settings.from_env()
    ledger = Ledger(s.state_dir / "ledger.jsonl", s.budget_usd)
    client = MetaClient(s, ledger, DiskCache(s.state_dir / "cache"))
    out = s.state_dir / "smoke"
    out.mkdir(parents=True, exist_ok=True)
    failures = 0

    print(f"Key loaded. Cap ${s.budget_usd:.2f}, spent so far ${ledger.total:.3f}\n")

    try:
        r = client.chat_json("Reply as JSON only.", "Set ok=true and write a six-word note about travel.", Ping)
        print(f"[1/3] Muse Spark structured output OK -> {r.model_dump()}")
    except Exception as exc:  # noqa: BLE001
        failures += 1
        print(f"[1/3] Muse Spark FAILED: {type(exc).__name__}: {exc}")

    prompt = "A small hand-painted gouache postcard of a lighthouse at dusk. No text."
    for i, (label, controls) in enumerate([("plain call", False), ("with tool controls", True)], start=2):
        try:
            data = client.generate_image(prompt + f" Variant {i}.", tool_controls=controls, size="1536x1024", draft=True)
            path = out / f"smoke_{i}.webp"
            path.write_bytes(data)
            print(f"[{i}/3] Muse Image {label} OK -> {path} ({len(data) // 1024} KB)")
        except Exception as exc:  # noqa: BLE001
            failures += 1
            print(f"[{i}/3] Muse Image {label} FAILED: {type(exc).__name__}: {exc}")
            if controls:
                print("      Tip: set WANDER_IMAGE_TOOL_CONTROLS=0 in .env to skip the tool block.")

    print(f"\nSpend this session: {ledger.summary()}")
    print("All good." if not failures else f"{failures} check(s) failed. Fix those before moving on.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
