"""
Generate 5 ASS subtitle files in different modern caption styles
from a Whisper word-level JSON transcript.

Output: 5 .ass files in <out_dir>/

Usage: python _caption_styles.py <whisper.json> <out_dir>
"""
import json
import sys
from pathlib import Path

JSON_IN = Path(sys.argv[1])
OUT_DIR = Path(sys.argv[2])
OUT_DIR.mkdir(parents=True, exist_ok=True)

data = json.loads(JSON_IN.read_text(encoding="utf-8"))

# Flatten all words across segments
words = []
for seg in data["segments"]:
    for w in seg.get("words", []):
        text = w["word"].strip()
        if text:
            words.append({"text": text, "start": w["start"], "end": w["end"]})

# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def ts(t: float) -> str:
    """ASS timestamp: H:MM:SS.cs"""
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def header(styles_block: str) -> str:
    return (
        "[Script Info]\n"
        "ScriptType: v4.00+\n"
        "PlayResX: 1080\n"
        "PlayResY: 1920\n"
        "ScaledBorderAndShadow: yes\n"
        "WrapStyle: 2\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
        "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
        "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"{styles_block}\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )

def chunk_words(words, max_words=4, max_gap=1.2):
    """Group words into chunks of up to max_words, breaking on long pauses."""
    chunks = []
    cur = []
    for w in words:
        if cur and (len(cur) >= max_words or w["start"] - cur[-1]["end"] > max_gap):
            chunks.append(cur)
            cur = []
        cur.append(w)
    if cur:
        chunks.append(cur)
    return chunks

# ----------------------------------------------------------------------
# Style 1: Hormozi (massive uppercase, gold highlight on key words)
# ----------------------------------------------------------------------
def style1_hormozi():
    styles = (
        "Style: Base,Impact,72,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,"
        "1,0,0,0,100,100,2,0,1,6,0,2,40,40,140,1\n"
        "Style: Hi,Impact,72,&H006DA5E8,&H000000FF,&H00000000,&H00000000,"
        "1,0,0,0,100,100,2,0,1,6,0,2,40,40,140,1\n"
    )
    EMPHASIS = {
        "diagnosis", "begging", "begged", "beg", "autism", "love", "friend",
        "friends", "wonder", "wonderful", "favorite", "real", "judge",
    }
    chunks = chunk_words(words, max_words=3)
    events = []
    for chunk in chunks:
        start = chunk[0]["start"]
        end = chunk[-1]["end"]
        parts = []
        for w in chunk:
            clean = w["text"].upper()
            stripped = "".join(c for c in clean.lower() if c.isalpha())
            if stripped in EMPHASIS:
                parts.append(f"{{\\c&H6DA5E8&}}{clean}{{\\c&HFFFFFF&}}")
            else:
                parts.append(clean)
        text = " ".join(parts)
        events.append(f"Dialogue: 0,{ts(start)},{ts(end)},Base,,0,0,0,,{text}")
    return header(styles) + "\n".join(events) + "\n"

# ----------------------------------------------------------------------
# Style 2: Karaoke highlight (whole sentence visible, current word colored)
# ----------------------------------------------------------------------
def style2_karaoke():
    styles = (
        "Style: Base,Arial,42,&H00CCCCCC,&H0000FFFF,&H00000000,&H80000000,"
        "1,0,0,0,100,100,1,0,1,3,0,2,80,80,120,1\n"
    )
    chunks = chunk_words(words, max_words=8)
    events = []
    for chunk in chunks:
        start = chunk[0]["start"]
        end = chunk[-1]["end"]
        parts = []
        for w in chunk:
            dur_cs = max(1, int((w["end"] - w["start"]) * 100))
            # \kf = sweep highlight, secondary color becomes the highlight color
            parts.append(f"{{\\kf{dur_cs}}}{w['text']}")
        text = " ".join(parts)
        events.append(f"Dialogue: 0,{ts(start)},{ts(end)},Base,,0,0,0,,{text}")
    return header(styles) + "\n".join(events) + "\n"

# ----------------------------------------------------------------------
# Style 3: Word-by-word pop (one word at a time, huge, animated)
# ----------------------------------------------------------------------
def style3_popword():
    styles = (
        "Style: Pop,Impact,96,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,"
        "1,0,0,0,100,100,3,0,1,8,0,2,40,40,160,1\n"
    )
    events = []
    for w in words:
        text = w["text"].upper()
        # scale-in animation: start at 50%, grow to 100% over first 100ms
        animated = f"{{\\fscx50\\fscy50\\t(0,100,\\fscx100\\fscy100)}}{text}"
        events.append(f"Dialogue: 0,{ts(w['start'])},{ts(w['end'])},Pop,,0,0,0,,{animated}")
    return header(styles) + "\n".join(events) + "\n"

# ----------------------------------------------------------------------
# Style 4: Opus Clip 2-line bold (4 words, uppercase, key words gold)
# ----------------------------------------------------------------------
def style4_opusclip():
    styles = (
        "Style: Base,Arial Black,52,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,"
        "1,0,0,0,100,100,2,0,1,5,0,2,60,60,140,1\n"
    )
    EMPHASIS = {
        "diagnosis", "begging", "begged", "beg", "autism", "love", "friend",
        "friends", "wonder", "real", "judge", "back", "favorite",
    }
    chunks = chunk_words(words, max_words=4)
    events = []
    for chunk in chunks:
        start = chunk[0]["start"]
        end = chunk[-1]["end"]
        parts = []
        for w in chunk:
            clean = w["text"].upper()
            stripped = "".join(c for c in clean.lower() if c.isalpha())
            if stripped in EMPHASIS:
                # gold #E8B86D = BGR &H6DB8E8&
                parts.append(f"{{\\c&H6DB8E8&}}{clean}{{\\c&HFFFFFF&}}")
            else:
                parts.append(clean)
        text = " ".join(parts)
        events.append(f"Dialogue: 0,{ts(start)},{ts(end)},Base,,0,0,0,,{text}")
    return header(styles) + "\n".join(events) + "\n"

# ----------------------------------------------------------------------
# Style 5: Clean broadcast (sentence-case lines, white w/ subtle box)
# ----------------------------------------------------------------------
def style5_broadcast():
    styles = (
        "Style: Base,Arial,38,&H00FFFFFF,&H000000FF,&H00000000,&HA0000000,"
        "0,0,0,0,100,100,0,0,3,0,0,2,80,80,130,1\n"
    )
    # Use whisper segments (sentence-level) for broadcast feel
    events = []
    for seg in data["segments"]:
        text = seg["text"].strip()
        if not text:
            continue
        events.append(
            f"Dialogue: 0,{ts(seg['start'])},{ts(seg['end'])},Base,,0,0,0,,{text}"
        )
    return header(styles) + "\n".join(events) + "\n"

# ----------------------------------------------------------------------
# Write all 5 files
# ----------------------------------------------------------------------
outputs = {
    "style1-hormozi.ass":    style1_hormozi(),
    "style2-karaoke.ass":    style2_karaoke(),
    "style3-popword.ass":    style3_popword(),
    "style4-opusclip.ass":   style4_opusclip(),
    "style5-broadcast.ass":  style5_broadcast(),
}
for name, content in outputs.items():
    p = OUT_DIR / name
    p.write_text(content, encoding="utf-8")
    print(f"wrote {p}")
