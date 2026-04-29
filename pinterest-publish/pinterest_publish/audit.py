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
        json.dumps(asdict(report), indent=2), encoding="utf-8"
    )
    (output_dir / "audit-report.md").write_text(render_audit_md(report), encoding="utf-8")
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
