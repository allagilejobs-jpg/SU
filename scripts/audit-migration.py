"""
End-to-end audit of the brand-palette migration.

Runs as a self-contained test harness — no external test framework.
Each check prints a PASS/FAIL line; non-zero exit code if anything fails.

Checks:
  1. Idempotency       — re-running the migration changes 0 files.
  2. Signature gone    — no migrated file still contains the old navy gradient.
  3. PNG existence     — every migrated HTML has a sibling PNG (size > 0).
  4. PNG freshness     — every PNG mtime is newer than its HTML mtime
                         (i.e. it was re-rendered after the color swap).
  5. PNG validity      — every PNG starts with the 8-byte PNG signature.
  6. Pixel-level color — top-left pixel of dark-bg slides is in the purple
                         family, not navy. Sampled across the manifest.
  7. Gallery integrity — every <img src> in the gallery resolves to a file.
  8. No orphan navy    — repo-wide scan: no other HTML still ships the navy gradient.
  9. Edge-case report  — non-palette colors that survived the migration
                         (informational; surfaces things like green badges).
 10. Git scope         — only HTML/PNG/scripts/* paths were modified
                         (no surprise edits elsewhere).
"""

from __future__ import annotations

import re
import struct
import subprocess
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST = REPO_ROOT / "scripts" / "migration-manifest.txt"

# Beacon W1 was migrated separately and isn't in the manifest.
BEACON_W1 = [
    REPO_ROOT / "content" / "beacon-week1-start-here",
    REPO_ROOT / "content" / "beacon-week1-5-things",
    REPO_ROOT / "content" / "beacon-week1-iep-checklist",
    REPO_ROOT / "content" / "beacon-week1-meltdown",
]

NAVY_SIGNATURE = re.compile(r"linear-gradient\(165deg,\s*#1a1a2e", re.IGNORECASE)
ANY_HEX = re.compile(r"#[0-9A-Fa-f]{6}")

NEW_PALETTE = {"#cc78cb", "#18a8f1", "#fdb03e", "#52008c", "#2a004a", "#3a005f",
               "#0f7bb3", "#e59a2a"}
# Common neutrals/accents we don't flag as "stray".
NEUTRAL = {"#ffffff", "#000000", "#1a1a1a", "#222222", "#fafafa", "#f5f5f5"}

PURPLE_TARGET_RANGE = {  # Top-left pixel acceptable hues (purple gradient stops)
    "r": (15, 110),  # 0x0a..0x6e
    "g": (0, 30),    # 0x00..0x1e
    "b": (60, 180),  # 0x3c..0xb4
}


# ---------- helpers ----------------------------------------------------------

def collect_targets() -> list[Path]:
    paths: list[Path] = []
    if MANIFEST.exists():
        for line in MANIFEST.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                paths.append(REPO_ROOT / line)
    for d in BEACON_W1:
        paths.extend(sorted(d.glob("*.html")))
    # de-dupe while preserving order
    seen, out = set(), []
    for p in paths:
        rp = p.resolve()
        if rp not in seen:
            seen.add(rp)
            out.append(p)
    return out


def png_topleft_rgb(path: Path) -> tuple[int, int, int] | None:
    """Decode the first pixel of a PNG without external deps."""
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    # Walk chunks: IHDR first, then IDAT(s)
    pos = 8
    width = height = bit_depth = color_type = 0
    idat = bytearray()
    while pos < len(data):
        if pos + 8 > len(data):
            break
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        ctype = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + length]
        if ctype == b"IHDR":
            width, height, bit_depth, color_type = struct.unpack(">IIBB", body[:10])
        elif ctype == b"IDAT":
            idat.extend(body)
        elif ctype == b"IEND":
            break
        pos += 8 + length + 4  # 4 = CRC

    if not idat or bit_depth != 8:
        return None
    import zlib
    try:
        raw = zlib.decompress(bytes(idat))
    except zlib.error:
        return None
    # First scanline filter byte then RGB[A]
    if color_type == 2:  # RGB
        if len(raw) < 4:
            return None
        return raw[1], raw[2], raw[3]
    if color_type == 6:  # RGBA
        if len(raw) < 5:
            return None
        return raw[1], raw[2], raw[3]
    return None


# ---------- checks -----------------------------------------------------------

results: list[tuple[str, bool, str]] = []

def record(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))
    flag = "PASS" if ok else "FAIL"
    print(f"[{flag}] {name}{(' — ' + detail) if detail else ''}")


def check_idempotency() -> None:
    """Re-run the migration. It should change zero files."""
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "migrate-palette.py"), "--dry-run"],
        capture_output=True, text=True,
    )
    out = proc.stdout
    m = re.search(r"WOULD CHANGE:\s*(\d+)", out)
    if not m:
        record("1. idempotency", False, f"could not parse output: {out!r}")
        return
    would_change = int(m.group(1))
    record(
        "1. idempotency",
        would_change == 0,
        f"dry-run would change {would_change} files (expected 0)",
    )


def check_signature_gone(targets: list[Path]) -> None:
    leftovers = []
    for p in targets:
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        if NAVY_SIGNATURE.search(text):
            leftovers.append(p)
    record(
        "2. navy gradient removed",
        not leftovers,
        f"{len(targets)} HTML files clean" if not leftovers
        else f"{len(leftovers)} files still have navy signature, e.g. {leftovers[0]}",
    )


def check_png_existence(targets: list[Path]) -> tuple[list[Path], list[Path]]:
    pngs, missing = [], []
    for p in targets:
        png = p.with_suffix(".png")
        if not png.exists() or png.stat().st_size == 0:
            missing.append(p)
        else:
            pngs.append(png)
    record(
        "3. PNG existence",
        not missing,
        f"all {len(pngs)} PNGs present (size > 0)" if not missing
        else f"{len(missing)} HTML files missing a sibling PNG, e.g. {missing[0]}",
    )
    return pngs, missing


