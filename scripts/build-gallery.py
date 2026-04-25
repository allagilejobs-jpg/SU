"""
Build a one-page browse + download gallery of every PNG that pairs with a
migrated HTML file. Reads the migration manifest, groups by top-level
directory, lazy-loads thumbnails, and gives each card a Download link.
"""

from __future__ import annotations

import html
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST = REPO_ROOT / "scripts" / "migration-manifest.txt"
# Beacon W1 was migrated separately (manifest got overwritten); add manually.
BEACON_W1_DIRS = [
    "content/beacon-week1-start-here",
    "content/beacon-week1-5-things",
    "content/beacon-week1-iep-checklist",
    "content/beacon-week1-meltdown",
]
OUTPUT = REPO_ROOT / "brand-update-gallery.html"


def collect_pngs() -> list[Path]:
    paths: list[Path] = []
    seen: set[Path] = set()

    if MANIFEST.exists():
        for line in MANIFEST.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            html_path = REPO_ROOT / line.strip()
            png_path = html_path.with_suffix(".png")
            if png_path.exists() and png_path not in seen:
                paths.append(png_path)
                seen.add(png_path)

    for d in BEACON_W1_DIRS:
        for png_path in (REPO_ROOT / d).glob("*.png"):
            if png_path not in seen:
                paths.append(png_path)
                seen.add(png_path)

    return sorted(paths)


def group_label(rel: Path) -> tuple[str, str]:
    """Return (group_key, display_name) for a relative path."""
    parts = rel.parts
    if len(parts) == 1:
        return "_root", "Repo root"
    top = parts[0]
    if top == "content" and len(parts) >= 2:
        sub = parts[1]
        # Bucket day-XX content together for sanity
        if sub.startswith("day-"):
            return "content/day-XX", "Content — daily posts (day-XX)"
        if sub.startswith("beacon-week1-"):
            return "content/beacon-week1", "Content — Beacon Week 1"
        if sub == "curated" and len(parts) >= 3:
            return "content/curated", "Content — curated artists"
        return f"content/{sub}", f"Content — {sub}"
    if top == "tiktok":
        if len(parts) >= 2:
            return f"tiktok/{parts[1]}", f"TikTok — {parts[1]}"
        return "tiktok", "TikTok"
    if top in ("reel-dontsay", "reel-famous", "reel-signs"):
        return top, f"Reel — {top.replace('reel-', '')}"
    if top == "sensory-hacks":
        return "sensory-hacks", "Sensory hacks"
    if top == "graphics":
        return "graphics", "Graphics (templates)"
    if top == "weekly-ideas":
        return "weekly-ideas", "Weekly ideas"
    return top, top


