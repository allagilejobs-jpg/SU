#!/usr/bin/env bash
# Build 3 vertical fit variants from a landscape source.
# Usage: build_variants <source.mp4> <output_dir>
set -e

build_variants() {
  local SRC="$1"
  local DIR="$2"

  echo ">>> $DIR <<<"

  # ---- Option A: Blurred background fit (no crop) ----
  # Sharp full-width video centered, blurred zoomed copy fills top/bottom.
  ffmpeg -y -i "$SRC" -filter_complex "
    [0:v]split=2[bg][fg];
    [bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=40:1,eq=brightness=-0.10[bg];
    [fg]scale=1080:-2[fg];
    [bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1
  " -c:v libx264 -preset medium -crf 20 -c:a aac -b:a 128k -movflags +faststart \
    "$DIR/clip-blurfit.mp4" 2>&1 | tail -3

  # ---- Option B: Black letterbox (no crop) ----
  ffmpeg -y -i "$SRC" -vf "
    scale=1080:-2,
    pad=1080:1920:0:(1920-ih)/2:black,
    setsar=1
  " -c:v libx264 -preset medium -crf 20 -c:a aac -b:a 128k -movflags +faststart \
    "$DIR/clip-letterbox.mp4" 2>&1 | tail -3

  # ---- Option C: Loose crop (4:3 area, less aggressive than full crop) ----
  # Scale source so it fills a 1080x1440 area (4:3 framing), crop sides,
  # then pad top/bottom 240px each with black to reach 1080x1920.
  ffmpeg -y -i "$SRC" -vf "
    scale=-2:1440,
    crop=1080:1440,
    pad=1080:1920:0:240:black,
    setsar=1
  " -c:v libx264 -preset medium -crf 20 -c:a aac -b:a 128k -movflags +faststart \
    "$DIR/clip-loosecrop.mp4" 2>&1 | tail -3
}

build_variants "content/curated/holly-peete/_source-landscape.mp4" "content/curated/holly-peete"
build_variants "content/curated/ot-genasis/_source-landscape.mp4"  "content/curated/ot-genasis"

echo
echo "=== RESULTS ==="
for f in content/curated/holly-peete/clip-blurfit.mp4 \
         content/curated/holly-peete/clip-letterbox.mp4 \
         content/curated/holly-peete/clip-loosecrop.mp4 \
         content/curated/ot-genasis/clip-blurfit.mp4 \
         content/curated/ot-genasis/clip-letterbox.mp4 \
         content/curated/ot-genasis/clip-loosecrop.mp4; do
  if [ -f "$f" ]; then
    size=$(du -h "$f" | cut -f1)
    dim=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "$f")
    echo "OK  $f ($dim, $size)"
  else
    echo "MISS $f"
  fi
done
