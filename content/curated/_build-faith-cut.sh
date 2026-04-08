#!/usr/bin/env bash
# Build faith-evans/_source-synced.mp4 by cutting and concatenating
# the 6 best quote segments from the full 7-min source.
set -e

DIR="content/curated/faith-evans"
SRC="$DIR/_source-landscape.mp4"
OUT="$DIR/_source-synced.mp4"

echo ">>> Cutting Faith best-of segments..."

# 6 segments (start end)
SEGMENTS=(
  "109.34 117.80"
  "128.00 146.20"
  "149.30 169.20"
  "246.40 262.20"
  "296.10 312.60"
  "312.70 324.94"
)

# Build filter_complex
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
FILTER+="${CONCAT_V}concat=n=${N}:v=1:a=0[vout];"
FILTER+="${CONCAT_A}concat=n=${N}:v=0:a=1[aout]"

ffmpeg -y -i "$SRC" \
  -filter_complex "$FILTER" \
  -map "[vout]" -map "[aout]" \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 192k \
  -movflags +faststart \
  "$OUT" 2>&1 | tail -3

echo
echo "Result:"
ffprobe -v error -show_entries stream=index,codec_type,start_time,duration -of default=noprint_wrappers=0 "$OUT" 2>&1 | grep -E "index|codec_type|start_time|^duration"
