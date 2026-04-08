"""
Spectrum Unlocked branded karaoke captions.

Style:
  - Font: Poppins ExtraBold (loaded from ../fonts/)
  - 3-state coloring:
      past words   = white     #FFFFFF
      current word = gold      #E8B86D  (brand accent)
      future words = muted gray (slightly cool to match brand)
  - Word groups of ~6 words, max 2 lines visible at a time.
  - Each "frame" of the karaoke is emitted as its own Dialogue line so
    the 3-state coloring is exact (ASS \k tags only support 2 states).
  - Phrases break on long pauses or when group is full.

ASS color format: &HBBGGRR&  (libass uses BGR, not RGB)
  white  #FFFFFF -> &H00FFFFFF&
  gold   #E8B86D -> &H006DB8E8&
  faded  #6B7B8C -> &H008C7B6B&

Usage: python _karaoke_brand.py <whisper.json> <out.ass>
"""
import json
import sys
from pathlib import Path

JSON_IN = Path(sys.argv[1])
OUT_ASS = Path(sys.argv[2])

# ---- brand colors (BGR for ASS) ----
WHITE  = "&H00FFFFFF&"
GOLD   = "&H006DB8E8&"   # #E8B86D
FADED  = "&H008C7B6B&"   # muted blue-gray, brand-coherent

# ---- layout ----
PLAY_W = 1080
PLAY_Y = 1920
FONT_NAME = "Poppins"
FONT_SIZE = 68           # big and readable
ANCHOR_X = 540           # horizontal center
ANCHOR_Y = 1620          # vertical CENTER of caption block
MAX_WORDS_PER_GROUP = 5  # smaller groups -> consistent wrap
MAX_PAUSE = 0.9          # break group on pause longer than this

# Timing tweaks for sync quality
READ_AHEAD = 0.0         # don't show ahead of speech (was causing perceived lead)
WORD_BIAS  = 0.0         # no shift now that source is properly synced
TAIL_HOLD  = 0.40        # last word stays highlighted this long after group ends
                         # (or until next group starts, whichever is sooner)

data = json.loads(JSON_IN.read_text(encoding="utf-8"))

# Flatten words across segments
words = []
for seg in data["segments"]:
    for w in seg.get("words", []):
        text = w["word"].strip()
        if text:
            words.append({"text": text, "start": w["start"], "end": w["end"]})

# Group words into phrases
groups = []
cur = []
for w in words:
    if cur and (
        len(cur) >= MAX_WORDS_PER_GROUP
        or (w["start"] - cur[-1]["end"]) > MAX_PAUSE
    ):
        groups.append(cur)
        cur = []
    cur.append(w)
if cur:
    groups.append(cur)

def ts(t: float) -> str:
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def header() -> str:
    return f"""[Script Info]
ScriptType: v4.00+
PlayResX: {PLAY_W}
PlayResY: {PLAY_Y}
ScaledBorderAndShadow: yes
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Karaoke,{FONT_NAME},{FONT_SIZE},&H00FFFFFF,&H000000FF,&H00000000,&H00000000,1,0,0,0,100,100,2,0,1,4,2,5,80,80,40,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

events = []
for gi, group in enumerate(groups):
    group_start = group[0]["start"] + WORD_BIAS
    group_end   = group[-1]["end"]   + WORD_BIAS

    # When does the next group start? We extend our last word's
    # display until the next group begins (no caption gaps).
    if gi + 1 < len(groups):
        next_group_start = groups[gi + 1][0]["start"] + WORD_BIAS
    else:
        next_group_start = group_end + 1.0  # last group: hold a bit at the end

    # For each word in the group, emit a Dialogue line that spans
    # from when this word becomes "current" to when the NEXT word does.
    for i, w in enumerate(group):
        word_start = w["start"] + WORD_BIAS
        if i == 0:
            # First word: show the phrase a bit early so viewer can read ahead
            line_start = max(0, word_start - READ_AHEAD)
        else:
            line_start = word_start

        if i + 1 < len(group):
            line_end = group[i + 1]["start"] + WORD_BIAS
        else:
            # Last word: hold until next group begins, capped by TAIL_HOLD
            line_end = min(next_group_start, w["end"] + WORD_BIAS + TAIL_HOLD)

        # Build colored line: past=white, current=gold, future=faded.
        # Position override is prepended once; libass handles adjacent
        # {} override blocks correctly without needing string surgery.
        prefix = f"{{\\an5\\pos({ANCHOR_X},{ANCHOR_Y})}}"
        word_parts = []
        for j, w2 in enumerate(group):
            txt = w2["text"]
            if j < i:
                col = WHITE
            elif j == i:
                col = GOLD
            else:
                col = FADED
            word_parts.append(f"{{\\1c{col}}}{txt}")
        text = prefix + " ".join(word_parts)
        events.append(
            f"Dialogue: 0,{ts(line_start)},{ts(line_end)},Karaoke,,0,0,0,,{text}"
        )

OUT_ASS.write_text(header() + "\n".join(events) + "\n", encoding="utf-8")
print(f"wrote {OUT_ASS}  ({len(groups)} groups, {len(events)} lines)")
