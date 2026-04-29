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
