"""First vertical slice: vague vibe -> 4 destination postcards in one art style -> index.html

    python scripts/first_slice.py --vibe "I want to feel small near something enormous, and eat well"
    python scripts/first_slice.py --vibe "..." --final     # high-effort images for demo material
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from wander.cache import DiskCache  # noqa: E402
from wander.client import MetaClient  # noqa: E402
from wander.config import Settings  # noqa: E402
from wander.ledger import BudgetExceeded, Ledger  # noqa: E402
from wander.pipeline import run_first_slice  # noqa: E402
from wander.schemas import TripBrief  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--vibe", required=True, help="Free-text mood, however vague.")
    ap.add_argument("--days", type=int, default=5)
    ap.add_argument("--budget", choices=["shoestring", "comfortable", "splurge"], default="comfortable")
    ap.add_argument("--from", dest="origin", default=None, help="Where you travel from (optional).")
    ap.add_argument("--avoid", action="append", default=[], help="Repeatable, e.g. --avoid crowds")
    ap.add_argument("-n", type=int, default=4, help="Number of destinations (default 4).")
    ap.add_argument("--final", action="store_true", help="High-effort images (same price, slower).")
    ap.add_argument("--out", default="out")
    args = ap.parse_args()

    s = Settings.from_env()
    ledger = Ledger(s.state_dir / "ledger.jsonl", s.budget_usd)
    client = MetaClient(s, ledger, DiskCache(s.state_dir / "cache"))
    brief = TripBrief(vibe=args.vibe, days=args.days, budget=args.budget, travelling_from=args.origin, avoid=args.avoid)

    try:
        index = run_first_slice(client, brief, state_dir=s.state_dir, out_root=Path(args.out), n=args.n, draft=not args.final)
    except BudgetExceeded as exc:
        print(f"Stopped by the spend cap: {exc}")
        return 2

    print(f"\nDone. Open {index}")
    print(f"Spend: {ledger.summary()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