def build() -> None:
    pngs = collect_pngs()
    groups: dict[str, list[Path]] = defaultdict(list)
    labels: dict[str, str] = {}

    for png in pngs:
        rel = png.relative_to(REPO_ROOT)
        key, label = group_label(rel)
        groups[key].append(png)
        labels[key] = label

    # Stable sort: Beacon first, then content, then everything else
    def group_sort_key(k: str) -> tuple[int, str]:
        if k == "content/beacon-week1":
            return (0, k)
        if k.startswith("content/"):
            return (1, k)
        if k.startswith("tiktok"):
            return (3, k)
        if k.startswith("reel-"):
            return (2, k)
        return (4, k)

    sorted_keys = sorted(groups.keys(), key=group_sort_key)

    css = """
      * { box-sizing: border-box; margin: 0; padding: 0; }
      body { font-family: 'Poppins', system-ui, sans-serif; background: #f4f4f8; color: #1a1a2e; padding: 40px 20px 80px; }
      header { max-width: 1400px; margin: 0 auto 28px; }
      h1 { font-family: 'Playfair Display', Georgia, serif; font-size: 38px; color: #52008C; margin-bottom: 6px; }
      header p { color: #444; font-size: 14px; line-height: 1.6; max-width: 820px; }
      .toc { max-width: 1400px; margin: 24px auto 40px; background: #fff; border-radius: 14px; padding: 18px 22px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
      .toc h2 { font-size: 14px; text-transform: uppercase; letter-spacing: 2px; color: #52008C; margin-bottom: 10px; }
      .toc ul { list-style: none; display: flex; flex-wrap: wrap; gap: 6px 14px; }
      .toc a { color: #18A8F1; text-decoration: none; font-size: 13px; font-weight: 600; padding: 4px 10px; border-radius: 16px; background: rgba(24,168,241,0.1); }
      .toc a:hover { background: rgba(24,168,241,0.22); }
      .group { max-width: 1400px; margin: 0 auto 50px; background: #fff; border-radius: 14px; padding: 22px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); scroll-margin-top: 20px; }
      .group h2 { font-family: 'Playfair Display', Georgia, serif; font-size: 22px; color: #52008C; margin-bottom: 4px; }
      .group .count { color: #888; font-size: 13px; margin-bottom: 16px; }
      .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 14px; }
      .card { background: #fafafd; border: 1px solid #e7e7ee; border-radius: 10px; overflow: hidden; display: flex; flex-direction: column; }
      .card a.preview { display: block; aspect-ratio: 4/5; background: #2a004a; overflow: hidden; }
      .card img { width: 100%; height: 100%; object-fit: cover; display: block; }
      .meta { padding: 8px 10px 10px; font-size: 11px; color: #555; line-height: 1.45; word-break: break-all; }
      .meta .name { font-weight: 600; color: #1a1a2e; margin-bottom: 4px; }
      .meta a.dl { color: #18A8F1; text-decoration: none; font-weight: 600; }
      .meta a.dl:hover { text-decoration: underline; }
    """

    parts: list[str] = []
    parts.append("<!DOCTYPE html>")
    parts.append("<html lang='en'><head><meta charset='UTF-8'>")
    parts.append("<title>Brand-Update Gallery — Spectrum Unlocked</title>")
    parts.append("<link href='https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&family=Playfair+Display:wght@700&display=swap' rel='stylesheet'>")
    parts.append(f"<style>{css}</style></head><body>")

    parts.append("<header>")
    parts.append("<h1>Brand-Update Gallery</h1>")
    parts.append(
        "<p>Every PNG re-rendered on the new palette (Pink / Azure / Amber / Purple). Click any thumbnail "
        "to view full-size, or hit Download to save. Originals stayed in git history if you ever need to roll back.</p>"
    )
    parts.append(f"<p style='margin-top:8px;color:#888;font-size:12px;'>Total assets: {len(pngs)} · Generated from migration-manifest.txt + Beacon Week 1.</p>")
    parts.append("</header>")

    parts.append("<nav class='toc'><h2>Jump to</h2><ul>")
    for key in sorted_keys:
        anchor = key.replace("/", "-")
        parts.append(f"<li><a href='#{anchor}'>{html.escape(labels[key])} ({len(groups[key])})</a></li>")
    parts.append("</ul></nav>")

    for key in sorted_keys:
        anchor = key.replace("/", "-")
        parts.append(f"<section class='group' id='{anchor}'>")
        parts.append(f"<h2>{html.escape(labels[key])}</h2>")
        parts.append(f"<div class='count'>{len(groups[key])} files</div>")
        parts.append("<div class='grid'>")
        for png in sorted(groups[key]):
            rel = png.relative_to(REPO_ROOT)
            url = str(rel).replace("\\", "/")
            display_name = png.name
            parent = str(rel.parent).replace("\\", "/") if rel.parent != Path(".") else ""
            parts.append("<div class='card'>")
            parts.append(f"<a class='preview' href='{html.escape(url)}' target='_blank' rel='noopener'>")
            parts.append(f"<img loading='lazy' src='{html.escape(url)}' alt='{html.escape(display_name)}'>")
            parts.append("</a>")
            parts.append("<div class='meta'>")
            parts.append(f"<div class='name'>{html.escape(display_name)}</div>")
            if parent:
                parts.append(f"<div style='color:#999;font-size:10px;margin-bottom:4px'>{html.escape(parent)}</div>")
            parts.append(f"<a class='dl' href='{html.escape(url)}' download>Download ↓</a>")
            parts.append("</div></div>")
        parts.append("</div></section>")

    parts.append("</body></html>")

    OUTPUT.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(REPO_ROOT)} with {len(pngs)} assets across {len(groups)} groups.")


if __name__ == "__main__":
    build()
