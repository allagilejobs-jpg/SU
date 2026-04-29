import base64
import pytest
import responses
from pinterest_publish.api import PinterestClient, RateLimitError, PinterestApiError

BASE = "https://api.pinterest.com/v5"

@responses.activate
def test_list_boards_paginates():
    responses.add(
        method=responses.GET,
        url=f"{BASE}/boards",
        json={"items": [{"id": "b1", "name": "Board1"}], "bookmark": "abc"},
        status=200,
    )
    responses.add(
        method=responses.GET,
        url=f"{BASE}/boards",
        json={"items": [{"id": "b2", "name": "Board2"}], "bookmark": None},
        status=200,
    )
    client = PinterestClient(access_token="t", api_base=BASE)
    boards = client.list_boards()
    assert [b["id"] for b in boards] == ["b1", "b2"]

@responses.activate
def test_list_boards_stops_when_bookmark_key_absent():
    """Pagination should terminate when 'bookmark' is missing entirely (not just None)."""
    responses.add(
        method=responses.GET,
        url=f"{BASE}/boards",
        json={"items": [{"id": "b1", "name": "Board1"}]},  # no 'bookmark' key at all
        status=200,
    )
    client = PinterestClient(access_token="t", api_base=BASE)
    boards = client.list_boards()
    assert [b["id"] for b in boards] == ["b1"]

@responses.activate
def test_create_pin_sends_base64():
    captured = {}
    def callback(req):
        import json
        captured["body"] = json.loads(req.body)
        return (201, {}, '{"id": "newpin"}')
    responses.add_callback(responses.POST, f"{BASE}/pins", callback=callback)

    client = PinterestClient(access_token="t", api_base=BASE)
    img_bytes = b"\x89PNG\r\n\x1a\nfake"
    pin = client.create_pin(
        title="T",
        description="D",
        link="https://example.com/",
        board_id="b1",
        section_id=None,
        image_bytes=img_bytes,
    )
    assert pin["id"] == "newpin"
    assert captured["body"]["title"] == "T"
    assert captured["body"]["board_id"] == "b1"
    assert captured["body"]["media_source"]["source_type"] == "image_base64"
    assert (
        captured["body"]["media_source"]["data"]
        == base64.b64encode(img_bytes).decode("ascii")
    )

@responses.activate
def test_delete_pin():
    responses.add(method=responses.DELETE, url=f"{BASE}/pins/abc", status=204)
    client = PinterestClient(access_token="t", api_base=BASE)
    client.delete_pin("abc")  # should not raise

@responses.activate
def test_429_raises_rate_limit_error():
    responses.add(
        method=responses.GET,
        url=f"{BASE}/boards",
        json={"message": "rate limit"},
        status=429,
        headers={"Retry-After": "30"},
    )
    client = PinterestClient(access_token="t", api_base=BASE)
    with pytest.raises(RateLimitError) as exc:
        client.list_boards()
    assert exc.value.retry_after == 30

@responses.activate
def test_other_error_raises_api_error():
    responses.add(
        method=responses.GET,
        url=f"{BASE}/boards",
        json={"message": "bad"},
        status=400,
    )
    client = PinterestClient(access_token="t", api_base=BASE)
    with pytest.raises(PinterestApiError, match="400"):
        client.list_boards()
