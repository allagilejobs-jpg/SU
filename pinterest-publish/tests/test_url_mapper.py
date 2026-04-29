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
