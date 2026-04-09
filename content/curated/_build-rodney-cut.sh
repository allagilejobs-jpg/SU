#!/usr/bin/env bash
# Build rodney-peete/_source-synced.mp4 by cutting and concatenating
# the 7 best segments from the CBS Early Show source, then blur-fit
# to 1080x1920. Uses blur-fit because:
#  1. Source is SD (640x480) — any crop magnifies the softness
#  2. Shot is mostly a 2-shot of Holly + Rodney on the Early Show couch,
#     so center/left/right biased crops all lose one parent.
set -e

DIR="content/curated/rodney-peete"
SRC="$DIR/_source-landscape.mp4"
OUT="$DIR/_source-synced.mp4"

echo ">>> Cutting Rodney best-of segments from $SRC..."

# 7 segments (start end) - see _cuts.txt for labels
SEGMENTS=(
  "143.38 152.06"
  "214.04 225.30"
  "229.90 239.40"
  "239.40 250.30"
  "250.30 254.80"
  "263.40 271.40"
  "134.70 140.30"
)

# Build filter_complex: trim each segment, then concat, then blur-fit to 1080x1920
FILTER=""
CONCAT_V=""
CONCAT_A=""
for i in "${!SEGMENTS[@]}"; do
  read -r START END <<< "${SEGMENTS[$i]}"
  FILTER+="[0:v]trim=start=${START}:end=${END},setpts=PTS-STARTPTS[v${i}];"
  FILTER+="[0:a]atrim=start=${START}:end=${END},asetpts=PTS-STARTPTS,aresample=44100[a${i}];"
  CONCAT_V+="[v${i}]"
  CONCAT_A+="[a${i}]"
done
N=${#SEGMENTS[@]}
FILTER+="${CONCAT_V}concat=n=${N}:v=1:a=0[vcat];"
FILTER+="${CONCAT_A}concat=n=${N}:v=0:a=1[aout];"

# Blur-fit: scale content to 1080 wide maintaining aspect, overlay on blurred 1080x1920 bg.
# For 640x480 source, 1080 wide = 810 tall content inside 1920 frame.
FILTER+="[vcat]split=2[vfg][vbg];"
FILTER+="[vbg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=40:2[bg];"
FILTER+="[vfg]scale=1080:-2[fg];"
FILTER+="[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1,format=yuv420p[vout]"

ffmpeg -y -i "$SRC" \
  -filter_complex "$FILTER" \
  -map "[vout]" -map "[aout]" \
  -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p \
  -c:a aac -b:a 192k \
  -movflags +faststart \
  "$OUT" 2>&1 | tail -5

echo
echo "Result:"
ffprobe -v error -show_entries stream=index,codec_type,width,height,duration -of default=noprint_wrappers=0 "$OUT" 2>&1 | grep -E "index|codec_type|width|height|^duration"
