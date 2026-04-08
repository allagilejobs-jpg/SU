#!/usr/bin/env bash
# Build the carousel video slide (1080x1350) for each artist.
#
# Source: _source-synced.mp4 (clean landscape, already offset-fixed / cut)
# Output: <slug>/carousel-v2/slide-2-video.mp4
#
# Holly / OT: standard center crop
# Faith:      left-biased crop (she sits on left of Tamron Hall couch)
#
# Overlays: brand-overlay-carousel.png (top crop of the 1080x1920 overlay)
#           + karaoke-brand.ass (libass auto-scales PlayRes positions)
set -e

# Step 1 - build 1080x1350 brand overlays from the 1920 ones by cropping
#          the top 1350 pixels (all brand content is in the top ~420px)
for slug in holly-peete ot-genasis faith-evans; do
  DIR="content/curated/$slug"
  if [ -f "$DIR/brand-overlay-v2.png" ]; then
    ffmpeg -y -i "$DIR/brand-overlay-v2.png" \
      -vf "crop=1080:1350:0:0" \
      "$DIR/carousel-v2/brand-overlay-carousel.png" 2>&1 | tail -2
    echo "cropped brand overlay for $slug"
  fi
done

# Step 2 - build the video slides
build_carousel_video() {
  local DIR="$1"
  local CROP_X="$2"   # 0 = center, 400 = left-bias for Faith

  local SRC="$DIR/_source-synced.mp4"
  local OVERLAY="$DIR/carousel-v2/brand-overlay-carousel.png"
  local OUT="$DIR/carousel-v2/slide-2-video.mp4"

  local CROP_EXPR
  if [ "$CROP_X" = "center" ]; then
    CROP_EXPR="crop=1080:1350:(in_w-1080)/2:0"
  else
    CROP_EXPR="crop=1080:1350:${CROP_X}:0"
  fi

  echo ">>> $OUT (crop_x=$CROP_X) <<<"

  pushd "$DIR" >/dev/null

  ffmpeg -y -i "_source-synced.mp4" -i "carousel-v2/brand-overlay-carousel.png" \
    -filter_complex "
      [0:v]scale=-2:1350,${CROP_EXPR},setsar=1,format=yuv420p[cropped];
      [cropped][1:v]overlay=0:0[branded];
      [branded]ass=styles/karaoke-brand.ass:fontsdir=../fonts,format=yuv420p[vout]
    " \
    -map "[vout]" -map "0:a" \
    -c:v libx264 -preset medium -crf 20 \
    -profile:v high -level 4.0 -pix_fmt yuv420p \
    -c:a aac -b:a 128k -movflags +faststart \
    "carousel-v2/slide-2-video.mp4" 2>&1 | tail -3

  popd >/dev/null

  ffprobe -v error -select_streams v:0 -show_entries stream=width,height,duration -of csv=p=0 "$OUT"
}

build_carousel_video "content/curated/holly-peete"  "center"
build_carousel_video "content/curated/ot-genasis"   "center"
build_carousel_video "content/curated/faith-evans"  "400"
