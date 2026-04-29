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
