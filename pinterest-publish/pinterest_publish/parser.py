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
