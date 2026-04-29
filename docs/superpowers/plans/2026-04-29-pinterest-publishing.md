# Pinterest Publishing Pipeline — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python CLI (`auth → audit → plan → apply`) that publishes the 25 polished pins from `content/pinterest/` to the Spectrum Unlocked Pinterest account via the Pinterest v5 API, replacing existing old-palette pins with new-palette versions.

**Architecture:** A 4-stage CLI where each stage writes reviewable artifacts to `pinterest-publish/state/` and is independently re-runnable. Source data parsed from `content/pinterest/PINTEREST-POSTS.md` plus a new `pinterest-publish/url-map.yaml` for per-pin destination URLs. OAuth 2.0 flow stores tokens locally; rate-limited apply stage uses an append-only log to resume across days.

**Tech Stack:** Python 3.10+, `requests` (HTTP), `pyyaml` (config), `pillow` (image dimension validation), `pytest` (testing). Pinterest v5 REST API (`https://api.pinterest.com/v5/`).

**Reference spec:** `docs/superpowers/specs/2026-04-29-pinterest-publishing-design.md`

---

## File structure

```
pinterest-publish/
├── README.md                       # operator docs (Task 12)
├── url-map.yaml                    # pin → destination URL (Task 11)
├── pyproject.toml                  # deps + entry point (Task 1)
├── pinterest_publish/
│   ├── __init__.py                 # (Task 1)
│   ├── __main__.py                 # python -m pinterest_publish entry (Task 1)
│   ├── config.py                   # constants: paths, API base, scopes (Task 1)
│   ├── parser.py                   # PINTEREST-POSTS.md → records (Task 2)
│   ├── url_mapper.py               # url-map.yaml lookup (Task 3)
│   ├── api.py                      # Pinterest REST wrapper (Task 4)
│   ├── auth.py                     # OAuth flow + token refresh (Task 5, 6)
│   ├── audit.py                    # GET boards/pins → reports (Task 7)
│   ├── plan.py                     # cross-reference → plan (Task 8)
│   ├── apply.py                    # execute plan + log + resume (Task 9)
│   └── cli.py                      # argparse entry, wires stages (Task 10)
├── state/                          # gitignored, runtime artifacts
└── tests/
    ├── __init__.py
    ├── test_parser.py              # (Task 2)
    ├── test_url_mapper.py          # (Task 3)
    ├── test_api.py                 # (Task 4)
    ├── test_auth.py                # (Task 5)
    ├── test_audit.py               # (Task 7)
    ├── test_plan.py                # (Task 8)
    ├── test_apply.py               # (Task 9)
    └── fixtures/
        ├── sample-PINTEREST-POSTS.md  # (Task 2)
        ├── sample-pin.png              # (Task 2, 1000x1500 PNG)
        └── sample-audit.json           # (Task 8)
```

`.gitignore` updates (Task 1) — add to repo's existing `.gitignore`:
```
pinterest-publish/state/
pinterest-publish/.env
```

---

## Task 1: Scaffold project

**Files:**
- Create: `pinterest-publish/pyproject.toml`
- Create: `pinterest-publish/pinterest_publish/__init__.py`
- Create: `pinterest-publish/pinterest_publish/__main__.py`
- Create: `pinterest-publish/pinterest_publish/config.py`
- Create: `pinterest-publish/tests/__init__.py`
- Modify: `.gitignore` (append two lines)

- [ ] **Step 1: Create `pyproject.toml`**

```toml
[project]
name = "pinterest-publish"
version = "0.1.0"
description = "Publish Spectrum Unlocked pins to Pinterest via v5 API"
requires-python = ">=3.10"
dependencies = [
    "requests>=2.31",
    "pyyaml>=6.0",
    "pillow>=10.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4",
    "pytest-mock>=3.12",
    "responses>=0.24",
]

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["."]
include = ["pinterest_publish*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Create empty `__init__.py` files**

`pinterest-publish/pinterest_publish/__init__.py`:
```python
"""Pinterest publishing pipeline for Spectrum Unlocked."""
__version__ = "0.1.0"
```

`pinterest-publish/tests/__init__.py`: (empty file — touch it)

- [ ] **Step 3: Create `__main__.py` so `python -m pinterest_publish` works**

`pinterest-publish/pinterest_publish/__main__.py`:
```python
from pinterest_publish.cli import main

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Create `config.py`**

`pinterest-publish/pinterest_publish/config.py`:
```python
"""Constants and paths for the Pinterest publishing pipeline."""
from pathlib import Path

# Repo paths
REPO_ROOT = Path(__file__).resolve().parents[2]
PINTEREST_SOURCE_DIR = REPO_ROOT / "content" / "pinterest"
PINTEREST_POSTS_MD = PINTEREST_SOURCE_DIR / "PINTEREST-POSTS.md"

# Tool paths
TOOL_ROOT = REPO_ROOT / "pinterest-publish"
URL_MAP_PATH = TOOL_ROOT / "url-map.yaml"
STATE_DIR = TOOL_ROOT / "state"
TOKEN_PATH = STATE_DIR / ".pinterest-token.json"
AUDIT_REPORT_JSON = STATE_DIR / "audit-report.json"
AUDIT_REPORT_MD = STATE_DIR / "audit-report.md"
PUBLISH_PLAN_JSON = STATE_DIR / "publish-plan.json"
PUBLISH_PLAN_MD = STATE_DIR / "publish-plan.md"
APPLY_LOG = STATE_DIR / "apply-log.jsonl"

# Pinterest API
API_BASE_PRODUCTION = "https://api.pinterest.com/v5"
API_BASE_SANDBOX = "https://api-sandbox.pinterest.com/v5"
OAUTH_AUTHORIZE_URL = "https://www.pinterest.com/oauth/"
OAUTH_REDIRECT_URI = "http://localhost:8080/callback"
OAUTH_CALLBACK_PORT = 8080

# Required scopes — write scopes only requested when needed
SCOPES_READ_ONLY = ["pins:read", "boards:read"]
SCOPES_PUBLISH = ["pins:read", "pins:write", "boards:read"]
SCOPES_PUBLISH_WITH_CREATE = ["pins:read", "pins:write", "boards:read", "boards:write"]

# Pinterest content limits
MAX_TITLE_LEN = 100
MAX_DESCRIPTION_LEN = 500
EXPECTED_IMAGE_SIZE = (1000, 1500)
```

- [ ] **Step 5: Append to repo `.gitignore`**

Append these two lines (use Edit tool):
```
pinterest-publish/state/
pinterest-publish/.env
```

- [ ] **Step 6: Install in editable mode**

```bash
cd pinterest-publish && pip install -e ".[dev]"
```

Expected: installs `pinterest-publish` in site-packages and `pytest`, `responses`, `pytest-mock` available.

- [ ] **Step 7: Verify package imports**

```bash
python -c "import pinterest_publish; print(pinterest_publish.__version__)"
```

Expected output: `0.1.0`

- [ ] **Step 8: Commit**

```bash
git add pinterest-publish/pyproject.toml pinterest-publish/pinterest_publish/ pinterest-publish/tests/__init__.py .gitignore
git commit -m "feat(pinterest-publish): scaffold package + config"
```

---

## Task 2: Parser — `PINTEREST-POSTS.md` → pin records

**Files:**
- Create: `pinterest-publish/tests/fixtures/sample-PINTEREST-POSTS.md`
- Create: `pinterest-publish/tests/fixtures/sample-pin.png` (1000×1500 PNG)
- Create: `pinterest-publish/tests/test_parser.py`
- Create: `pinterest-publish/pinterest_publish/parser.py`

- [ ] **Step 1: Create the test fixture markdown**

`pinterest-publish/tests/fixtures/sample-PINTEREST-POSTS.md`:
```markdown
# Sample Posts

## 1. IEP Accommodations
**File:** `sample-pin.png`

**Title:** Test IEP Accommodations Title

**Description:** This is a test description for IEP accommodations that fits within Pinterest's 500 char limit.

**Board:** Autism Parenting Tips / IEP & School Advocacy

---

## 2. Sleep Strategies
**File:** `sample-pin.png`

**Title:** Test Sleep Strategies Title

**Description:** This is a test description for sleep strategies.

**Board:** Autism Parenting Tips / Sleep

---
```

