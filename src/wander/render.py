"""Renders the postcards into a static, self-contained HTML sheet (images referenced by relative path)."""

from __future__ import annotations

import html
import os
from pathlib import Path
from typing import Mapping, Sequence

from .schemas import Destination, TripBrief

_CSS = """
:root{--paper:#f4ecdc;--ink:#2b2118;--muted:#7a6a58;--accent:#b5532f}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.5 Georgia,serif}
header{padding:40px 24px 8px;max-width:1100px;margin:auto}
h1{font-size:2.2rem;margin:0 0 4px;letter-spacing:.02em}
.vibe{color:var(--muted);font-style:italic;margin:0}
main{max-width:1100px;margin:auto;padding:16px 24px 48px;display:grid;gap:28px;
grid-template-columns:repeat(auto-fit,minmax(420px,1fr))}
article{background:#fffaf0;border:1px solid #e4d6bb;border-radius:6px;overflow:hidden;
box-shadow:0 6px 18px rgba(60,40,10,.12)}
article img{display:block;width:100%;height:auto}
.body{padding:16px 20px 20px}
h2{margin:0;font-size:1.4rem}.country{color:var(--muted);font-size:.95rem}
.tag{color:var(--accent);margin:6px 0 10px;font-style:italic}
ul{margin:8px 0;padding-left:20px}.meta{color:var(--muted);font-size:.9rem;margin-top:10px}
footer{max-width:1100px;margin:auto;padding:0 24px 40px;color:var(--muted);font-size:.85rem}
@media(max-width:520px){main{grid-template-columns:1fr}}
"""


def _e(s: object) -> str:
    return html.escape(str(s), quote=True)


def render_contact_sheet(
    brief: TripBrief,
    destinations: Sequence[Destination],
    postcards: Mapping[str, Path],
    run_dir: Path,
) -> Path:
    run_dir.mkdir(parents=True, exist_ok=True)
    cards = []
    for d in destinations:
        img = postcards.get(d.name)
        rel = os.path.relpath(img, run_dir) if img else ""
        items = "".join(f"<li>{_e(h)}</li>" for h in d.highlights)
        cards.append(
            f"""<article>
{f'<img src="{_e(rel)}" alt="Postcard of {_e(d.name)}">' if img else ''}
<div class="body"><h2>{_e(d.name)}</h2><div class="country">{_e(d.country)}</div>
<div class="tag">{_e(d.tagline)}</div><p>{_e(d.why_it_fits)}</p><ul>{items}</ul>
<div class="meta">Best months: {_e(d.best_months)} &middot; roughly ${_e(d.daily_budget_usd_low)}&ndash;${_e(d.daily_budget_usd_high)} per day
&middot; {_e(', '.join(d.mood_tags))}</div></div></article>"""
        )
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Wander</title><style>{_CSS}</style></head>
<body><header><h1>Wander</h1><p class="vibe">&ldquo;{_e(brief.vibe)}&rdquo; &mdash; {_e(brief.days)} days, {_e(brief.budget)}</p></header>
<main>{''.join(cards)}</main>
<footer>Destinations and budget ranges are AI suggestions. Verify prices, seasons and entry rules before booking.</footer>
</body></html>"""
    out = run_dir / "index.html"
    out.write_text(page, encoding="utf-8")
    return out
