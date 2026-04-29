"""OAuth token storage, refresh, and (in Task 6) interactive browser flow."""
from __future__ import annotations
import base64
import json
import os
import secrets
import threading
import time
import urllib.parse
import webbrowser
from dataclasses import dataclass, asdict
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import List, Optional

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
        text = json.dumps(asdict(token), indent=2)
        # 0o600 is enforced on POSIX; Windows treats it as a no-op but the
        # token file is gitignored either way (state/ is in .gitignore).
        fd = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        try:
            os.write(fd, text.encode("utf-8"))
        finally:
            os.close(fd)

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
    resp = requests.post(f"{api_base}/oauth/token", headers=headers, data=data, timeout=30)
    if resp.status_code >= 400:
        raise AuthError(f"refresh failed: {resp.status_code} {resp.text[:200]}")
    body = resp.json()
    return Token(
        access_token=body["access_token"],
        refresh_token=body.get("refresh_token", refresh_token),
        expires_at=time.time() + int(body.get("expires_in", 2592000)),
    )


def run_interactive_oauth(
    client_id: str,
    client_secret: str,
    api_base: str,
    redirect_uri: str,
    callback_port: int,
    scopes: List[str],
    authorize_url: str,
) -> Token:
    """Spawn a local server, open the browser to Pinterest, capture code, exchange for tokens."""
    state = secrets.token_urlsafe(16)
    captured: dict = {}

    class _Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path != "/callback":
                self.send_response(404)
                self.end_headers()
                return
            qs = urllib.parse.parse_qs(parsed.query)
            captured["code"] = (qs.get("code") or [None])[0]
            captured["state"] = (qs.get("state") or [None])[0]
            captured["error"] = (qs.get("error") or [None])[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"<html><body><h2>Pinterest auth complete.</h2>"
                b"<p>You may close this tab.</p></body></html>"
            )

        def log_message(self, *args, **kwargs):
            pass  # silence default access log

    server = HTTPServer(("localhost", callback_port), _Handler)
    server.timeout = 1  # seconds; handle_request returns after this if idle

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": ",".join(scopes),
        "state": state,
    }
    url = f"{authorize_url}?{urllib.parse.urlencode(params)}"
    print(f"Opening browser to:\n  {url}\n")
    webbrowser.open(url)
    print(f"Listening on {redirect_uri} ...")

    # Single-threaded handle_request loop — avoids shutdown() deadlock on Windows.
    # Loop until callback fires or 5-minute deadline.
    try:
        deadline = time.time() + 300
        while time.time() < deadline:
            if "code" in captured or "error" in captured:
                break
            server.handle_request()
    finally:
        server.server_close()

    if captured.get("error"):
        raise AuthError(f"authorization denied: {captured['error']}")
    if not captured.get("code"):
        raise AuthError("timed out waiting for OAuth callback")
    if captured.get("state") != state:
        raise AuthError("OAuth state mismatch — possible CSRF")

    return _exchange_code_for_token(
        code=captured["code"],
        client_id=client_id,
        client_secret=client_secret,
        api_base=api_base,
        redirect_uri=redirect_uri,
    )


def _exchange_code_for_token(
    code: str,
    client_id: str,
    client_secret: str,
    api_base: str,
    redirect_uri: str,
) -> Token:
    basic = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    headers = {
        "Authorization": f"Basic {basic}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
    }
    resp = requests.post(f"{api_base}/oauth/token", headers=headers, data=data, timeout=30)
    if resp.status_code >= 400:
        raise AuthError(f"token exchange failed: {resp.status_code} {resp.text[:200]}")
    body = resp.json()
    return Token(
        access_token=body["access_token"],
        refresh_token=body["refresh_token"],
        expires_at=time.time() + int(body.get("expires_in", 2592000)),
    )
