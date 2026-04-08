#!/usr/bin/env bash
# Build dan-orlovsky-madden/_source-synced.mp4 by cutting and concatenating
# the 5 best segments, then pre-formatting to 1080x1920 with blur-fit.
# Uses blur-fit (NOT center crop) because Beat 4 (the quote) is a split-screen
# where Madden is on the left and Dan is on the right. Center-cropping would
# destroy Dan's reaction.
set -e

DIR="content/curated/dan-orlovsky-madden"
SRC="$DIR/_source-landscape-crf22.mp4"
[ -f "$SRC" ] || SRC="$DIR/_source-landscape.mp4"
OUT="$DIR/_source-synced.mp4"

echo ">>> Cutting Dan/Madden best-of segments from $SRC..."

# 5 segments (start end) - see _cuts.txt for labels
SEGMENTS=(
  "42.0 52.0"
  "72.0 84.0"
  "222.0 232.0"
  "584.0 612.0"
  "625.0 632.0"
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

# Blur-fit: scale content to 1080 wide maintaining aspect, overlay on blurred 1080x1920 bg
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
