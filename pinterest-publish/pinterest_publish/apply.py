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

    # Creates first — keep old pins live until new ones are confirmed up.
    # If creates fail or hit the rate cap, deletes are skipped this run and
    # picked up next time once all creates have logged successfully.
    creates_done = 0
    cap = options.max_creates if options.max_creates is not None else len(plan.creates)
    creates_remaining = False
    for c in plan.creates:
        if creates_done >= cap:
            print(f"max-creates cap reached ({cap}) — stopping before deletes")
            creates_remaining = True
            break
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

    # Only run deletes once every planned create has logged ok=True.
    # This way the old pin stays live until its replacement is confirmed.
    pending_creates = [
        c for c in plan.creates if not log.already_done("create", c["filename"])
    ]
    if pending_creates or creates_remaining:
        print(
            f"holding {len(plan.deletes)} deletes — {len(pending_creates)} creates "
            f"still pending. Re-run apply after creates complete."
        )
        return

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
    print("Order: creates first, then deletes (only if all creates have logged ok).\n")
    cap = options.max_creates if options.max_creates is not None else len(plan.creates)
    print(f"Would create {min(cap, len(plan.creates))} of {len(plan.creates)} pins:")
    for c in plan.creates[:cap]:
        print(f"  CREATE {c['filename']} -> board={c['board_id']} section={c.get('board_section_id')}")
        print(f"    title: {c['title']}")
        print(f"    link:  {c['link']}")
    if cap < len(plan.creates):
        print(f"  ({len(plan.creates) - cap} more pins capped by --max-creates)")
    print(f"\nWould delete {len(plan.deletes)} pins (only after all creates complete):")
    for d in plan.deletes:
        print(f"  DELETE [{d['id']}] {d.get('title','')}")
