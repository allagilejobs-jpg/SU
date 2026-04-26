"""Find every PNG that doesn't match the canvas size its sibling HTML declares."""
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BODY_RE = re.compile(r"body\s*\{[^}]*?width:\s*(\d+)px;\s*height:\s*(\d+)px", re.DOTALL)
ANY_RE = re.compile(r"\{[^}]*?width:\s*(\d+)px;[^}]*?height:\s*(\d+)px", re.DOTALL)


def detect_size(html_text: str):
    m = BODY_RE.search(html_text)
    if m:
        return int(m.group(1)), int(m.group(2))
    for m in ANY_RE.finditer(html_text):
        w, h = int(m.group(1)), int(m.group(2))
        if w >= 1000 and h >= 1000:
            return w, h
    return None


def png_size(p: Path):
    try:
        data = p.open("rb").read(24)
        if data[:8] != b"\x89PNG\r\n\x1a\n":
            return None
        return struct.unpack(">II", data[16:24])
    except OSError:
        return None


mismatches = []
for html_path in ROOT.rglob("*.html"):
    if "node_modules" in html_path.parts or ".git" in html_path.parts:
        continue
    png_path = html_path.with_suffix(".png")
    if not png_path.exists():
        continue
    try:
        text = html_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        continue
    declared = detect_size(text)
    if declared is None:
        continue
    actual = png_size(png_path)
    if actual is None:
        continue
    if declared != actual:
        mismatches.append((html_path.relative_to(ROOT), declared, actual))

print(f"Mismatches: {len(mismatches)}")
for path, declared, actual in mismatches[:15]:
    print(f"  {path}  declared={declared}  actual={actual}")

(ROOT / "scripts" / "wrong-size.txt").write_text(
    "\n".join(str(p) for p, _, _ in mismatches) + "\n",
    encoding="utf-8",
)
print(f"\nWrote scripts/wrong-size.txt with {len(mismatches)} entries.")
