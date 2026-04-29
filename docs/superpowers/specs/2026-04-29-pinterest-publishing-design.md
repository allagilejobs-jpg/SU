# Pinterest publishing pipeline — design spec

**Date:** 2026-04-29
**Status:** Approved (awaiting implementation plan)
**Phase:** 1 of 2 (publishes the 25 polished pins from `content/pinterest/`; Phase 2 — curating new pins from the 131 daily-content folders — is a separate future effort)

## Goal

Build a small Python CLI that publishes the 25 polished Pinterest pins from `content/pinterest/` to the Spectrum Unlocked Pinterest account via the Pinterest v5 REST API.

The current Pinterest account already has older versions of these pins live, built with the previous navy/teal/gold palette. The new pins use the current Pink/Azure/Amber/Purple brand palette. The tool replaces (delete + recreate) old pins with the new-palette versions in a single coordinated sweep.

## Out of scope (Phase 1)

- Curating/polishing the ~131 daily-content folders into Pinterest pins (Phase 2).
- Scheduled future publishing.
- Analytics polling.
- Any UI — pure CLI.

## Constraints and inputs

- **Pinterest app:** Spectrum Unlocked OAuth app, trial-tier access. App ID + secret stored locally in `pinterest-publish/.env` (gitignored), never committed.
- **Auth model:** OAuth 2.0 authorization-code flow using `client_id` + `client_secret`. Required scopes: `pins:read`, `pins:write`, `boards:read`. Add `boards:write` only if `--create-missing` is invoked.
- **Rate limits:** Pinterest trial tier historically caps creation at ~5 pins/day; full sweep of 25 expected to take ~5 calendar days.
- **Image format:** all 25 source PNGs are 1000×1500 (Pinterest's recommended 2:3 ratio). Parser rejects mismatched dimensions.

## Architecture — 4-stage CLI

```
auth   →   audit   →   plan   →   apply
```

Each stage writes reviewable artifacts so the operator can pause, inspect, and re-run between any two stages. Nothing destructive happens without explicit confirmation.

| Stage | What it does | Output |
|---|---|---|
| **`auth`** | One-time browser OAuth flow. Spawns local HTTP server on `:8080`, opens browser, captures `code`, exchanges for `access_token` + `refresh_token`. Auto-refreshes silently on subsequent runs. | `state/.pinterest-token.json` |
| **`audit`** | Read-only. Lists boards, sections, and every existing pin (title, image URL, board, stats). | `state/audit-report.json` + `audit-report.md` |
| **`plan`** | Cross-references audit with repo pins. Per pin, decides delete + create actions. Surfaces unresolvable cases (missing boards, orphaned live pins). | `state/publish-plan.json` + `publish-plan.md` |
| **`apply`** | Executes the plan. Supports `--dry-run`, `--max-creates N`, `--create-missing`, `--yes`. Confirms before destructive actions. Logs every API call to append-only `apply-log.jsonl`. Re-runnable: skips already-completed actions. | `state/apply-log.jsonl` |

## Source data and URL mapping

Three sources combined at parse time:

1. **`content/pinterest/PINTEREST-POSTS.md`** — already contains, for each pin, title + description + board path (e.g. `Autism Parenting Tips / IEP & School Advocacy`). Parser walks the existing `## N. <Topic>` headers.
2. **`content/pinterest/pin-XX-*.png`** — the image files. Filename is the join key.
3. **`pinterest-publish/url-map.yaml`** — *new file* in this project, committed to git, the editable source of truth for per-pin destination URLs.

### `url-map.yaml` shape

```yaml
default: "https://www.spectrumunlocked.com/"

pins:
  pin-01-iep-accommodations.png:    "https://www.spectrumunlocked.com/blog/iep-rights-schools-wont-tell-you"
  pin-02-meltdown-vs-tantrum.png:   "https://www.spectrumunlocked.com/blog/autism-meltdown-vs-tantrum"
  pin-03-sensory-hacks.png:         "https://www.spectrumunlocked.com/blog/sensory-diet-beginners-guide"
  pin-04-sleep-strategies.png:      "https://www.spectrumunlocked.com/blog/autism-sleep-strategies"
  pin-06-potty-training.png:        "https://www.spectrumunlocked.com/blog/autism-potty-training-readiness-guide"
  pin-09-aac-communication.png:     "https://www.spectrumunlocked.com/blog/aac-for-beginners"
  pin-11-5-things-diagnosis.png:    "https://www.spectrumunlocked.com/blog/diagnosed-now-what"
  pin-12-visual-supports.png:       "https://www.spectrumunlocked.com/blog/visual-schedule-guide"
  pin-13-self-care-parents.png:     "https://www.spectrumunlocked.com/blog/self-care-autism-parents"
  pin-14-glass-child.png:           "https://www.spectrumunlocked.com/blog/autism-sibling-support"
  pin-15-autistic-burnout.png:      "https://www.spectrumunlocked.com/blog/autism-parent-burnout"
  pin-17-acceptance-vs-awareness.png: "https://www.spectrumunlocked.com/blog/autism-acceptance-month-2026"
  pin-19-feeding-challenges.png:    "https://www.spectrumunlocked.com/blog/autism-picky-eating"
  pin-20-autism-teens.png:          "https://www.spectrumunlocked.com/start-here/parents-of-teens"
  pin-24-school-accommodations.png: "https://www.spectrumunlocked.com/blog/first-iep-meeting-checklist"
  pin-25-aba-controversy.png:       "https://www.spectrumunlocked.com/blog/autism-therapy-types-explained"
  # Pins not listed (5, 7, 8, 10, 16, 18, 21, 22, 23) fall through to `default`.

aliases:
  # If a live pin's title was edited on Pinterest after creation, list the
  # current live title here to map it back to the repo filename.
  # Empty by default.
```

### Internal pin record shape

```python
{
  "filename":     "pin-01-iep-accommodations.png",
  "image_path":   "content/pinterest/pin-01-iep-accommodations.png",
  "title":        "Neurodiversity-Affirming IEP Accommodations",
  "description":  "Your child's IEP shouldn't teach them to mask. ...",
  "board_path":   "Autism Parenting Tips / IEP & School Advocacy",
  "link":         "https://www.spectrumunlocked.com/blog/iep-rights-schools-wont-tell-you",
}
```

### Parser validation (fail loud)

- Every PNG referenced in `PINTEREST-POSTS.md` must exist on disk.
- Every record must have title + description + board_path.
- Image dimensions must be 1000×1500 (parser rejects mismatches via Pillow).
- Title ≤ 100 chars; description ≤ 500 chars; link must be valid HTTPS URL.

## Plan and apply semantics

### Matching old pins to repo pins

Match **by exact title** (the title from `PINTEREST-POSTS.md`). The `aliases` block in `url-map.yaml` handles the rare case of titles edited on Pinterest after creation. The `plan` stage prints a section called **"Live pins with no repo match"** so the operator can spot-check before applying.

### Board mapping (audit feeds this)

After `audit` runs, `plan` resolves each repo `board_path` against live boards/sections. Three possible outcomes per pin:

- **Resolved cleanly** — exact board + section name match → use those IDs.
- **Fuzzy match candidate** — board matches but section name differs slightly → flagged in plan with the candidate; operator approves before apply.
- **Unresolved** — no board found → plan lists under "Pins blocked on missing boards." Operator can: (a) re-run apply with `--create-missing` (creates boards/sections on-the-fly, requires `boards:write` scope), (b) edit repo metadata, or (c) create boards manually in Pinterest UI then re-audit.

**Default behavior: never auto-create boards/sections.** Opt-in only.

### Concrete plan output (`publish-plan.md`)

```markdown
# Pinterest publish plan — generated 2026-04-29

## Summary
- 25 repo pins, 18 live pins, 17 title matches, 1 live pin orphaned
- 17 deletes + 25 creates planned, 0 unresolved boards

## DELETE (live pins flagged for removal)
1. [pin_id 12345] "Meltdown vs Tantrum: Know the Difference"
   board:  Autism Parenting Tips › Meltdown Support
   stats:  saves 4, impressions 312
2. ...

## CREATE (new pins from repo)
1. pin-01-iep-accommodations.png  →  Autism Parenting Tips › IEP & School Advocacy
   title:  Neurodiversity-Affirming IEP Accommodations
   link:   https://www.spectrumunlocked.com/blog/iep-rights-schools-wont-tell-you
2. ...

## ORPHANED LIVE PINS (no repo match — left untouched)
- [pin_id 99988] "Old Stuff" (probably edited title — review manually)
```

### Apply behavior

- **`--dry-run`** prints every API call without sending.
- **Confirmation prompt** before destructive actions: shows count + total saves/impressions about to be lost; requires typing `yes` to proceed (`--yes` to bypass; documented but discouraged).
- **Order:** deletes first, then creates.
- **`--max-creates N`** caps creates this run for deliberate pacing.
- **`--create-missing`** opts into auto-creating missing boards/sections.
- **Image upload:** base64-encoded inline (`image_base64` field on `POST /v5/pins`). PNGs are ~100–200KB, well under Pinterest's 32MB limit.
- **Append-only `state/apply-log.jsonl`** — one line per API call: timestamp, action, request, response, stable `repo_pin_id`. Re-runs read this log and skip completed actions.

### Rate limit handling

- Tracks creates per UTC day from the log.
- HTTP 429 → exponential backoff up to 60s.
- If still capped after backoff, **exits cleanly with a "resume tomorrow" message**.
- Deletes and creates accounted separately (deletes typically aren't rate-limited the same way).

## Project structure

```
pinterest-publish/
├── README.md                       # how to run, troubleshooting
├── url-map.yaml                    # pin → destination URL (committed)
├── pyproject.toml                  # deps: requests, pyyaml, pillow
├── pinterest_publish/
│   ├── __init__.py
│   ├── cli.py                      # argparse entry: auth/audit/plan/apply
│   ├── config.py                   # constants: API base, scopes, paths
│   ├── auth.py                     # OAuth flow + token refresh
│   ├── api.py                      # thin Pinterest REST wrapper
│   ├── parser.py                   # PINTEREST-POSTS.md → pin records
│   ├── url_mapper.py               # url-map.yaml lookup with default fallback
│   ├── audit.py                    # GET boards/sections/pins → reports
│   ├── plan.py                     # cross-reference, build delete+create plan
│   └── apply.py                    # execute plan, log, rate-limit, resume
├── state/                          # gitignored; created at runtime
│   ├── .pinterest-token.json
│   ├── audit-report.{json,md}
│   ├── publish-plan.{json,md}
│   └── apply-log.jsonl
└── tests/
    ├── test_parser.py
    ├── test_url_mapper.py
    ├── test_plan.py
    └── fixtures/
        ├── sample-PINTEREST-POSTS.md
        └── sample-audit.json
```

## OAuth flow

One-time setup (documented in `pinterest-publish/README.md`):

1. In the Pinterest dev console, add `http://localhost:8080/callback` to the app's redirect URIs.
2. Set env vars (or paste into `pinterest-publish/.env`, gitignored):
   ```
   PINTEREST_CLIENT_ID=<your-app-id>
   PINTEREST_CLIENT_SECRET=<your-app-secret>
   ```
3. Run `python -m pinterest_publish auth`.

What `auth` does:

- Spawns local HTTP server on `:8080` listening at `/callback`.
- Opens browser to Pinterest's OAuth URL with `scope=pins:read,pins:write,boards:read` (plus `boards:write` if needed).
- Pinterest redirects to `localhost:8080/callback?code=...`.
- Local server captures `code`, exchanges at `POST /v5/oauth/token` for `access_token` + `refresh_token`, writes both to `state/.pinterest-token.json`, prints success, exits.

On every subsequent run, `auth.py` reads the token file. Pinterest access tokens last ~30 days; refresh tokens last ~365 days. If `access_token` is expired, the tool auto-refreshes silently and updates the file.

## `.gitignore` additions

```
# Pinterest publishing — local secrets and state
pinterest-publish/state/
pinterest-publish/.env
```

## Testing strategy

**Unit tests (no network):**

- `test_parser.py` — fixture `PINTEREST-POSTS.md` parses to expected records; malformed inputs fail loud.
- `test_url_mapper.py` — exact match wins, falls back to `default`, raises on missing default, alias resolution works.
- `test_plan.py` — given fixture audit + repo records, produces expected plan. Cases: clean match, fuzzy section, missing board, orphaned live pin, alias-resolved title mismatch.

**Integration (Pinterest sandbox):**

- The Pinterest dev console offers a Sandbox environment. CLI takes `--env sandbox|production` (default production).
- One end-to-end sandbox test: `audit → plan → apply --dry-run` to verify wire-format correctness before any production run.

**Manual checklist (in README):**

1. Run `auth` once.
2. Run `audit`, eyeball `audit-report.md`.
3. Run `plan`, eyeball `publish-plan.md`.
4. Run `apply --dry-run` against production, eyeball log.
5. Run `apply --max-creates 1` against production for the first real pin, verify it appears on Pinterest correctly.
6. Then full `apply` (will pace itself across days under trial-tier cap).

## Operational guidelines

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
- Don't ship pins where the image isn't 1000×1500 — Pinterest accepts other ratios but truncates oddly. The parser will reject mismatched dimensions.

### Pinterest API content limits (enforced at parse time)

- Title ≤ 100 chars
- Description ≤ 500 chars
- Link: valid HTTPS URL

### Trial-tier reality

- ~5 pin creates/day expected; full 25-pin sweep ≈ 5 calendar days.
- Deletes don't count against the create cap.
- If access is upgraded to Standard later, the tool keeps working — sweep finishes faster.

## Pin → URL mapping reference

Strong matches (16):

| # | Pin | URL |
|---|---|---|
| 1 | IEP Accommodations | `/blog/iep-rights-schools-wont-tell-you` |
| 2 | Meltdown vs Tantrum | `/blog/autism-meltdown-vs-tantrum` |
| 3 | 5 Sensory Hacks | `/blog/sensory-diet-beginners-guide` |
| 4 | Sleep Strategies | `/blog/autism-sleep-strategies` |
| 6 | Potty Training | `/blog/autism-potty-training-readiness-guide` |
| 9 | AAC Communication | `/blog/aac-for-beginners` |
| 11 | 5 Things After Diagnosis | `/blog/diagnosed-now-what` |
| 12 | Visual Supports | `/blog/visual-schedule-guide` |
| 13 | Self-Care for Parents | `/blog/self-care-autism-parents` |
| 14 | Glass Child / Siblings | `/blog/autism-sibling-support` |
| 15 | Autistic Burnout | `/blog/autism-parent-burnout` (close-but-not-perfect; explicitly accepted) |
| 17 | Acceptance vs Awareness | `/blog/autism-acceptance-month-2026` |
| 19 | Feeding Challenges | `/blog/autism-picky-eating` |
| 20 | Autism in Teens | `/start-here/parents-of-teens` |
| 24 | School Accommodations | `/blog/first-iep-meeting-checklist` |
| 25 | ABA Controversy | `/blog/autism-therapy-types-explained` |

Falling through to homepage default (9): #5 Signs of Masking, #7 AuDHD, #8 Autism in Girls, #10 Autism & Anxiety, #16 5 Autism Myths, #18 Late-Diagnosed Autism, #21 Travel with Autistic Child, #22 Summer Camps, #23 Building Friendships.

When matching blog posts are written on spectrumunlocked.com later, just add lines to `url-map.yaml` and re-run `plan` + `apply` for an update sweep.