- [ ] **Step 2: Create the test PNG fixture**

```bash
cd pinterest-publish && python -c "from PIL import Image; Image.new('RGB', (1000, 1500), 'pink').save('tests/fixtures/sample-pin.png')"
```

Expected: file `tests/fixtures/sample-pin.png` exists, 1000×1500.

- [ ] **Step 3: Write failing tests for parser**

`pinterest-publish/tests/test_parser.py`:
```python
from pathlib import Path
import pytest
from pinterest_publish.parser import parse_pinterest_posts, PinRecord, ParseError

FIXTURES = Path(__file__).parent / "fixtures"
SAMPLE_MD = FIXTURES / "sample-PINTEREST-POSTS.md"

def test_parses_two_records():
    records = parse_pinterest_posts(SAMPLE_MD, image_dir=FIXTURES)
    assert len(records) == 2
    assert isinstance(records[0], PinRecord)

def test_record_fields_populated():
    records = parse_pinterest_posts(SAMPLE_MD, image_dir=FIXTURES)
    r = records[0]
    assert r.filename == "sample-pin.png"
    assert r.title == "Test IEP Accommodations Title"
    assert "IEP accommodations" in r.description
    assert r.board_path == "Autism Parenting Tips / IEP & School Advocacy"
    assert r.image_path == FIXTURES / "sample-pin.png"

def test_missing_image_fails_loud(tmp_path):
    md = tmp_path / "posts.md"
    md.write_text(
        "## 1. Test\n**File:** `nope.png`\n\n"
        "**Title:** T\n\n**Description:** D\n\n"
        "**Board:** B / S\n---\n"
    )
    with pytest.raises(ParseError, match="image not found"):
        parse_pinterest_posts(md, image_dir=tmp_path)

def test_title_too_long_fails(tmp_path):
    long_title = "x" * 101
    md = tmp_path / "posts.md"
    img = tmp_path / "p.png"
    from PIL import Image
    Image.new("RGB", (1000, 1500)).save(img)
    md.write_text(
        f"## 1. Test\n**File:** `p.png`\n\n"
        f"**Title:** {long_title}\n\n**Description:** D\n\n"
        f"**Board:** B / S\n---\n"
    )
    with pytest.raises(ParseError, match="title.*100"):
        parse_pinterest_posts(md, image_dir=tmp_path)

def test_wrong_image_dimensions_fails(tmp_path):
    md = tmp_path / "posts.md"
    img = tmp_path / "p.png"
    from PIL import Image
    Image.new("RGB", (500, 500)).save(img)
    md.write_text(
        "## 1. Test\n**File:** `p.png`\n\n"
        "**Title:** T\n\n**Description:** D\n\n"
        "**Board:** B / S\n---\n"
    )
    with pytest.raises(ParseError, match="dimensions"):
        parse_pinterest_posts(md, image_dir=tmp_path)
```

- [ ] **Step 4: Run tests to verify they fail**

```bash
cd pinterest-publish && pytest tests/test_parser.py -v
```

Expected: ImportError or 5 failures because `parser.py` doesn't exist yet.

- [ ] **Step 5: Implement parser**

`pinterest-publish/pinterest_publish/parser.py`:
```python
"""Parse content/pinterest/PINTEREST-POSTS.md into PinRecord objects."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import re
from typing import List, Optional

from PIL import Image

from .config import (
    MAX_TITLE_LEN,
    MAX_DESCRIPTION_LEN,
    EXPECTED_IMAGE_SIZE,
)


class ParseError(Exception):
    """Raised when PINTEREST-POSTS.md is malformed or pin metadata invalid."""


@dataclass(frozen=True)
class PinRecord:
    filename: str
    image_path: Path
    title: str
    description: str
    board_path: str   # e.g. "Autism Parenting Tips / IEP & School Advocacy"


# Section is delimited by `## N. <Topic>` and ends at next `## ` or EOF
_SECTION_RE = re.compile(r"^## \d+\. (.+?)$", re.MULTILINE)
_FILE_RE = re.compile(r"\*\*File:\*\*\s*`([^`]+)`")
_TITLE_RE = re.compile(r"\*\*Title:\*\*\s*(.+?)(?:\n|$)")
_DESC_RE = re.compile(r"\*\*Description:\*\*\s*(.+?)(?=\n\n)", re.DOTALL)
_BOARD_RE = re.compile(r"\*\*Board:\*\*\s*(.+?)(?:\n|$)")


def parse_pinterest_posts(md_path: Path, image_dir: Path) -> List[PinRecord]:
    if not md_path.exists():
        raise ParseError(f"PINTEREST-POSTS.md not found at {md_path}")

    text = md_path.read_text(encoding="utf-8")

    # Split on `## N. ` headers — keep the topic text but ignore it (we use Title field instead)
    starts = [(m.start(), m.group(1)) for m in _SECTION_RE.finditer(text)]
    if not starts:
        raise ParseError("no `## N. <Topic>` sections found")

    records: List[PinRecord] = []
    for i, (start, topic) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else len(text)
        section = text[start:end]
        records.append(_parse_section(section, topic, image_dir))
    return records


def _parse_section(section: str, topic: str, image_dir: Path) -> PinRecord:
    file_m = _FILE_RE.search(section)
    title_m = _TITLE_RE.search(section)
    desc_m = _DESC_RE.search(section)
    board_m = _BOARD_RE.search(section)

    if not file_m:
        raise ParseError(f"section '{topic}': missing File field")
    if not title_m:
        raise ParseError(f"section '{topic}': missing Title field")
    if not desc_m:
        raise ParseError(f"section '{topic}': missing Description field")
    if not board_m:
        raise ParseError(f"section '{topic}': missing Board field")

    filename = file_m.group(1).strip()
    title = title_m.group(1).strip()
    description = desc_m.group(1).strip()
    board_path = board_m.group(1).strip()

    image_path = image_dir / filename
    if not image_path.exists():
        raise ParseError(f"section '{topic}': image not found at {image_path}")

    if len(title) > MAX_TITLE_LEN:
        raise ParseError(
            f"section '{topic}': title exceeds {MAX_TITLE_LEN} chars (got {len(title)})"
        )
    if len(description) > MAX_DESCRIPTION_LEN:
        raise ParseError(
            f"section '{topic}': description exceeds {MAX_DESCRIPTION_LEN} chars (got {len(description)})"
        )

    with Image.open(image_path) as img:
        if img.size != EXPECTED_IMAGE_SIZE:
            raise ParseError(
                f"section '{topic}': image dimensions {img.size} != expected {EXPECTED_IMAGE_SIZE}"
            )

    return PinRecord(
        filename=filename,
        image_path=image_path,
        title=title,
        description=description,
        board_path=board_path,
    )
```

- [ ] **Step 6: Run tests to verify they pass**

```bash
cd pinterest-publish && pytest tests/test_parser.py -v
```

Expected: 5 PASS.

- [ ] **Step 7: Commit**

```bash
git add pinterest-publish/pinterest_publish/parser.py pinterest-publish/tests/test_parser.py pinterest-publish/tests/fixtures/
git commit -m "feat(pinterest-publish): markdown parser with validation"
```

---

## Task 3: URL mapper

**Files:**
- Create: `pinterest-publish/tests/test_url_mapper.py`
- Create: `pinterest-publish/pinterest_publish/url_mapper.py`

- [ ] **Step 1: Write failing tests**

`pinterest-publish/tests/test_url_mapper.py`:
```python
from pathlib import Path
import pytest
from pinterest_publish.url_mapper import UrlMapper, UrlMapError

def _write_yaml(tmp_path: Path, contents: str) -> Path:
    p = tmp_path / "url-map.yaml"
    p.write_text(contents)
    return p

def test_exact_match_wins(tmp_path):
    p = _write_yaml(tmp_path, """
default: "https://example.com/"
pins:
  pin-01.png: "https://example.com/iep"
  pin-02.png: "https://example.com/sleep"
""")
    m = UrlMapper.load(p)
    assert m.url_for("pin-01.png") == "https://example.com/iep"
    assert m.url_for("pin-02.png") == "https://example.com/sleep"

