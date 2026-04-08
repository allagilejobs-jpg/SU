#!/usr/bin/env bash
# Render 5 caption-style demos using Holly's blur-fit clip + brand overlay.
# Each demo is the FULL clip with one caption style burned in.
set -e

DIR="content/curated/holly-peete"
SRC="$DIR/clip-blurfit.mp4"
BRAND="$DIR/brand-overlay-v2.png"
OUTDIR="$DIR/style-demos"
mkdir -p "$OUTDIR"

pushd "$DIR" >/dev/null

for STYLE in style1-hormozi style2-karaoke style3-popword style4-opusclip style5-broadcast; do
  ASS="styles/${STYLE}.ass"
  OUT="style-demos/demo-${STYLE}.mp4"
  echo ">>> $OUT <<<"
  ffmpeg -y -i "clip-blurfit.mp4" -i "brand-overlay-v2.png" \
    -filter_complex "
      [0:v][1:v]overlay=0:0[branded];
      [branded]ass=${ASS}[vout]
    " \
    -map "[vout]" -map "0:a" \
    -c:v libx264 -preset medium -crf 20 \
    -c:a aac -b:a 128k \
    -movflags +faststart \
    "$OUT" 2>&1 | tail -3
done

popd >/dev/null

echo
echo "=== RESULTS ==="
for f in $DIR/style-demos/*.mp4; do
  dim=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height,duration -of csv=p=0 "$f")
  size=$(du -h "$f" | cut -f1)
  echo "OK $f ($dim, $size)"
done
