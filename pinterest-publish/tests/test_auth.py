import json
import time
from pathlib import Path
import pytest
import responses
from pinterest_publish.auth import (
    TokenStore,
    Token,
    load_or_refresh,
    AuthError,
)

BASE = "https://api.pinterest.com/v5"

def test_save_and_load_roundtrip(tmp_path):
    store = TokenStore(tmp_path / "tok.json")
    tok = Token(
        access_token="A",
        refresh_token="R",
        expires_at=time.time() + 1000,
    )
    store.save(tok)
    loaded = store.load()
    assert loaded.access_token == "A"
    assert loaded.refresh_token == "R"

def test_load_missing_file_returns_none(tmp_path):
    store = TokenStore(tmp_path / "nope.json")
    assert store.load() is None

def test_token_is_expired_when_in_past():
    tok = Token(access_token="A", refresh_token="R", expires_at=time.time() - 10)
    assert tok.is_expired()

def test_token_not_expired_when_future():
    tok = Token(access_token="A", refresh_token="R", expires_at=time.time() + 1000)
    assert not tok.is_expired()

@responses.activate
def test_load_or_refresh_refreshes_when_expired(tmp_path):
    store = TokenStore(tmp_path / "tok.json")
    expired = Token(access_token="OLD", refresh_token="R1", expires_at=time.time() - 10)
    store.save(expired)

    responses.add(
        method=responses.POST,
        url="https://api.pinterest.com/v5/oauth/token",
        json={
            "access_token": "NEW",
            "refresh_token": "R2",
            "expires_in": 2592000,
        },
        status=200,
    )

    refreshed = load_or_refresh(
        store=store,
        client_id="cid",
        client_secret="csec",
        api_base=BASE,
    )
    assert refreshed.access_token == "NEW"
    saved = store.load()
    assert saved.access_token == "NEW"

@responses.activate
def test_load_or_refresh_returns_existing_when_fresh(tmp_path):
    store = TokenStore(tmp_path / "tok.json")
    fresh = Token(access_token="FRESH", refresh_token="R", expires_at=time.time() + 1000)
    store.save(fresh)
    # Don't add a responses mock — refresh should NOT be called
    result = load_or_refresh(
        store=store,
        client_id="cid",
        client_secret="csec",
        api_base=BASE,
    )
    assert result.access_token == "FRESH"

def test_load_or_refresh_no_token_raises(tmp_path):
    store = TokenStore(tmp_path / "nope.json")
    with pytest.raises(AuthError, match="auth"):
        load_or_refresh(
            store=store,
            client_id="cid",
            client_secret="csec",
            api_base=BASE,
        )