def test_falls_back_to_default(tmp_path):
    p = _write_yaml(tmp_path, """
default: "https://example.com/"
pins:
  pin-01.png: "https://example.com/iep"
""")
    m = UrlMapper.load(p)
    assert m.url_for("pin-99.png") == "https://example.com/"

def test_missing_default_raises(tmp_path):
    p = _write_yaml(tmp_path, """
pins:
  pin-01.png: "https://example.com/iep"
""")
    with pytest.raises(UrlMapError, match="default"):
        UrlMapper.load(p)

def test_aliases_lookup(tmp_path):
    p = _write_yaml(tmp_path, """
default: "https://example.com/"
pins:
  pin-01.png: "https://example.com/iep"
aliases:
  pin-01.png:
    - "Old Renamed Title"
    - "Another Old Title"
""")
    m = UrlMapper.load(p)
    assert m.filename_for_alias("Old Renamed Title") == "pin-01.png"
    assert m.filename_for_alias("Another Old Title") == "pin-01.png"
    assert m.filename_for_alias("Unknown Title") is None

def test_missing_aliases_section_ok(tmp_path):
    p = _write_yaml(tmp_path, """
default: "https://example.com/"
pins:
  pin-01.png: "https://example.com/iep"
""")
    m = UrlMapper.load(p)
    assert m.filename_for_alias("Anything") is None

def test_invalid_url_raises(tmp_path):
    p = _write_yaml(tmp_path, """
default: "not-a-url"
pins:
  pin-01.png: "https://example.com/"
""")
    with pytest.raises(UrlMapError, match="https"):
        UrlMapper.load(p)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd pinterest-publish && pytest tests/test_url_mapper.py -v
```

Expected: ImportError / 6 failures.

- [ ] **Step 3: Implement url_mapper**

`pinterest-publish/pinterest_publish/url_mapper.py`:
```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd pinterest-publish && pytest tests/test_url_mapper.py -v
```

Expected: 6 PASS.

- [ ] **Step 5: Commit**

```bash
git add pinterest-publish/pinterest_publish/url_mapper.py pinterest-publish/tests/test_url_mapper.py
git commit -m "feat(pinterest-publish): URL mapper with default + aliases"
```

---

## Task 4: Pinterest API client

**Files:**
- Create: `pinterest-publish/tests/test_api.py`
- Create: `pinterest-publish/pinterest_publish/api.py`

- [ ] **Step 1: Write failing tests using `responses` library**

`pinterest-publish/tests/test_api.py`:
```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd pinterest-publish && pytest tests/test_api.py -v
```

Expected: ImportError / 5 failures.

- [ ] **Step 3: Implement API client**

`pinterest-publish/pinterest_publish/api.py`:
```python
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
            "Content-Type": "application/json",
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
            if not bookmark:
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
        if section_id:
            body["board_section_id"] = section_id
        return self._request("POST", "/pins", json=body).json()

    def delete_pin(self, pin_id: str) -> None:
        self._request("DELETE", f"/pins/{pin_id}")
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd pinterest-publish && pytest tests/test_api.py -v
```

Expected: 5 PASS.

- [ ] **Step 5: Commit**

```bash
git add pinterest-publish/pinterest_publish/api.py pinterest-publish/tests/test_api.py
git commit -m "feat(pinterest-publish): Pinterest v5 REST client"
```

---

## Task 5: Auth — token storage + refresh (non-interactive parts)

**Files:**
- Create: `pinterest-publish/tests/test_auth.py`
- Create: `pinterest-publish/pinterest_publish/auth.py`

This task handles **token persistence and refresh**. The interactive browser flow lives in Task 6.

- [ ] **Step 1: Write failing tests**

`pinterest-publish/tests/test_auth.py`:
```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd pinterest-publish && pytest tests/test_auth.py -v
```

Expected: ImportError / failures.

- [ ] **Step 3: Implement auth (non-interactive parts)**

`pinterest-publish/pinterest_publish/auth.py`:
```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd pinterest-publish && pytest tests/test_auth.py -v
```

Expected: 7 PASS.

- [ ] **Step 5: Commit**

```bash
git add pinterest-publish/pinterest_publish/auth.py pinterest-publish/tests/test_auth.py
git commit -m "feat(pinterest-publish): token storage + refresh"
```

---

## Task 6: Auth — interactive browser OAuth flow

**Files:**
- Modify: `pinterest-publish/pinterest_publish/auth.py` (add `run_interactive_oauth`)

This adds the one-time browser flow. The flow is hard to unit test directly (it spawns a browser and listens on a real port), so we rely on a manual smoke test plus the existing refresh tests.

- [ ] **Step 1: Add `run_interactive_oauth` to `auth.py`**

Append to `pinterest-publish/pinterest_publish/auth.py`:
```python
import base64
import secrets
import threading
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import List


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
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
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

        # Wait for the callback — poll up to 5 minutes
        for _ in range(300):
            if "code" in captured or "error" in captured:
                break
            time.sleep(1)
    finally:
        server.shutdown()
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
    resp = requests.post(f"{api_base}/oauth/token", headers=headers, data=data)
    if resp.status_code >= 400:
        raise AuthError(f"token exchange failed: {resp.status_code} {resp.text[:200]}")
    body = resp.json()
    return Token(
        access_token=body["access_token"],
        refresh_token=body["refresh_token"],
        expires_at=time.time() + int(body.get("expires_in", 2592000)),
    )
```

- [ ] **Step 2: Run existing auth tests to confirm nothing regressed**

```bash
cd pinterest-publish && pytest tests/test_auth.py -v
```

Expected: 7 PASS (no new tests added — the OAuth flow is exercised manually).

- [ ] **Step 3: Commit**

```bash
git add pinterest-publish/pinterest_publish/auth.py
git commit -m "feat(pinterest-publish): interactive browser OAuth flow"
```

---

## Task 7: Audit command

**Files:**
- Create: `pinterest-publish/tests/test_audit.py`
- Create: `pinterest-publish/pinterest_publish/audit.py`

- [ ] **Step 1: Write failing tests**

`pinterest-publish/tests/test_audit.py`:
```python
import json
from pathlib import Path
from unittest.mock import MagicMock
from pinterest_publish.audit import run_audit, AuditReport, render_audit_md

def _mock_client():
    client = MagicMock()
    client.list_boards.return_value = [
        {"id": "b1", "name": "Autism Parenting Tips", "pin_count": 25},
    ]
    client.list_board_sections.return_value = [
        {"id": "s1", "name": "IEP & School Advocacy"},
        {"id": "s2", "name": "Sleep"},
    ]
    client.list_pins.return_value = [
        {
            "id": "p1",
            "title": "Old Title",
            "board_id": "b1",
            "board_section_id": "s1",
            "link": "https://example.com/",
        },
    ]
    return client

def test_audit_collects_boards_sections_pins(tmp_path):
    client = _mock_client()
    report = run_audit(client, output_dir=tmp_path)
    assert len(report.boards) == 1
    assert report.boards[0]["sections"][0]["name"] == "IEP & School Advocacy"
    assert len(report.pins) == 1

def test_audit_writes_json_and_md(tmp_path):
    client = _mock_client()
    report = run_audit(client, output_dir=tmp_path)
    assert (tmp_path / "audit-report.json").exists()
    assert (tmp_path / "audit-report.md").exists()
    md = (tmp_path / "audit-report.md").read_text()
    assert "Autism Parenting Tips" in md
    assert "Old Title" in md

def test_render_audit_md_lists_pins_per_board():
    report = AuditReport(
        boards=[{
            "id": "b1",
            "name": "Test Board",
            "sections": [{"id": "s1", "name": "Sec1"}],
        }],
        pins=[{"id": "p1", "title": "Pin A", "board_id": "b1", "board_section_id": "s1"}],
    )
    md = render_audit_md(report)
    assert "Test Board" in md
    assert "Pin A" in md
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd pinterest-publish && pytest tests/test_audit.py -v
```

Expected: ImportError / failures.

- [ ] **Step 3: Implement audit**

`pinterest-publish/pinterest_publish/audit.py`:
```python
"""Audit: list boards, sections, pins; write reports."""
from __future__ import annotations
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Dict, Any

