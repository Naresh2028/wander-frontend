from pathlib import Path

from conftest import StubSDK, make_destinations
from wander.pipeline import run_first_slice
from wander.schemas import TripBrief


def test_first_slice_end_to_end(make_client, tmp_path):
    client, sdk, ledger = make_client()
    brief = TripBrief(vibe="quiet <script>alert(1)</script> water", days=4)
    index = run_first_slice(client, brief, state_dir=tmp_path / "state", out_root=tmp_path / "out", n=4, draft=True)

    page = index.read_text(encoding="utf-8")
    assert index.name == "index.html"
    assert "<script>alert(1)</script>" not in page  # user text and model text are escaped
    assert "&lt;script&gt;" in page
    assert "Place 0 &lt;b&gt;" in page  # model-provided names are escaped too
    assert page.count("<article>") == 4

    images = list(Path(index.parent / "postcards").glob("*.webp"))
    assert len(images) == 4
    # 1 style anchor + 4 postcards, at $0.01 each, plus one Spark call
    assert len(sdk.calls["responses"]) == 5
    assert 0.05 < ledger.total < 0.07


def test_second_run_is_nearly_free_thanks_to_cache(make_client, tmp_path):
    client, sdk, ledger = make_client()
    brief = TripBrief(vibe="same vibe")
    run_first_slice(client, brief, state_dir=tmp_path / "state", out_root=tmp_path / "out", draft=True)
    spent = ledger.total
    run_first_slice(client, brief, state_dir=tmp_path / "state", out_root=tmp_path / "out2", draft=True)
    assert ledger.total == spent
