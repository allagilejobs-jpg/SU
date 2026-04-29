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


def _load_env_file(path: Path) -> None:
    """Minimal .env loader: KEY=VALUE per line, # comments, blank lines OK.

    Existing os.environ values take precedence (so a real shell export wins).
    """
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def main(argv: List[str] | None = None) -> int:
    _load_env_file(config.TOOL_ROOT / ".env")
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

    audit_data = json.loads(config.AUDIT_REPORT_JSON.read_text(encoding="utf-8"))
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

    plan_data = json.loads(config.PUBLISH_PLAN_JSON.read_text(encoding="utf-8"))
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