from .api import PinterestClient


@dataclass
class AuditReport:
    boards: List[Dict[str, Any]] = field(default_factory=list)
    pins: List[Dict[str, Any]] = field(default_factory=list)


def run_audit(client: PinterestClient, output_dir: Path) -> AuditReport:
    output_dir.mkdir(parents=True, exist_ok=True)

    boards_raw = client.list_boards()
    boards: List[Dict[str, Any]] = []
    for b in boards_raw:
        sections = client.list_board_sections(b["id"])
        boards.append({
            "id": b["id"],
            "name": b["name"],
            "pin_count": b.get("pin_count", 0),
            "sections": [{"id": s["id"], "name": s["name"]} for s in sections],
        })

    pins = client.list_pins()
    report = AuditReport(boards=boards, pins=pins)

    (output_dir / "audit-report.json").write_text(
        json.dumps(asdict(report), indent=2)
    )
    (output_dir / "audit-report.md").write_text(render_audit_md(report))
    return report


def render_audit_md(report: AuditReport) -> str:
    lines: List[str] = []
    lines.append("# Pinterest audit report\n")
    lines.append(f"Boards: {len(report.boards)}  |  Pins: {len(report.pins)}\n")

    for board in report.boards:
        lines.append(f"\n## {board['name']}  (id: `{board['id']}`)")
        if board.get("sections"):
            lines.append("\n### Sections")
            for s in board["sections"]:
                lines.append(f"- {s['name']}  (id: `{s['id']}`)")

    lines.append("\n## Pins\n")
    for p in report.pins:
        title = p.get("title") or "(untitled)"
        bid = p.get("board_id") or "?"
        sid = p.get("board_section_id") or "-"
        link = p.get("link") or ""
        lines.append(
            f"- [{p['id']}] **{title}** — board:`{bid}` section:`{sid}`  → {link}"
        )

    return "\n".join(lines) + "\n"
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd pinterest-publish && pytest tests/test_audit.py -v
```

Expected: 3 PASS.

- [ ] **Step 5: Commit**

```bash
git add pinterest-publish/pinterest_publish/audit.py pinterest-publish/tests/test_audit.py
git commit -m "feat(pinterest-publish): audit boards/sections/pins"
```

---

## Task 8: Plan command

**Files:**
- Create: `pinterest-publish/tests/test_plan.py`
- Create: `pinterest-publish/tests/fixtures/sample-audit.json`
- Create: `pinterest-publish/pinterest_publish/plan.py`

- [ ] **Step 1: Create sample audit fixture**

`pinterest-publish/tests/fixtures/sample-audit.json`:
```json
{
  "boards": [
    {
      "id": "b1",
      "name": "Autism Parenting Tips",
      "pin_count": 2,
      "sections": [
        {"id": "s1", "name": "IEP & School Advocacy"},
        {"id": "s2", "name": "Sleep"}
      ]
    }
  ],
  "pins": [
    {"id": "p_old_iep", "title": "Test IEP Accommodations Title", "board_id": "b1", "board_section_id": "s1", "link": "https://x"},
    {"id": "p_orphan", "title": "Some Old Pin Title", "board_id": "b1", "board_section_id": "s2", "link": "https://x"}
  ]
}
```

- [ ] **Step 2: Write failing tests**

`pinterest-publish/tests/test_plan.py`:
```python
import json
from pathlib import Path
from pinterest_publish.parser import PinRecord
from pinterest_publish.url_mapper import UrlMapper
from pinterest_publish.plan import build_plan, PublishPlan, render_plan_md
from pinterest_publish.audit import AuditReport

FIXTURES = Path(__file__).parent / "fixtures"

def _audit_from_fixture() -> AuditReport:
    data = json.loads((FIXTURES / "sample-audit.json").read_text())
    return AuditReport(boards=data["boards"], pins=data["pins"])

def _records():
    return [
        PinRecord(
            filename="sample-pin.png",
            image_path=FIXTURES / "sample-pin.png",
            title="Test IEP Accommodations Title",
            description="d",
            board_path="Autism Parenting Tips / IEP & School Advocacy",
        ),
        PinRecord(
            filename="sample-pin.png",
            image_path=FIXTURES / "sample-pin.png",
            title="Test Sleep Strategies Title",
            description="d",
            board_path="Autism Parenting Tips / Sleep",
        ),
    ]

def _mapper(tmp_path):
    p = tmp_path / "url-map.yaml"
    p.write_text(
        'default: "https://example.com/"\n'
        'pins:\n'
        '  sample-pin.png: "https://example.com/x"\n'
    )
    return UrlMapper.load(p)

def test_clean_match_produces_delete_and_create(tmp_path):
    plan = build_plan(
        records=_records(),
        audit=_audit_from_fixture(),
        mapper=_mapper(tmp_path),
    )
    # First record's title matches live pin "p_old_iep" -> delete + create
    deletes_titles = [d["title"] for d in plan.deletes]
    assert "Test IEP Accommodations Title" in deletes_titles
    creates_titles = [c["title"] for c in plan.creates]
    assert "Test IEP Accommodations Title" in creates_titles
    # Both records produce a create
    assert len(plan.creates) == 2

def test_orphaned_live_pin_listed(tmp_path):
    plan = build_plan(
        records=_records(),
        audit=_audit_from_fixture(),
        mapper=_mapper(tmp_path),
    )
    orphan_titles = [o["title"] for o in plan.orphaned_live_pins]
    assert "Some Old Pin Title" in orphan_titles

def test_unresolved_board_listed(tmp_path):
    records = [
        PinRecord(
            filename="sample-pin.png",
            image_path=FIXTURES / "sample-pin.png",
            title="X",
            description="d",
            board_path="Nonexistent Board / Whatever",
        ),
    ]
    plan = build_plan(
        records=records,
        audit=_audit_from_fixture(),
        mapper=_mapper(tmp_path),
    )
    assert len(plan.unresolved_boards) == 1
    assert plan.unresolved_boards[0]["board_path"] == "Nonexistent Board / Whatever"
    assert plan.creates == []  # blocked

def test_alias_resolves_renamed_live_pin(tmp_path):
    p = tmp_path / "url-map.yaml"
    p.write_text(
        'default: "https://example.com/"\n'
        'pins:\n'
        '  sample-pin.png: "https://example.com/x"\n'
        'aliases:\n'
        '  sample-pin.png:\n'
        '    - "Some Old Pin Title"\n'
    )
    mapper = UrlMapper.load(p)
    records = [
        PinRecord(
            filename="sample-pin.png",
            image_path=FIXTURES / "sample-pin.png",
            title="Test IEP Accommodations Title",
            description="d",
            board_path="Autism Parenting Tips / IEP & School Advocacy",
        ),
    ]
    plan = build_plan(records=records, audit=_audit_from_fixture(), mapper=mapper)
    deletes_titles = [d["title"] for d in plan.deletes]
    # Should delete BOTH the title-match AND the alias-match
    assert "Test IEP Accommodations Title" in deletes_titles
    assert "Some Old Pin Title" in deletes_titles
    assert plan.orphaned_live_pins == []  # alias claimed it

def test_render_plan_md_summary(tmp_path):
    plan = build_plan(
        records=_records(),
        audit=_audit_from_fixture(),
        mapper=_mapper(tmp_path),
    )
    md = render_plan_md(plan)
    assert "DELETE" in md
    assert "CREATE" in md
    assert "Test IEP Accommodations Title" in md
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
cd pinterest-publish && pytest tests/test_plan.py -v
```

Expected: ImportError / failures.

- [ ] **Step 4: Implement plan**

`pinterest-publish/pinterest_publish/plan.py`:
```python
"""Cross-reference repo pins with live audit, build delete+create plan."""
from __future__ import annotations
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Dict, Any, Optional

from .audit import AuditReport
from .parser import PinRecord
from .url_mapper import UrlMapper


@dataclass
class PublishPlan:
    deletes: List[Dict[str, Any]] = field(default_factory=list)
    creates: List[Dict[str, Any]] = field(default_factory=list)
    orphaned_live_pins: List[Dict[str, Any]] = field(default_factory=list)
    unresolved_boards: List[Dict[str, Any]] = field(default_factory=list)


