"""Thin Pinterest v5 REST API wrapper."""
from __future__ import annotations
import base64
from typing import Iterator, List, Optional, Dict, Any

import requests


class PinterestApiError(Exception):
    """Generic Pinterest API failure."""


class RateLimitError(PinterestApiError):
    """HTTP 429. Caller should back off (or pause for retry_after seconds)."""

    def __init__(self, retry_after: int, message: str = "rate limited"):
        super().__init__(message)
        self.retry_after = retry_after


class PinterestClient:
    def __init__(self, access_token: str, api_base: str):
        self.access_token = access_token
        self.api_base = api_base.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {access_token}",
        })

    # ---------- helpers ----------

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = f"{self.api_base}{path}"
        resp = self._session.request(method, url, **kwargs)
        if resp.status_code == 429:
            retry_after = int(resp.headers.get("Retry-After", "60"))
            raise RateLimitError(retry_after=retry_after)
        if resp.status_code >= 400:
            raise PinterestApiError(
                f"{method} {path} -> {resp.status_code}: {resp.text[:300]}"
            )
        return resp

    def _paginate(self, path: str, params: Optional[Dict[str, Any]] = None) -> Iterator[dict]:
        params = dict(params or {})
        while True:
            resp = self._request("GET", path, params=params)
            data = resp.json()
            for item in data.get("items", []):
                yield item
            bookmark = data.get("bookmark")
            if bookmark is None:
                return
            params["bookmark"] = bookmark

    # ---------- boards ----------

    def list_boards(self) -> List[dict]:
        return list(self._paginate("/boards", {"page_size": 100}))

    def list_board_sections(self, board_id: str) -> List[dict]:
        return list(self._paginate(f"/boards/{board_id}/sections", {"page_size": 100}))

    def create_board(self, name: str, description: str = "", privacy: str = "PUBLIC") -> dict:
        body = {"name": name, "description": description, "privacy": privacy}
        return self._request("POST", "/boards", json=body).json()

    def create_board_section(self, board_id: str, name: str) -> dict:
        return self._request(
            "POST", f"/boards/{board_id}/sections", json={"name": name}
        ).json()

    # ---------- pins ----------

    def list_pins(self) -> List[dict]:
        return list(self._paginate("/pins", {"page_size": 100}))

    def create_pin(
        self,
        title: str,
        description: str,
        link: str,
        board_id: str,
        section_id: Optional[str],
        image_bytes: bytes,
    ) -> dict:
        body = {
            "title": title,
            "description": description,
            "link": link,
            "board_id": board_id,
            "media_source": {
                "source_type": "image_base64",
                "content_type": "image/png",
                "data": base64.b64encode(image_bytes).decode("ascii"),
            },
        }
        if section_id is not None:
            body["board_section_id"] = section_id
        return self._request("POST", "/pins", json=body).json()

    def delete_pin(self, pin_id: str) -> None:
        self._request("DELETE", f"/pins/{pin_id}")
