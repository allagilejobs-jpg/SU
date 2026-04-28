"""Comprehensive repo audit: find every HTML file still using legacy navy/teal/gold/orange/etc."""
import re
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent

# Hex colors that should NOT be in any post-migration HTML
LEGACY_HEX = {
    "#1a1a2e": "navy bg",
    "#16213e": "navy bg",
    "#0f3460": "navy bg",
    "#0f0f1a": "navy bg dark",
    "#0a1628": "navy bg dark",
    "#1a365d": "navy variant",
    "#4A90A4": "teal accent",
    "#2C5F6E": "darker teal",
    "#3a7a94": "teal variant",
    "#128190": "teal variant",
    "#E8B86D": "gold",
    "#d4a85d": "darker gold",
    "#D4A84B": "darker gold",
    "#D4A05A": "gold variant",
    "#D4A35A": "gold variant",
    "#E67E22": "orange",
    "#F39C12": "flat-UI orange",
    "#27AE60": "success green",
    "#1E8449": "darker green",
    "#128228": "green variant",
    "#2ecc71": "flat-UI green",
    "#E74C3C": "alert red",
    "#C0392B": "darker red",
    "#9B59B6": "generic purple",
    "#3498DB": "flat-UI blue",
}

# Build case-insensitive regex
LEGACY_RE = re.compile(
    "|".join(re.escape(h) for h in LEGACY_HEX.keys()),
    re.IGNORECASE,
)

per_file = defaultdict(list)
per_dir = defaultdict(int)

for html in ROOT.rglob("*.html"):
    if "node_modules" in html.parts or ".git" in html.parts:
        continue
    try:
        text = html.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        continue
    hits = LEGACY_RE.findall(text)
    if hits:
        rel = html.relative_to(ROOT)
        per_file[str(rel)] = hits
        # Top-level dir bucket
        parts = rel.parts
        if len(parts) >= 2 and parts[0] in ("content", "leadmagnet", "tiktok"):
            per_dir[f"{parts[0]}/{parts[1]}"] += 1
        else:
            per_dir[parts[0]] += 1

print(f"Files with legacy colors: {len(per_file)}\n")
print("By directory:")
for d, count in sorted(per_dir.items(), key=lambda x: -x[1])[:25]:
    print(f"  {count:4d}  {d}")

# Write to manifest for migration
(ROOT / "scripts" / "legacy-color-files.txt").write_text(
    "\n".join(sorted(per_file.keys())) + "\n",
    encoding="utf-8",
)
print(f"\nWrote scripts/legacy-color-files.txt with {len(per_file)} entries")

# Show sample files
print("\nSample files with legacy colors:")
for f in sorted(per_file.keys())[:8]:
    hits = per_file[f]
    summary = ", ".join(f"{c}×{hits.count(c)}" for c in sorted(set(hits)))
    print(f"  {f}: {summary}")