def build_plan(
    records: List[PinRecord],
    audit: AuditReport,
    mapper: UrlMapper,
) -> PublishPlan:
    plan = PublishPlan()

    # Index live pins by exact title (case-sensitive — Pinterest is case-sensitive)
    pins_by_title: Dict[str, Dict[str, Any]] = {
        p["title"]: p for p in audit.pins if p.get("title")
    }
    claimed_pin_ids: set = set()

    # Index boards/sections by name
    boards_by_name: Dict[str, Dict[str, Any]] = {b["name"]: b for b in audit.boards}

    for rec in records:
        # Resolve board path
        board_id, section_id, board_err = _resolve_board(rec.board_path, boards_by_name)
        if board_err is not None:
            plan.unresolved_boards.append({
                "filename": rec.filename,
                "board_path": rec.board_path,
                "reason": board_err,
            })
            continue

        # Find live pin to delete (by title, then by alias)
        live_pin = pins_by_title.get(rec.title)
        if live_pin and live_pin["id"] not in claimed_pin_ids:
            plan.deletes.append({
                "id": live_pin["id"],
                "title": live_pin["title"],
                "board_id": live_pin.get("board_id"),
                "board_section_id": live_pin.get("board_section_id"),
            })
            claimed_pin_ids.add(live_pin["id"])

        # Also delete any aliased pin titles tied to this filename
        for live_p in audit.pins:
            if live_p["id"] in claimed_pin_ids:
                continue
            alias_target = mapper.filename_for_alias(live_p.get("title", "") or "")
            if alias_target == rec.filename:
                plan.deletes.append({
                    "id": live_p["id"],
                    "title": live_p["title"],
                    "board_id": live_p.get("board_id"),
                    "board_section_id": live_p.get("board_section_id"),
                })
                claimed_pin_ids.add(live_p["id"])

        # Create new pin
        plan.creates.append({
            "filename": rec.filename,
            "image_path": str(rec.image_path),
            "title": rec.title,
            "description": rec.description,
            "link": mapper.url_for(rec.filename),
            "board_id": board_id,
            "board_section_id": section_id,
            "board_path": rec.board_path,
        })

    # Orphaned live pins = live pins not claimed by any record (by title or alias)
    for p in audit.pins:
        if p["id"] not in claimed_pin_ids:
            plan.orphaned_live_pins.append({
                "id": p["id"],
                "title": p.get("title", "(untitled)"),
                "board_id": p.get("board_id"),
            })

    return plan


def _resolve_board(
    board_path: str,
    boards_by_name: Dict[str, Dict[str, Any]],
) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """Return (board_id, section_id, error_msg). error_msg=None means success."""
    parts = [p.strip() for p in board_path.split("/", 1)]
    board_name = parts[0]
    section_name = parts[1] if len(parts) > 1 else None

    board = boards_by_name.get(board_name)
    if not board:
        return None, None, f"board '{board_name}' not found on account"

    if section_name is None:
        return board["id"], None, None

    for s in board.get("sections", []):
        if s["name"] == section_name:
            return board["id"], s["id"], None

    return board["id"], None, f"section '{section_name}' not found in board '{board_name}'"


def write_plan(plan: PublishPlan, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "publish-plan.json").write_text(
        json.dumps(asdict(plan), indent=2)
    )
    (output_dir / "publish-plan.md").write_text(render_plan_md(plan))


def render_plan_md(plan: PublishPlan) -> str:
    lines: List[str] = []
    lines.append("# Pinterest publish plan\n")
    lines.append(
        f"Summary: {len(plan.deletes)} deletes, {len(plan.creates)} creates, "
        f"{len(plan.orphaned_live_pins)} orphaned live pins, "
        f"{len(plan.unresolved_boards)} unresolved boards\n"
    )

    lines.append("\n## DELETE (live pins flagged for removal)\n")
    if not plan.deletes:
        lines.append("_(none)_\n")
    for d in plan.deletes:
        lines.append(f"- [{d['id']}] **{d['title']}**  (board `{d.get('board_id')}`)")

    lines.append("\n## CREATE (new pins from repo)\n")
    if not plan.creates:
        lines.append("_(none)_\n")
    for c in plan.creates:
        lines.append(
            f"- `{c['filename']}` → {c['board_path']}\n"
            f"    title: {c['title']}\n"
            f"    link:  {c['link']}"
        )

    lines.append("\n## ORPHANED LIVE PINS (no repo match — left untouched)\n")
    if not plan.orphaned_live_pins:
        lines.append("_(none)_\n")
    for o in plan.orphaned_live_pins:
        lines.append(f"- [{o['id']}] **{o['title']}** (board `{o.get('board_id')}`)")

    lines.append("\n## UNRESOLVED BOARDS (creates blocked)\n")
    if not plan.unresolved_boards:
        lines.append("_(none)_\n")
    for u in plan.unresolved_boards:
        lines.append(f"- `{u['filename']}`: {u['board_path']} — {u['reason']}")

    return "\n".join(lines) + "\n"
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd pinterest-publish && pytest tests/test_plan.py -v
```

Expected: 5 PASS.

- [ ] **Step 6: Commit**

```bash
git add pinterest-publish/pinterest_publish/plan.py pinterest-publish/tests/test_plan.py pinterest-publish/tests/fixtures/sample-audit.json
git commit -m "feat(pinterest-publish): build publish plan with dedup + alias support"
```

---

## Task 9: Apply command

**Files:**
- Create: `pinterest-publish/tests/test_apply.py`
- Create: `pinterest-publish/pinterest_publish/apply.py`

- [ ] **Step 1: Write failing tests**

`pinterest-publish/tests/test_apply.py`:
```python
import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, ANY
import pytest
from pinterest_publish.api import RateLimitError
from pinterest_publish.plan import PublishPlan
from pinterest_publish.apply import (
    apply_plan,
    ApplyOptions,
    ApplyLog,
    DailyCapReached,
)

def _client():
    c = MagicMock()
    c.delete_pin.return_value = None
    c.create_pin.return_value = {"id": "newpin"}
    return c

def _plan():
    plan = PublishPlan()
    plan.deletes = [{"id": "p1", "title": "Old"}]
    plan.creates = [{
        "filename": "a.png",
        "image_path": "/tmp/a.png",  # we'll mock _read_image
        "title": "New A",
        "description": "d",
        "link": "https://example.com/",
        "board_id": "b1",
        "board_section_id": "s1",
        "board_path": "B / S",
    }]
    return plan

def test_dry_run_makes_no_api_calls(tmp_path, monkeypatch):
    client = _client()
    monkeypatch.setattr("pinterest_publish.apply._read_image_bytes", lambda p: b"PNG")
    apply_plan(
        plan=_plan(),
        client=client,
        log_path=tmp_path / "log.jsonl",
        options=ApplyOptions(dry_run=True, yes=True, max_creates=None),
    )
    client.delete_pin.assert_not_called()
    client.create_pin.assert_not_called()

def test_apply_executes_delete_and_create(tmp_path, monkeypatch):
    client = _client()
    monkeypatch.setattr("pinterest_publish.apply._read_image_bytes", lambda p: b"PNG")
    apply_plan(
        plan=_plan(),
        client=client,
        log_path=tmp_path / "log.jsonl",
        options=ApplyOptions(dry_run=False, yes=True, max_creates=None),
    )
    client.delete_pin.assert_called_once_with("p1")
    client.create_pin.assert_called_once_with(
        title="New A",
        description="d",
        link="https://example.com/",
        board_id="b1",
        section_id="s1",
        image_bytes=b"PNG",
    )

def test_resume_skips_already_logged(tmp_path, monkeypatch):
    log_path = tmp_path / "log.jsonl"
    # Pre-seed log: delete already done
    log_path.write_text(json.dumps({
        "ts": "2026-04-29T00:00:00Z",
        "action": "delete",
        "key": "p1",
        "ok": True,
    }) + "\n")

    client = _client()
    monkeypatch.setattr("pinterest_publish.apply._read_image_bytes", lambda p: b"PNG")
    apply_plan(
        plan=_plan(),
        client=client,
        log_path=log_path,
        options=ApplyOptions(dry_run=False, yes=True, max_creates=None),
    )
    client.delete_pin.assert_not_called()
    client.create_pin.assert_called_once()

