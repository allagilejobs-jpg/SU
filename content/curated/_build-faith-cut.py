"""
Build faith-evans/_source-synced.mp4 by cutting and concatenating the
6 best quote segments from the full 7-min source, with smooth
crossfades and audio acrossfades between each segment.
"""
import subprocess
from pathlib import Path

BASE = Path("C:/Users/Solomon/Desktop/SU/content/curated/faith-evans")
SRC  = BASE / "_source-landscape.mp4"
OUT  = BASE / "_source-synced.mp4"

# (start, end) in source seconds
# Cuts avoid:
#   - 159.5-160.5  (Tamron reaction cutaway in the middle of cut 3)
#   - 247.5-252.0  (audience B-roll in the middle of cut 4)
SEGMENTS = [
    (109.34, 117.80),  # "Ryder was just under three. I was kind of begging..."
    (128.00, 146.20),  # Knew he wasn't meeting milestones; doctor told her to wait
    (149.30, 159.50),  # "I finally just begged enough... California legislation" (part 1)
    (160.50, 169.20),  # (part 2 - skipping Tamron reaction cutaway)
    (241.30, 247.40),  # "with the help of other parents, thank God" (pre-audience)
    (252.40, 262.20),  # "it was another parent who became my first advocate" (post-audience)
    (296.10, 312.60),  # "You got to beg for it... I'll come with you"
    (312.70, 324.94),  # Started Ryder's Room "to not gatekeep... cry together"
]

XFADE = 0.30  # crossfade duration between segments (seconds)

def dur(seg):
    return seg[1] - seg[0]

# Compute cumulative durations & xfade offsets
durations  = [dur(s) for s in SEGMENTS]
n = len(SEGMENTS)

# Build filter_complex
lines = []
for i, (start, end) in enumerate(SEGMENTS):
    lines.append(
        f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS,format=yuv420p[v{i}];"
    )
    lines.append(
        f"[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS,aresample=44100[a{i}];"
    )

# Chain video xfades
running_dur = durations[0]
vcur = "v0"
for i in range(1, n):
    offset = running_dur - XFADE
    nxt = f"vt{i}" if i < n - 1 else "vout"
    lines.append(
        f"[{vcur}][v{i}]xfade=transition=fade:duration={XFADE}:offset={offset:.3f}[{nxt}];"
    )
    running_dur = running_dur + durations[i] - XFADE
    vcur = nxt

# Chain audio acrossfades
acur = "a0"
for i in range(1, n):
    nxt = f"at{i}" if i < n - 1 else "aout"
    lines.append(
        f"[{acur}][a{i}]acrossfade=d={XFADE}[{nxt}];"
    )
    acur = nxt

# Trim trailing semicolon of last line
filter_complex = "\n".join(lines).rstrip(";")

print("Filter graph:")
print(filter_complex)
print()
print(f"Expected final duration: {running_dur:.3f}s")
print()

cmd = [
    "ffmpeg", "-y", "-i", str(SRC),
    "-filter_complex", filter_complex,
    "-map", "[vout]", "-map", "[aout]",
    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
    "-profile:v", "high", "-level", "4.0", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "192k",
    "-movflags", "+faststart",
    str(OUT),
]
print("Running ffmpeg...")
r = subprocess.run(cmd, capture_output=True, text=True)
# Print last few lines of ffmpeg output
tail = "\n".join((r.stderr or r.stdout).strip().splitlines()[-5:])
print(tail)
if r.returncode != 0:
    raise SystemExit(r.returncode)

# Probe result
probe = subprocess.run(
    ["ffprobe", "-v", "error",
     "-show_entries", "stream=index,codec_type,start_time,duration",
     "-of", "default=noprint_wrappers=0",
     str(OUT)],
    capture_output=True, text=True,
)
print()
print(probe.stdout)
