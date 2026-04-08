#!/usr/bin/env bash
# Create _source-synced.mp4 = video and audio aligned at t=0
# (trims the leading audio that has no corresponding video frames).
set -e

sync_source() {
  local DIR="$1"
  local SRC="$DIR/_source-landscape.mp4"
  local OUT="$DIR/_source-synced.mp4"

  echo ">>> $OUT <<<"

  # Read the video stream's start_time and audio start_time
  local VSTART
  VSTART=$(ffprobe -v error -select_streams v:0 -show_entries stream=start_time -of csv=p=0 "$SRC")
  local ASTART
  ASTART=$(ffprobe -v error -select_streams a:0 -show_entries stream=start_time -of csv=p=0 "$SRC")
  echo "video starts at $VSTART, audio starts at $ASTART"

  # Skip $VSTART seconds of audio so it aligns with first video frame.
  # Reset both stream PTS to start at 0 in the output.
  ffmpeg -y -i "$SRC" \
    -vf "setpts=PTS-STARTPTS" \
    -af "atrim=start=${VSTART},asetpts=PTS-STARTPTS,aresample=44100" \
    -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
    -c:a aac -b:a 192k \
    -movflags +faststart \
    "$OUT" 2>&1 | tail -2

  echo "verification:"
  ffprobe -v error -show_entries stream=index,codec_type,start_time,duration -of default=noprint_wrappers=0 "$OUT" 2>&1 | grep -E "index|codec_type|start_time|^duration"
}

sync_source "content/curated/holly-peete"
sync_source "content/curated/ot-genasis"
