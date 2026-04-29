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