def test_max_creates_caps_creates(tmp_path, monkeypatch):
    plan = PublishPlan()
    plan.creates = [
        {"filename": f"p{i}.png", "image_path": "/x", "title": f"T{i}",
         "description": "d", "link": "https://example.com/",
         "board_id": "b1", "board_section_id": None, "board_path": "B"}
        for i in range(5)
    ]
    client = _client()
    monkeypatch.setattr("pinterest_publish.apply._read_image_bytes", lambda p: b"PNG")
    apply_plan(
        plan=plan,
        client=client,
        log_path=tmp_path / "log.jsonl",
        options=ApplyOptions(dry_run=False, yes=True, max_creates=2),
    )
    assert client.create_pin.call_count == 2

def test_rate_limit_exits_cleanly(tmp_path, monkeypatch):
    plan = PublishPlan()
    plan.creates = [
        {"filename": "p.png", "image_path": "/x", "title": "T",
         "description": "d", "link": "https://example.com/",
         "board_id": "b1", "board_section_id": None, "board_path": "B"}
    ]
    client = MagicMock()
    client.create_pin.side_effect = RateLimitError(retry_after=999)
    monkeypatch.setattr("pinterest_publish.apply._read_image_bytes", lambda p: b"PNG")
    monkeypatch.setattr("pinterest_publish.apply._sleep", lambda s: None)

    with pytest.raises(DailyCapReached):
        apply_plan(
            plan=plan,
            client=client,
            log_path=tmp_path / "log.jsonl",
            options=ApplyOptions(dry_run=False, yes=True, max_creates=None),
        )
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd pinterest-publish && pytest tests/test_apply.py -v
```

Expected: ImportError / failures.

- [ ] **Step 3: Implement apply**

`pinterest-publish/pinterest_publish/apply.py`:
```python
"""Execute a publish plan: delete olds, create news, log every API call."""
from __future__ import annotations
import json
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional, Set

from .api import PinterestClient, RateLimitError
from .plan import PublishPlan


class DailyCapReached(Exception):
    """Raised when Pinterest 429s and we've decided to stop for the day."""


@dataclass
class ApplyOptions:
    dry_run: bool = False
    yes: bool = False
    max_creates: Optional[int] = None