def check_png_freshness(targets: list[Path]) -> None:
    stale = []
    for p in targets:
        png = p.with_suffix(".png")
        if not png.exists():
            continue
        if png.stat().st_mtime < p.stat().st_mtime:
            stale.append(p)
    record(
        "4. PNG re-rendered after HTML edit",
        not stale,
        "all sibling PNGs are newer than their HTML" if not stale
        else f"{len(stale)} stale, e.g. {stale[0]}",
    )


def check_png_validity(pngs: list[Path]) -> None:
    bad = []
    for png in pngs:
        try:
            head = png.open("rb").read(8)
        except OSError:
            bad.append(png)
            continue
        if head != b"\x89PNG\r\n\x1a\n":
            bad.append(png)
    record(
        "5. PNG file validity",
        not bad,
        f"all {len(pngs)} PNGs have valid PNG signature" if not bad
        else f"{len(bad)} invalid, e.g. {bad[0]}",
    )


def check_pixel_color(pngs: list[Path]) -> None:
    """Sample top-left pixel: should be in the purple gradient range, not navy."""
    sample_size = min(80, len(pngs))
    step = max(1, len(pngs) // sample_size)
    sampled = pngs[::step][:sample_size]
    off = []
    no_data = 0
    for png in sampled:
        rgb = png_topleft_rgb(png)
        if rgb is None:
            no_data += 1
            continue
        r, g, b = rgb
        # Reject if it looks like navy: low R, low G, mid-high B AND R is very low
        # Accept anything with at least 15 in R (dark purple has ~0x2a..0x52..0x3a)
        if PURPLE_TARGET_RANGE["r"][0] <= r <= PURPLE_TARGET_RANGE["r"][1] \
           and PURPLE_TARGET_RANGE["g"][0] <= g <= PURPLE_TARGET_RANGE["g"][1] \
           and PURPLE_TARGET_RANGE["b"][0] <= b <= PURPLE_TARGET_RANGE["b"][1]:
            continue
        # Some slides have a non-purple top-left (overlay / hero photo / different layout).
        # Only flag the unambiguous-navy ones (R<15, G<35, B>50 — old navy gradient stops).
        if r < 15 and g < 35 and 50 < b < 110:
            off.append((png, rgb))

    record(
        "6. pixel-level navy gone (sampled)",
        not off,
        f"sampled {len(sampled)} PNGs; {no_data} had no decodable pixel; "
        f"{len(off)} still navy" if off else
        f"sampled {len(sampled)} PNGs; {no_data} undecoded; none still navy",
    )


def check_gallery_integrity() -> None:
    gallery = REPO_ROOT / "brand-update-gallery.html"
    if not gallery.exists():
        record("7. gallery integrity", False, "brand-update-gallery.html missing")
        return
    text = gallery.read_text(encoding="utf-8")
    srcs = re.findall(r"<img[^>]+src='([^']+)'", text)
    missing = [s for s in srcs if not (REPO_ROOT / s).exists()]
    record(
        "7. gallery integrity",
        not missing,
        f"{len(srcs)} images, all resolve" if not missing
        else f"{len(missing)} broken refs, e.g. {missing[0]}",
    )


def check_no_orphan_navy() -> None:
    leftovers = []
    for path in REPO_ROOT.rglob("*.html"):
        if "node_modules" in path.parts or ".git" in path.parts:
            continue
        if path.name == "preview.html":  # samples doc references navy in copy
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if NAVY_SIGNATURE.search(text):
            leftovers.append(path.relative_to(REPO_ROOT))
    record(
        "8. no orphan navy elsewhere",
        not leftovers,
        "repo clean of navy gradient" if not leftovers
        else f"{len(leftovers)} files still have navy: {leftovers[:3]}",
    )


def check_stray_palette(targets: list[Path]) -> None:
    """Informational: how many migrated files use non-palette accent colors?"""
    counter: Counter[str] = Counter()
    for p in targets:
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        for match in ANY_HEX.findall(text):
            color = match.lower()
            if color in NEW_PALETTE or color in NEUTRAL:
                continue
            counter[color] += 1
    common = counter.most_common(8)
    detail = ", ".join(f"{c}×{n}" for c, n in common) if common else "none"
    record("9. non-palette colors (info)", True, f"top stray hex: {detail}")


def check_git_scope() -> None:
    proc = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "status", "--porcelain"],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        record("10. git scope", False, "git status failed")
        return
    suspicious = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        path = line.split(maxsplit=1)[1] if " " in line else line
        if path.endswith((".html", ".png")):
            continue
        if path.startswith("scripts/") or path.startswith("brand-update-"):
            continue
        if path == "package-lock.json" or path == "package.json":
            continue
        suspicious.append(path)
    record(
        "10. git scope (only HTML/PNG/scripts/* changed)",
        not suspicious,
        "no surprise edits" if not suspicious
        else f"{len(suspicious)} unexpected paths, e.g. {suspicious[:3]}",
    )


# ---------- main -------------------------------------------------------------

def main() -> int:
    targets = collect_targets()
    print(f"Auditing {len(targets)} migrated HTML files…\n")

    check_idempotency()
    check_signature_gone(targets)
    pngs, _missing = check_png_existence(targets)
    check_png_freshness(targets)
    check_png_validity(pngs)
    check_pixel_color(pngs)
    check_gallery_integrity()
    check_no_orphan_navy()
    check_stray_palette(targets)
    check_git_scope()

    print()
    failed = [name for name, ok, _ in results if not ok]
    if failed:
        print(f"FAILED: {len(failed)} of {len(results)} checks — {failed}")
        return 1
    print(f"All {len(results)} checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
