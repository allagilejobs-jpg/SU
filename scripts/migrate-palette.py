"""
Color palette migration: navy/teal/gold/orange  ->  Purple/Azure/Amber/Pink.

Only touches files that contain the exact navy-gradient signature so we don't
bleed into unrelated dark UI styles. Walks the whole repo, leaves git history
intact, and writes a manifest of every file changed for the renderer to consume.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Files are in scope if they ship ANY legacy palette color (navy, teal, gold,
# orange, green, red, purple-variant, blue) or the new purple palette.
LEGACY_FAMILY = re.compile(
    r"#1a1a2e|#16213e|#0f3460|#0f0f1a|#0a1628|#1a365d"     # navy family
    r"|#4A90A4|#2C5F6E|#3a7a94|#128190"                    # teal family
    r"|#E8B86D|#d4a85d|#D4A84B|#D4A05A|#D4A35A"            # gold family
    r"|#E67E22|#F39C12"                                    # orange family
    r"|#27AE60|#1E8449|#128228|#2ecc71"                    # green family
    r"|#E74C3C|#C0392B"                                    # red family
    r"|#9B59B6|#8e44ad"                                    # purple-variant family
    r"|#3498DB",                                           # blue family
    re.IGNORECASE,
)
NAVY_RGB = re.compile(r"rgb\(\s*26\s*,\s*26\s*,\s*46\s*\)|rgba\(\s*26\s*,\s*26\s*,\s*46")
PURPLE_HEX = re.compile(r"#52008C|#2a004a", re.IGNORECASE)

# ---- Replacements -----------------------------------------------------------
# Order matters: longer / more specific patterns first.
REPLACEMENTS: list[tuple[re.Pattern[str], str]] = [
    # Core navy gradient stops -> Purple gradient
    (re.compile(r"#1a1a2e", re.IGNORECASE), "#2a004a"),
    (re.compile(r"#16213e", re.IGNORECASE), "#52008C"),
    (re.compile(r"#0f3460", re.IGNORECASE), "#3a005f"),
    (re.compile(r"#0f0f1a", re.IGNORECASE), "#1f0033"),  # ultra-dark sibling
    (re.compile(r"#0a1628", re.IGNORECASE), "#1f0033"),  # very-dark navy sibling
    (re.compile(r"#1a365d", re.IGNORECASE), "#3a005f"),  # navy variant -> purple variant

    # Teal accent  -> Vivid Azure
    (re.compile(r"#4A90A4", re.IGNORECASE), "#18A8F1"),
    (re.compile(r"#2C5F6E", re.IGNORECASE), "#0F7BB3"),  # darker teal -> darker azure
    (re.compile(r"#3a7a94", re.IGNORECASE), "#0F7BB3"),  # teal variant
    (re.compile(r"#128190", re.IGNORECASE), "#0F7BB3"),

    # Gold/amber variants  -> Amber
    (re.compile(r"#E8B86D", re.IGNORECASE), "#FDB03E"),
    (re.compile(r"#d4a85d", re.IGNORECASE), "#E59A2A"),  # darker gold hover
    (re.compile(r"#D4A84B", re.IGNORECASE), "#E59A2A"),
    (re.compile(r"#D4A05A", re.IGNORECASE), "#E59A2A"),
    (re.compile(r"#D4A35A", re.IGNORECASE), "#E59A2A"),

    # Orange flavors  -> Amber (alternative)
    (re.compile(r"#E67E22", re.IGNORECASE), "#18A8F1"),  # heading/badge orange -> Azure
    (re.compile(r"#F39C12", re.IGNORECASE), "#FDB03E"),  # flat-UI orange -> Amber

    # Stray semantic colors  -> brand palette
    # (Pinterest brand red #E60023 is INTENTIONALLY excluded — it's the platform color.)
    (re.compile(r"#27AE60", re.IGNORECASE), "#18A8F1"),  # success-green -> Vivid Azure
    (re.compile(r"#1E8449", re.IGNORECASE), "#0F7BB3"),  # darker green -> darker Azure
    (re.compile(r"#128228", re.IGNORECASE), "#0F7BB3"),  # outlier green -> darker Azure
    (re.compile(r"#2ecc71", re.IGNORECASE), "#18A8F1"),  # flat-UI green -> Azure
    (re.compile(r"#E74C3C", re.IGNORECASE), "#CC78CB"),  # alert-red -> Neon Pink
    (re.compile(r"#C0392B", re.IGNORECASE), "#B85FB6"),  # darker red -> darker Pink
    (re.compile(r"#9B59B6", re.IGNORECASE), "#52008C"),  # generic purple -> brand Purple
    (re.compile(r"#8e44ad", re.IGNORECASE), "#3F006D"),  # darker generic purple
    (re.compile(r"#3498DB", re.IGNORECASE), "#18A8F1"),  # flat-UI blue -> Vivid Azure

    # rgba forms (accept any whitespace and alpha)
    (re.compile(r"rgba\(\s*74\s*,\s*144\s*,\s*164\s*,\s*([0-9.]+)\s*\)"),
     r"rgba(24, 168, 241, \1)"),
    (re.compile(r"rgba\(\s*232\s*,\s*184\s*,\s*109\s*,\s*([0-9.]+)\s*\)"),
     r"rgba(253, 176, 62, \1)"),
    (re.compile(r"rgba\(\s*22\s*,\s*33\s*,\s*62\s*,\s*([0-9.]+)\s*\)"),
     r"rgba(82, 0, 140, \1)"),
    (re.compile(r"rgba\(\s*26\s*,\s*26\s*,\s*46\s*,\s*([0-9.]+)\s*\)"),
     r"rgba(42, 0, 74, \1)"),
    (re.compile(r"rgba\(\s*15\s*,\s*52\s*,\s*96\s*,\s*([0-9.]+)\s*\)"),
     r"rgba(58, 0, 95, \1)"),
    # Stray semantic rgba forms
    (re.compile(r"rgba\(\s*39\s*,\s*174\s*,\s*96\s*,\s*([0-9.]+)\s*\)"),
     r"rgba(24, 168, 241, \1)"),  # success-green
    (re.compile(r"rgba\(\s*231\s*,\s*76\s*,\s*60\s*,\s*([0-9.]+)\s*\)"),
     r"rgba(204, 120, 203, \1)"),  # alert-red -> Neon Pink
    (re.compile(r"rgba\(\s*155\s*,\s*89\s*,\s*182\s*,\s*([0-9.]+)\s*\)"),
     r"rgba(82, 0, 140, \1)"),  # generic purple -> brand Purple
    (re.compile(r"rgba\(\s*52\s*,\s*152\s*,\s*219\s*,\s*([0-9.]+)\s*\)"),
     r"rgba(24, 168, 241, \1)"),  # flat-UI blue -> Azure
    (re.compile(r"rgba\(\s*243\s*,\s*156\s*,\s*18\s*,\s*([0-9.]+)\s*\)"),
     r"rgba(253, 176, 62, \1)"),  # flat-UI orange -> Amber
]


def has_signature(text: str) -> bool:
    """In scope when the file uses any legacy palette color or the new purple palette."""
    if PURPLE_HEX.search(text):
        return True
    if LEGACY_FAMILY.search(text):
        return True
    if NAVY_RGB.search(text):
        return True
    return False


def migrate(text: str) -> str:
    new_text = text
    for pattern, replacement in REPLACEMENTS:
        new_text = pattern.sub(replacement, new_text)
    return new_text


def collect_targets(scope: Path) -> list[Path]:
    if scope.is_file():
        return [scope] if scope.suffix.lower() == ".html" else []
    return [p for p in scope.rglob("*.html")
            if "node_modules" not in p.parts
            and ".git" not in p.parts]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", default=str(REPO_ROOT),
                        help="Directory or file to migrate (default: repo root)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--manifest", default=str(REPO_ROOT / "scripts" / "migration-manifest.txt"),
                        help="Where to write the list of changed files (one path per line)")
    args = parser.parse_args()

    scope = Path(args.scope).resolve()
    targets = collect_targets(scope)

    changed: list[Path] = []
    skipped_no_signature = 0
    skipped_no_change = 0

    for path in targets:
        try:
            original = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

        if not has_signature(original):
            skipped_no_signature += 1
            continue

        updated = migrate(original)
        if updated == original:
            skipped_no_change += 1
            continue

        if not args.dry_run:
            path.write_text(updated, encoding="utf-8")
        changed.append(path)

    if not args.dry_run:
        manifest_path = Path(args.manifest)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            "\n".join(str(p.relative_to(REPO_ROOT)) for p in changed) + "\n",
            encoding="utf-8",
        )

    print(f"Scope: {scope}")
    print(f"  HTML files scanned: {len(targets)}")
    print(f"  Skipped (no navy signature): {skipped_no_signature}")
    print(f"  Skipped (signature but no color change): {skipped_no_change}")
    print(f"  {'WOULD CHANGE' if args.dry_run else 'CHANGED'}: {len(changed)}")
    if not args.dry_run:
        print(f"  Manifest: {Path(args.manifest).relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
