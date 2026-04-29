"""OAuth token storage, refresh, and (in Task 6) interactive browser flow."""
from __future__ import annotations
import base64
import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

import requests


class AuthError(Exception):
    """Raised when auth state is missing or refresh fails."""


@dataclass
class Token:
    access_token: str
    refresh_token: str
    expires_at: float  # unix seconds

    def is_expired(self, skew_seconds: int = 60) -> bool:
        return time.time() + skew_seconds >= self.expires_at


class TokenStore:
    def __init__(self, path: Path):
        self.path = path

    def save(self, token: Token) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(asdict(token), indent=2))

    def load(self) -> Optional[Token]:
        if not self.path.exists():
            return None
        data = json.loads(self.path.read_text())
        return Token(**data)


def load_or_refresh(
    store: TokenStore,
    client_id: str,
    client_secret: str,
    api_base: str,
) -> Token:
    """Return a valid access token, refreshing if necessary. Raise if no token saved."""
    tok = store.load()
    if tok is None:
        raise AuthError(
            "no saved token — run `python -m pinterest_publish auth` first"
        )
    if not tok.is_expired():
        return tok

    new_tok = _refresh_access_token(
        refresh_token=tok.refresh_token,
        client_id=client_id,
        client_secret=client_secret,
        api_base=api_base,
    )
    store.save(new_tok)
    return new_tok


def _refresh_access_token(
    refresh_token: str,
    client_id: str,
    client_secret: str,
    api_base: str,
) -> Token:
    basic = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    headers = {
        "Authorization": f"Basic {basic}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"grant_type": "refresh_token", "refresh_token": refresh_token}
    resp = requests.post(f"{api_base}/oauth/token", headers=headers, data=data)
    if resp.status_code >= 400:
        raise AuthError(f"refresh failed: {resp.status_code} {resp.text[:200]}")
    body = resp.json()
    return Token(
        access_token=body["access_token"],
        refresh_token=body.get("refresh_token", refresh_token),
        expires_at=time.time() + int(body.get("expires_in", 2592000)),
    )
