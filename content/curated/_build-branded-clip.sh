#!/usr/bin/env bash
# Build clip-branded.mp4 = blur fit + brand overlay + burned-in captions
# Run from the artist directory so subtitles filter can use relative path.
set -e

build_branded() {
  local DIR="$1"
  local SRC_REL="_source-landscape.mp4"
  local SRT_REL="_source-landscape.srt"
  local BRAND_REL="brand-overlay-v2.png"
  local OUT_REL="clip-branded.mp4"

  echo ">>> $DIR <<<"
  pushd "$DIR" >/dev/null

  ffmpeg -y \
    -i "$SRC_REL" \
    -i "$BRAND_REL" \
    -filter_complex "
      [0:v]split=2[bg][fg];
      [bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=40:1,eq=brightness=-0.15[bg2];
      [fg]scale=1080:-2[fg2];
      [bg2][fg2]overlay=(W-w)/2:(H-h)/2[blur];
      [blur][1:v]overlay=0:0[branded];
      [branded]subtitles=${SRT_REL}:force_style='Fontname=Arial,Fontsize=20,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BackColour=&H80000000,BorderStyle=1,Outline=3,Shadow=0,Bold=1,Alignment=2,MarginV=110,WrapStyle=2'[vout]
    " \
    -map "[vout]" -map "0:a" \
    -c:v libx264 -preset medium -crf 20 \
    -c:a aac -b:a 128k \
    -movflags +faststart \
    "$OUT_REL" 2>&1 | tail -5

  popd >/dev/null

  local dim
  dim=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height,duration -of csv=p=0 "$DIR/$OUT_REL")
  echo "OK $DIR/$OUT_REL ($dim)"
}

build_branded "content/curated/holly-peete"
build_branded "content/curated/ot-genasis"