class ApplyLog:
    """Append-only log of completed actions, keyed by (action, key)."""

    def __init__(self, path: Path):
        self.path = path
        self._completed_keys: Set[tuple] = set()
        if path.exists():
            for line in path.read_text().splitlines():
                if not line.strip():
                    continue
                rec = json.loads(line)
                if rec.get("ok"):
                    self._completed_keys.add((rec["action"], rec["key"]))

    def already_done(self, action: str, key: str) -> bool:
        return (action, key) in self._completed_keys

    def record(self, action: str, key: str, ok: bool, detail: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        line = json.dumps({
            "ts": ts, "action": action, "key": key, "ok": ok, "detail": detail,
        })
        with self.path.open("a") as f:
            f.write(line + "\n")
        if ok:
            self._completed_keys.add((action, key))


def apply_plan(
    plan: PublishPlan,
    client: PinterestClient,
    log_path: Path,
    options: ApplyOptions,
) -> None:
    log = ApplyLog(log_path)

    if options.dry_run:
        _print_dry_run(plan, options)
        return

    if not options.yes:
        _confirm_destructive(plan)

    # Deletes first
    for d in plan.deletes:
        if log.already_done("delete", d["id"]):
            continue
        try:
            client.delete_pin(d["id"])
            log.record("delete", d["id"], ok=True, detail={"title": d.get("title")})
            print(f"deleted [{d['id']}] {d.get('title','')}")
        except RateLimitError as e:
            _backoff_or_exit(e, action="delete", key=d["id"])
        except Exception as e:
            log.record("delete", d["id"], ok=False, detail={"error": str(e)})
            print(f"FAILED delete [{d['id']}]: {e}", file=sys.stderr)

    # Then creates, capped by max_creates
    creates_done = 0
    cap = options.max_creates if options.max_creates is not None else len(plan.creates)
    for c in plan.creates:
        if creates_done >= cap:
            print(f"max-creates cap reached ({cap}) — stopping")
            return
        key = c["filename"]
        if log.already_done("create", key):
            continue
        try:
            image_bytes = _read_image_bytes(c["image_path"])
            result = client.create_pin(
                title=c["title"],
                description=c["description"],
                link=c["link"],
                board_id=c["board_id"],
                section_id=c.get("board_section_id"),
                image_bytes=image_bytes,
            )
            log.record("create", key, ok=True, detail={"pin_id": result.get("id")})
            print(f"created {key} -> pin_id {result.get('id')}")
            creates_done += 1
        except RateLimitError as e:
            log.record("create", key, ok=False, detail={"rate_limited": True})
            _backoff_or_exit(e, action="create", key=key)
        except Exception as e:
            log.record("create", key, ok=False, detail={"error": str(e)})
            print(f"FAILED create {key}: {e}", file=sys.stderr)


def _read_image_bytes(image_path: str) -> bytes:
    return Path(image_path).read_bytes()


def _sleep(seconds: float) -> None:
    time.sleep(seconds)


def _backoff_or_exit(exc: RateLimitError, action: str, key: str) -> None:
    """One short backoff (max 60s); if still capped, exit cleanly."""
    wait = min(exc.retry_after, 60)
    if wait <= 60:
        print(f"rate limited on {action}/{key}; backing off {wait}s")
        _sleep(wait)
    raise DailyCapReached(
        f"Pinterest rate limit hit (retry-after={exc.retry_after}s). "
        f"State saved — re-run apply tomorrow."
    )


def _confirm_destructive(plan: PublishPlan) -> None:
    if not plan.deletes:
        return
    print(f"\nABOUT TO DELETE {len(plan.deletes)} live pins.")
    for d in plan.deletes:
        print(f"  [{d['id']}] {d.get('title','')}")
    answer = input("\nType 'yes' to proceed: ").strip().lower()
    if answer != "yes":
        print("aborted.")
        sys.exit(1)


def _print_dry_run(plan: PublishPlan, options: ApplyOptions) -> None:
    print("=== DRY RUN ===")
    print(f"Would delete {len(plan.deletes)} pins:")
    for d in plan.deletes:
        print(f"  DELETE [{d['id']}] {d.get('title','')}")
    cap = options.max_creates if options.max_creates is not None else len(plan.creates)
    print(f"\nWould create {min(cap, len(plan.creates))} of {len(plan.creates)} pins:")
    for c in plan.creates[:cap]:
        print(f"  CREATE {c['filename']} -> board={c['board_id']} section={c.get('board_section_id')}")
        print(f"    title: {c['title']}")
        print(f"    link:  {c['link']}")
    if cap < len(plan.creates):
        print(f"  ({len(plan.creates) - cap} more pins capped by --max-creates)")
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd pinterest-publish && pytest tests/test_apply.py -v
```

Expected: 5 PASS.

- [ ] **Step 5: Commit**

```bash
git add pinterest-publish/pinterest_publish/apply.py pinterest-publish/tests/test_apply.py
git commit -m "feat(pinterest-publish): apply executor with logging + resume"
```

---

## Task 10: CLI entry point

**Files:**
- Create: `pinterest-publish/pinterest_publish/cli.py`

The CLI wires all the pieces together. Largely orchestration, no new business logic. Manual smoke test rather than unit tests.

- [ ] **Step 1: Implement CLI**

`pinterest-publish/pinterest_publish/cli.py`:
```python
"""Command-line entry: auth | audit | plan | apply."""
from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path
from typing import List

from . import config
from .api import PinterestClient
from .audit import run_audit, AuditReport
from .auth import (
    AuthError, Token, TokenStore, load_or_refresh, run_interactive_oauth,
)
from .apply import apply_plan, ApplyOptions, DailyCapReached
from .parser import parse_pinterest_posts
from .plan import build_plan, write_plan
from .url_mapper import UrlMapper


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="pinterest_publish")
    parser.add_argument(
        "--env", choices=["production", "sandbox"], default="production",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("auth", help="One-time OAuth flow")
    sub.add_parser("audit", help="List boards / sections / pins")
    sub.add_parser("plan", help="Build delete+create plan")
    ap_apply = sub.add_parser("apply", help="Execute the plan")
    ap_apply.add_argument("--dry-run", action="store_true")
    ap_apply.add_argument("--yes", action="store_true",
                          help="skip destructive-action confirmation prompt")
    ap_apply.add_argument("--max-creates", type=int, default=None)
    ap_apply.add_argument("--create-missing", action="store_true",
                          help="create missing boards/sections on the fly")

    args = parser.parse_args(argv)

    api_base = (
        config.API_BASE_PRODUCTION if args.env == "production"
        else config.API_BASE_SANDBOX
    )

    try:
        if args.cmd == "auth":
            return _cmd_auth(api_base)
        if args.cmd == "audit":
            return _cmd_audit(api_base)
        if args.cmd == "plan":
            return _cmd_plan()
        if args.cmd == "apply":
            return _cmd_apply(api_base, args)
    except AuthError as e:
        print(f"AUTH ERROR: {e}", file=sys.stderr)
        return 2
    except DailyCapReached as e:
        print(str(e), file=sys.stderr)
        return 0  # not an error — expected pause point
    return 1


def _client(api_base: str) -> PinterestClient:
    cid = os.environ.get("PINTEREST_CLIENT_ID")
    csec = os.environ.get("PINTEREST_CLIENT_SECRET")
    if not cid or not csec:
        raise AuthError(
            "PINTEREST_CLIENT_ID and PINTEREST_CLIENT_SECRET must be set "
            "(via env or pinterest-publish/.env)"
        )
    store = TokenStore(config.TOKEN_PATH)
    tok = load_or_refresh(store, cid, csec, api_base)
    return PinterestClient(access_token=tok.access_token, api_base=api_base)


def _cmd_auth(api_base: str) -> int:
    cid = os.environ.get("PINTEREST_CLIENT_ID")
    csec = os.environ.get("PINTEREST_CLIENT_SECRET")
    if not cid or not csec:
        print(
            "Set PINTEREST_CLIENT_ID and PINTEREST_CLIENT_SECRET first.",
            file=sys.stderr,
        )
        return 2
    print("Starting interactive OAuth flow ...")
    tok = run_interactive_oauth(
        client_id=cid,
        client_secret=csec,
        api_base=api_base,
        redirect_uri=config.OAUTH_REDIRECT_URI,
        callback_port=config.OAUTH_CALLBACK_PORT,
        scopes=config.SCOPES_PUBLISH,
        authorize_url=config.OAUTH_AUTHORIZE_URL,
    )
    TokenStore(config.TOKEN_PATH).save(tok)
    print(f"Saved token to {config.TOKEN_PATH}")
    return 0


def _cmd_audit(api_base: str) -> int:
    client = _client(api_base)
    print("Listing boards, sections, pins ...")
    run_audit(client, output_dir=config.STATE_DIR)
    print(f"Wrote {config.AUDIT_REPORT_JSON}")
    print(f"Wrote {config.AUDIT_REPORT_MD}")
    return 0


def _cmd_plan() -> int:
    if not config.AUDIT_REPORT_JSON.exists():
        print("Run `audit` first.", file=sys.stderr)
        return 2

    audit_data = json.loads(config.AUDIT_REPORT_JSON.read_text())
    audit = AuditReport(boards=audit_data["boards"], pins=audit_data["pins"])

    records = parse_pinterest_posts(
        md_path=config.PINTEREST_POSTS_MD,
        image_dir=config.PINTEREST_SOURCE_DIR,
    )
    mapper = UrlMapper.load(config.URL_MAP_PATH)
    plan = build_plan(records=records, audit=audit, mapper=mapper)
    write_plan(plan, output_dir=config.STATE_DIR)
    print(f"Wrote {config.PUBLISH_PLAN_JSON}")
    print(f"Wrote {config.PUBLISH_PLAN_MD}")
    print(
        f"Summary: {len(plan.deletes)} deletes, {len(plan.creates)} creates, "
        f"{len(plan.orphaned_live_pins)} orphaned, "
        f"{len(plan.unresolved_boards)} unresolved boards"
    )
    return 0


def _cmd_apply(api_base: str, args: argparse.Namespace) -> int:
    if not config.PUBLISH_PLAN_JSON.exists():
        print("Run `plan` first.", file=sys.stderr)
        return 2

    plan_data = json.loads(config.PUBLISH_PLAN_JSON.read_text())
    from .plan import PublishPlan
    plan = PublishPlan(
        deletes=plan_data["deletes"],
        creates=plan_data["creates"],
        orphaned_live_pins=plan_data["orphaned_live_pins"],
        unresolved_boards=plan_data["unresolved_boards"],
    )

    if plan.unresolved_boards and not args.create_missing:
        print(
            f"BLOCKED: {len(plan.unresolved_boards)} unresolved boards. "
            "Re-run with --create-missing or fix repo metadata.",
            file=sys.stderr,
        )
        return 2

    client = _client(api_base)
    apply_plan(
        plan=plan,
        client=client,
        log_path=config.APPLY_LOG,
        options=ApplyOptions(
            dry_run=args.dry_run,
            yes=args.yes,
            max_creates=args.max_creates,
        ),
    )
    return 0
```

- [ ] **Step 2: Smoke-test `--help`**

```bash
cd pinterest-publish && python -m pinterest_publish --help
```

Expected: usage text showing `auth | audit | plan | apply`.

- [ ] **Step 3: Smoke-test apply `--help`**

```bash
cd pinterest-publish && python -m pinterest_publish apply --help
```

Expected: shows `--dry-run`, `--yes`, `--max-creates`, `--create-missing`.

- [ ] **Step 4: Run all tests one more time to confirm nothing broke**

```bash
cd pinterest-publish && pytest -v
```

Expected: all tests PASS (parser 5, url_mapper 6, api 5, auth 7, audit 3, plan 5, apply 5 = 36 tests).

- [ ] **Step 5: Commit**

```bash
git add pinterest-publish/pinterest_publish/cli.py
git commit -m "feat(pinterest-publish): CLI entry point wiring all stages"
```

---

## Task 11: Build `url-map.yaml` from spec

**Files:**
- Create: `pinterest-publish/url-map.yaml`

- [ ] **Step 1: Create the URL map**

`pinterest-publish/url-map.yaml`:
```yaml
# Per-pin destination URL on spectrumunlocked.com.
# Filename keys match content/pinterest/pin-*.png.
# Pins not listed fall through to `default`.

default: "https://www.spectrumunlocked.com/"

pins:
  pin-01-iep-accommodations.png:    "https://www.spectrumunlocked.com/blog/iep-rights-schools-wont-tell-you"
  pin-02-meltdown-vs-tantrum.png:   "https://www.spectrumunlocked.com/blog/autism-meltdown-vs-tantrum"
  pin-03-sensory-hacks.png:         "https://www.spectrumunlocked.com/blog/sensory-diet-beginners-guide"
  pin-04-sleep-strategies.png:      "https://www.spectrumunlocked.com/blog/autism-sleep-strategies"
  pin-06-potty-training.png:        "https://www.spectrumunlocked.com/blog/autism-potty-training-readiness-guide"
  pin-09-aac-communication.png:     "https://www.spectrumunlocked.com/blog/aac-for-beginners"
  pin-11-5-things-diagnosis.png:    "https://www.spectrumunlocked.com/blog/diagnosed-now-what"
  pin-12-visual-supports.png:       "https://www.spectrumunlocked.com/blog/visual-schedule-guide"
  pin-13-self-care-parents.png:     "https://www.spectrumunlocked.com/blog/self-care-autism-parents"
  pin-14-glass-child.png:           "https://www.spectrumunlocked.com/blog/autism-sibling-support"
  pin-15-autistic-burnout.png:      "https://www.spectrumunlocked.com/blog/autism-parent-burnout"
  pin-17-acceptance-vs-awareness.png: "https://www.spectrumunlocked.com/blog/autism-acceptance-month-2026"
  pin-19-feeding-challenges.png:    "https://www.spectrumunlocked.com/blog/autism-picky-eating"
  pin-20-autism-teens.png:          "https://www.spectrumunlocked.com/start-here/parents-of-teens"
  pin-24-school-accommodations.png: "https://www.spectrumunlocked.com/blog/first-iep-meeting-checklist"
  pin-25-aba-controversy.png:       "https://www.spectrumunlocked.com/blog/autism-therapy-types-explained"
  # Pins not listed fall through to `default`:
  #   pin-05-signs-of-masking
  #   pin-07-audhd
  #   pin-08-autism-in-girls
  #   pin-10-anxiety-autism
  #   pin-16-autism-myths
  #   pin-18-late-diagnosis
  #   pin-21-travel-autism
  #   pin-22-summer-camps
  #   pin-23-building-friendships

# Map live Pinterest titles back to repo filenames if you ever rename
# a pin on Pinterest after it's been published. Example:
#   pin-02-meltdown-vs-tantrum.png:
#     - "Meltdown vs Tantrum (the difference matters)"
aliases: {}
```

- [ ] **Step 2: Verify it loads via the URL mapper**

```bash
cd pinterest-publish && python -c "from pinterest_publish.url_mapper import UrlMapper; m = UrlMapper.load('url-map.yaml'); print(m.url_for('pin-02-meltdown-vs-tantrum.png')); print(m.url_for('pin-99-fake.png'))"
```

Expected output:
```
https://www.spectrumunlocked.com/blog/autism-meltdown-vs-tantrum
https://www.spectrumunlocked.com/
```

- [ ] **Step 3: Commit**

```bash
git add pinterest-publish/url-map.yaml
git commit -m "feat(pinterest-publish): pin -> destination URL mapping for 25 pins"
```

---

## Task 12: README + sandbox sanity check

**Files:**
- Create: `pinterest-publish/README.md`

- [ ] **Step 1: Create the README**

`pinterest-publish/README.md`:
```markdown
# pinterest-publish

Tool for publishing Spectrum Unlocked Pinterest pins from `content/pinterest/`
to Pinterest via the v5 API. Replaces existing old-palette pins with the
new-palette versions in a single coordinated sweep.

## One-time setup

1. Add `http://localhost:8080/callback` as a redirect URI in your Pinterest
   developer console for the "Spectrum Unlocked" app.
2. Set credentials (env vars OR a gitignored `pinterest-publish/.env`):
   ```
   PINTEREST_CLIENT_ID=1565261
   PINTEREST_CLIENT_SECRET=<from-dev-console>
   ```
3. Install:
   ```bash
   cd pinterest-publish && pip install -e ".[dev]"
   ```
4. Run the OAuth flow once:
   ```bash
   python -m pinterest_publish auth
   ```
   Browser opens, you authorize, the tool captures the token.

## Daily workflow

```bash
# 1. Read-only: see what's on Pinterest now
python -m pinterest_publish audit
less state/audit-report.md

# 2. Build the action plan from repo + audit
python -m pinterest_publish plan
less state/publish-plan.md

# 3. Dry-run apply to confirm what will happen
python -m pinterest_publish apply --dry-run

# 4. Real run, paced (good for first time)
python -m pinterest_publish apply --max-creates 1

# 5. Subsequent days — pick up where it left off
python -m pinterest_publish apply
```

## Safeguards (read this before running `apply`)

### DO

- Run `audit` and review `audit-report.md` before every `plan`.
- Run `plan` and review `publish-plan.md` before every `apply`.
- Run `apply --dry-run` the first time, always.
- Commit changes to `url-map.yaml` (it's the source of truth for destinations).
- Back up `state/apply-log.jsonl` before any re-run that involves manual
  edits to the log.
- Keep `content/pinterest/PINTEREST-POSTS.md` titles stable once a pin is
  published — changing them later breaks dedup.

### DON'T

- Don't commit `state/.pinterest-token.json` (gitignored, but worth saying
  out loud — it grants pin write access to your account).
- Don't manually edit pin titles **on Pinterest itself** — use the
  `aliases:` mechanism in `url-map.yaml` instead.
- Don't run `apply` in two terminals at once (log races, possible
  double-creates).
