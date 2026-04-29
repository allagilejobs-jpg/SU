# pinterest-publish

Tool for publishing Spectrum Unlocked Pinterest pins from `content/pinterest/` to Pinterest via the v5 API. Replaces existing old-palette pins with the new-palette versions in a single coordinated sweep.

## One-time setup

1. Add `http://localhost:8080/callback` as a redirect URI in your Pinterest developer console for the "Spectrum Unlocked" app.
2. Set credentials (env vars OR a gitignored `pinterest-publish/.env`):
   ```
   PINTEREST_CLIENT_ID=1565261
   PINTEREST_CLIENT_SECRET=<from-dev-console>
   ```
3. Install:
   ```bash
   cd pinterest-publish && pip install -e ".[dev]"
   ```
4. Run the OAuth flow once:
   ```bash
   python -m pinterest_publish auth
   ```
   Browser opens, you authorize, the tool captures the token.

## Daily workflow

```bash
# 1. Read-only: see what's on Pinterest now
python -m pinterest_publish audit
less state/audit-report.md

# 2. Build the action plan from repo + audit
python -m pinterest_publish plan
less state/publish-plan.md

# 3. Dry-run apply to confirm what will happen
python -m pinterest_publish apply --dry-run

# 4. Real run, paced (good for first time)
python -m pinterest_publish apply --max-creates 1

# 5. Subsequent days — pick up where it left off
python -m pinterest_publish apply
```

## Safeguards (read this before running `apply`)

### DO

- Run `audit` and review `audit-report.md` before every `plan`.
- Run `plan` and review `publish-plan.md` before every `apply`.
- Run `apply --dry-run` the first time, always.
- Commit changes to `url-map.yaml` (it's the source of truth for destinations).
- Back up `state/apply-log.jsonl` before any re-run that involves manual edits to the log.
- Keep `content/pinterest/PINTEREST-POSTS.md` titles stable once a pin is published — changing them later breaks dedup.

### DON'T

- Don't commit `state/.pinterest-token.json` (gitignored, but worth saying out loud — it grants pin write access to your account).
- Don't manually edit pin titles **on Pinterest itself** — use the `aliases:` mechanism in `url-map.yaml` instead.
- Don't run `apply` in two terminals at once (log races, possible double-creates).
- Don't bypass the confirmation prompt with `--yes` unless you've verified the plan in dry-run first.
- Don't ship pins where the image isn't 1000×1500 — the parser will reject mismatched dimensions.

### Pinterest content limits (enforced at parse time)

- Title ≤ 100 chars
- Description ≤ 500 chars
- Link: valid HTTPS URL

### Trial-tier reality

- ~5 pin creates/day expected; full 25-pin sweep ≈ 5 calendar days.
- Deletes don't count against the create cap.
- The append-only log makes resuming painless: each day, just re-run `apply` and it picks up where it left off.

## Sandbox

The Pinterest dev console offers a Sandbox environment. Pass `--env sandbox` to any subcommand to use it (e.g., for first-time wire-format verification):
```bash
python -m pinterest_publish --env sandbox audit
```

## Files

```
pinterest-publish/
├── README.md          # this file
├── url-map.yaml       # pin → destination URL (committed)
├── pyproject.toml     # deps + entry point
├── pinterest_publish/ # source
├── state/             # gitignored runtime artifacts
│   ├── .pinterest-token.json
│   ├── audit-report.{json,md}
│   ├── publish-plan.{json,md}
│   └── apply-log.jsonl
└── tests/             # unit tests
```

See `docs/superpowers/specs/2026-04-29-pinterest-publishing-design.md` for the full design and `docs/superpowers/plans/2026-04-29-pinterest-publishing.md` for the implementation plan.
