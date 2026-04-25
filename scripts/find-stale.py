"""Find all HTML files whose sibling PNG is older than the HTML (stale PNG)."""
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
stale = []
fresh = 0
for html in ROOT.rglob("*.html"):
    if "node_modules" in html.parts or ".git" in html.parts:
        continue
    png = html.with_suffix(".png")
    if not png.exists():
        continue
    if png.stat().st_mtime < html.stat().st_mtime:
        stale.append(str(html.relative_to(ROOT)))
    else:
        fresh += 1
print(f"Fresh: {fresh}, Stale: {len(stale)}")
(ROOT / "scripts" / "stale-pngs.txt").write_text("\n".join(stale) + "\n", encoding="utf-8")
print("First 10 stale:")
for s in stale[:10]:
    print(f"  {s}")