- Don't bypass the confirmation prompt with `--yes` unless you've verified
  the plan in dry-run first.
- Don't ship pins where the image isn't 1000×1500 — the parser will reject
  mismatched dimensions.

### Pinterest content limits (enforced at parse time)

- Title ≤ 100 chars
- Description ≤ 500 chars
- Link: valid HTTPS URL

### Trial-tier reality

- ~5 pin creates/day expected; full 25-pin sweep ≈ 5 calendar days.
- Deletes don't count against the create cap.
- The append-only log makes resuming painless: each day, just re-run
  `apply` and it picks up where it left off.

## Sandbox

The Pinterest dev console offers a Sandbox environment. Pass `--env sandbox`
to any subcommand to use it (e.g., for first-time wire-format verification):
```bash
python -m pinterest_publish --env sandbox audit
```

## Files

```
pinterest-publish/
├── README.md          # this file
├── url-map.yaml       # pin → destination URL (committed)
├── pyproject.toml     # deps + entry point
├── pinterest_publish/ # source
├── state/             # gitignored runtime artifacts
│   ├── .pinterest-token.json
│   ├── audit-report.{json,md}
│   ├── publish-plan.{json,md}
│   └── apply-log.jsonl
└── tests/             # unit tests
```

See `docs/superpowers/specs/2026-04-29-pinterest-publishing-design.md` for
the full design.
```

- [ ] **Step 2: Sandbox sanity check (manual)**

This step requires the operator to have completed the one-time auth setup. If credentials aren't configured, skip and document for the user to run manually.

```bash
cd pinterest-publish && python -m pinterest_publish --env sandbox audit
```

Expected: writes `state/audit-report.json` and `audit-report.md`. Sandbox accounts may be empty — that's fine, the audit just produces a near-empty report.

If credentials aren't yet configured, document this step for the operator to run after setup.

- [ ] **Step 3: Run full test suite one final time**

```bash
cd pinterest-publish && pytest -v
```

Expected: 36 tests PASS.

- [ ] **Step 4: Commit**

```bash
git add pinterest-publish/README.md
git commit -m "docs(pinterest-publish): operator README"
```

---

## Self-review

**Spec coverage check:**

- ✅ 4-stage CLI (auth/audit/plan/apply): Tasks 5–10
- ✅ OAuth 2.0 flow with localhost callback: Tasks 5, 6
- ✅ Token persistence and refresh: Task 5
- ✅ Source data parsing from PINTEREST-POSTS.md: Task 2
- ✅ url-map.yaml with default + aliases: Tasks 3, 11
- ✅ Image dimension + content limit validation: Task 2
- ✅ Audit boards/sections/pins: Task 7
- ✅ Plan with delete+create, alias resolution, orphan detection, unresolved boards: Task 8
- ✅ Apply with dry-run, confirmation, max-creates, append-only log, resume: Task 9
- ✅ Rate-limit handling with clean exit: Task 9
- ✅ create-missing flag plumbing: Task 10 (CLI arg) — note: actual board/section creation deferred until first time it's needed; a future task can wire `client.create_board`/`client.create_board_section` (already implemented in Task 4) into the apply flow when the operator opts in
- ✅ Sandbox env support: Task 10 (--env flag), Task 12
- ✅ Operational guidelines (DO/DON'T): Task 12 README
- ✅ .gitignore additions: Task 1

**Placeholder scan:** No "TBD"/"TODO"/"implement later"/"add appropriate handling" found.

**Type consistency:** `PinRecord` fields are consistent across Tasks 2/8. `PublishPlan` shape (deletes/creates/orphaned_live_pins/unresolved_boards) consistent across Tasks 8/9/10. `Token` (access_token/refresh_token/expires_at) consistent across Tasks 5/6/10.

**One nuance noted in self-review:** Task 10's `--create-missing` flag is currently only plumbed to *block* on unresolved boards rather than auto-create. The board/section creation methods exist in Task 4 (`client.create_board`, `client.create_board_section`) but aren't yet called from `apply`. This is intentional Phase-1 scope: by default never auto-create; if/when the operator wants it, a small follow-up adds a "resolve unresolved boards by creating them" pass before deletes. Documented as a known follow-up rather than a placeholder.
