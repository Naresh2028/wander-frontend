import pytest

from conftest import PNG_1PX, StubSDK
from wander.client import ImageGenerationError
from wander.ledger import BudgetExceeded
from wander.schemas import DestinationSet


def test_chat_json_parses_costs_and_caches(make_client):
    client, sdk, ledger = make_client()
    r1 = client.chat_json("sys", "user", DestinationSet)
    assert len(r1.destinations) == 4
    expected = 1000 * 1.25 / 1e6 + 500 * 4.25 / 1e6
    assert ledger.total == pytest.approx(expected)

    client.chat_json("sys", "user", DestinationSet)  # identical request -> cache hit
    assert len(sdk.calls["chat"]) == 1
    assert ledger.total == pytest.approx(expected)

    sent = sdk.calls["chat"][0]
    assert sent["model"] == "muse-spark-1.3"
    assert sent["response_format"]["type"] == "json_schema"
    assert sent["response_format"]["json_schema"]["name"] == "DestinationSet"


def test_image_decodes_by_type_and_charges_flat_price(make_client):
    client, sdk, ledger = make_client()
    data = client.generate_image("a lighthouse", draft=True, size="1536x1024")
    assert data == PNG_1PX
    assert ledger.total == pytest.approx(0.01)

    sent = sdk.calls["responses"][0]
    assert sent["model"] == "muse-image-1.0"
    tool = sent["tools"][0]
    assert tool["type"] == "image_generation" and tool["reasoning_strength"] == "low" and tool["size"] == "1536x1024"

    client.generate_image("a lighthouse", draft=True, size="1536x1024")  # cached
    assert len(sdk.calls["responses"]) == 1 and ledger.total == pytest.approx(0.01)


def test_final_quality_uses_high_reasoning(make_client):
    client, sdk, _ = make_client()
    client.generate_image("x", draft=False)
    assert sdk.calls["responses"][0]["tools"][0]["reasoning_strength"] == "high"


def test_tool_controls_can_be_disabled(make_client):
    client, sdk, _ = make_client()
    client.generate_image("x", tool_controls=False)
    assert "tools" not in sdk.calls["responses"][0]


def test_reference_image_is_sent_as_input_image(make_client, tmp_path):
    client, sdk, _ = make_client()
    ref = tmp_path / "ref.png"
    ref.write_bytes(PNG_1PX)
    client.generate_image("paint it", references=[ref])
    content = sdk.calls["responses"][0]["input"][0]["content"]
    assert content[0] == {"type": "input_text", "text": "paint it"}
    assert content[1]["type"] == "input_image" and content[1]["image_url"].startswith("data:image/png;base64,")


def test_missing_image_raises_clear_error_and_costs_nothing(make_client):
    client, _, ledger = make_client(StubSDK(image_ok=False))
    with pytest.raises(ImageGenerationError):
        client.generate_image("blocked prompt")
    assert ledger.total == 0


def test_budget_cap_blocks_calls_before_they_happen(make_client):
    client, sdk, _ = make_client(cap=0.005)
    with pytest.raises(BudgetExceeded):
        client.generate_image("too expensive")
    assert sdk.calls["responses"] == []
