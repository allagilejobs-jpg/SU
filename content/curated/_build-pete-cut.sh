#!/usr/bin/env bash
# Build pete-wright/_source-synced.mp4 from a 44-minute split-screen podcast
# interview. Uses a TWO-STAGE crop approach:
#   1. Pre-crop to just Pete's window (right side of split-screen at x=680 y=155
#      560 wide x 365 tall) so Dr. Roseann's window is removed
#   2. Standard blur-fit the resulting Pete-only 560x365 content to 1080x1920
# This makes Pete the full-frame star of the reel. Host reactions are lost
# (acceptable for an expertise-focused reel).
set -e

DIR="content/curated/pete-wright"
SRC="$DIR/_source-landscape.mp4"
OUT="$DIR/_source-synced.mp4"

echo ">>> Cutting Pete Wright best-of segments from $SRC..."

# 5 segments (start end)
SEGMENTS=(
  "179.00 196.60"
  "196.60 209.60"
  "259.00 265.00"
  "466.00 486.30"
  "540.50 575.50"
)

# Build filter_complex: trim -> crop to Pete's window -> concat -> blur-fit
FILTER=""
CONCAT_V=""
CONCAT_A=""
for i in "${!SEGMENTS[@]}"; do
  read -r START END <<< "${SEGMENTS[$i]}"
  FILTER+="[0:v]trim=start=${START}:end=${END},setpts=PTS-STARTPTS,crop=560:365:680:155[v${i}];"
  FILTER+="[0:a]atrim=start=${START}:end=${END},asetpts=PTS-STARTPTS,aresample=44100[a${i}];"
  CONCAT_V+="[v${i}]"
  CONCAT_A+="[a${i}]"
done
N=${#SEGMENTS[@]}
FILTER+="${CONCAT_V}concat=n=${N}:v=1:a=0[vcat];"
FILTER+="${CONCAT_A}concat=n=${N}:v=0:a=1[aout];"

# Blur-fit: scale Pete to 1080 wide maintaining aspect, overlay on blurred 1080x1920 bg.
# 560x365 -> scaled to 1080 wide -> 1080x704 Pete content inside 1920 frame.
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
