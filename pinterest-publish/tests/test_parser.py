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
