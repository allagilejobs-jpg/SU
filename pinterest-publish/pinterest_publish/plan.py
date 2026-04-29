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
        json.dumps(asdict(plan), indent=2),
        encoding="utf-8",
    )
    (output_dir / "publish-plan.md").write_text(render_plan_md(plan), encoding="utf-8")


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
            f"- `{c['filename']}` -> {c['board_path']}\n"
            f"    title: {c['title']}\n"
            f"    link:  {c['link']}"
        )

    lines.append("\n## ORPHANED LIVE PINS (no repo match -- left untouched)\n")
    if not plan.orphaned_live_pins:
        lines.append("_(none)_\n")
    for o in plan.orphaned_live_pins:
        lines.append(f"- [{o['id']}] **{o['title']}** (board `{o.get('board_id')}`)")

    lines.append("\n## UNRESOLVED BOARDS (creates blocked)\n")
    if not plan.unresolved_boards:
        lines.append("_(none)_\n")
    for u in plan.unresolved_boards:
        lines.append(f"- `{u['filename']}`: {u['board_path']} -- {u['reason']}")

    return "\n".join(lines) + "\n"
