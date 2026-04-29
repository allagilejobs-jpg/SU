"""Per-pin destination URL lookup with default fallback and title aliases."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import yaml


class UrlMapError(Exception):
    """Raised when url-map.yaml is missing required fields or invalid."""


@dataclass
class UrlMapper:
    default: str
    pins: Dict[str, str] = field(default_factory=dict)
    aliases: Dict[str, List[str]] = field(default_factory=dict)
    # Reverse lookup: alias title (lowercased+stripped) -> pin filename
    _alias_index: Dict[str, str] = field(default_factory=dict, repr=False)

    @classmethod
    def load(cls, path: Path) -> "UrlMapper":
        if not path.exists():
            raise UrlMapError(f"url-map.yaml not found at {path}")

        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        default = data.get("default")
        if not default:
            raise UrlMapError("url-map.yaml missing required `default` URL")
        if not _is_https_url(default):
            raise UrlMapError(f"default must be an https URL, got: {default!r}")

        pins = data.get("pins") or {}
        for fname, url in pins.items():
            if not _is_https_url(url):
                raise UrlMapError(f"pins[{fname}] must be https URL, got: {url!r}")

        aliases_raw = data.get("aliases") or {}
        aliases: Dict[str, List[str]] = {}
        alias_index: Dict[str, str] = {}
        for fname, titles in aliases_raw.items():
            if not isinstance(titles, list):
                raise UrlMapError(f"aliases[{fname}] must be a list of titles")
            aliases[fname] = list(titles)
            for title in titles:
                alias_index[_norm(title)] = fname

        return cls(
            default=default,
            pins=pins,
            aliases=aliases,
            _alias_index=alias_index,
        )

    def url_for(self, filename: str) -> str:
        return self.pins.get(filename, self.default)

    def filename_for_alias(self, title: str) -> Optional[str]:
        return self._alias_index.get(_norm(title))


def _is_https_url(s: str) -> bool:
    return isinstance(s, str) and s.startswith("https://")


def _norm(title: str) -> str:
    return title.strip().lower()
