#!/usr/bin/env bash
# Build FINAL-reel-v2.mp4 with seamless crossfade transitions:
#   cover (3s) --[0.5s xfade]--> clip --[0.8s xfade]--> ending CTA (3.5s)
# Audio: silent on stills, real on clip, acrossfade smooths the boundaries.
set -e

build_reel() {
  local DIR="$1"
  local COVER="$DIR/cover-slide-v3.png"
  local CLIP="$DIR/clip-blurfit.mp4"
  local ENDING="$DIR/ending-slide.png"
  local OUT="$DIR/FINAL-reel-v2.mp4"

  echo ">>> Building $OUT <<<"

  # Read clip duration
  local CLIP_DUR
  CLIP_DUR=$(ffprobe -v error -select_streams v:0 -show_entries stream=duration -of csv=p=0 "$CLIP")

  local COVER_DUR=3.0
  local ENDING_DUR=3.5
  local XFADE_IN=0.5    # cover -> clip
  local XFADE_OUT=0.8   # clip -> ending

  # xfade offsets (when each transition starts in the output timeline)
  local OFF1
  OFF1=$(awk -v c=$COVER_DUR -v x=$XFADE_IN 'BEGIN{printf "%.3f", c - x}')
  # After xfade1 the timeline length = COVER + CLIP - XFADE_IN
  local OFF2
  OFF2=$(awk -v c=$COVER_DUR -v cl=$CLIP_DUR -v xi=$XFADE_IN -v xo=$XFADE_OUT \
         'BEGIN{printf "%.3f", c + cl - xi - xo}')

  ffmpeg -y \
    -loop 1 -t $COVER_DUR  -i "$COVER" \
    -i "$CLIP" \
    -loop 1 -t $ENDING_DUR -i "$ENDING" \
    -f lavfi -t $COVER_DUR  -i anullsrc=channel_layout=stereo:sample_rate=44100 \
    -f lavfi -t $ENDING_DUR -i anullsrc=channel_layout=stereo:sample_rate=44100 \
    -filter_complex "
      [0:v]scale=1080:-2,pad=1080:1920:0:(1920-ih)/2:black,setsar=1,fps=29.97,format=yuv420p,trim=duration=${COVER_DUR},setpts=PTS-STARTPTS[v0];
      [1:v]scale=1080:1920,setsar=1,fps=29.97,format=yuv420p,setpts=PTS-STARTPTS[v1];
      [2:v]scale=1080:-2,pad=1080:1920:0:(1920-ih)/2:black,setsar=1,fps=29.97,format=yuv420p,trim=duration=${ENDING_DUR},setpts=PTS-STARTPTS[v2];
      [v0][v1]xfade=transition=fade:duration=${XFADE_IN}:offset=${OFF1}[v01];
      [v01][v2]xfade=transition=fade:duration=${XFADE_OUT}:offset=${OFF2}[vout];
      [3:a]asetpts=PTS-STARTPTS[a0];
      [1:a]aresample=44100,asetpts=PTS-STARTPTS[a1];
      [4:a]asetpts=PTS-STARTPTS[a2];
      [a0][a1]acrossfade=d=${XFADE_IN}[a01];
      [a01][a2]acrossfade=d=${XFADE_OUT}[aout]
    " \
    -map "[vout]" -map "[aout]" \
    -c:v libx264 -preset medium -crf 20 \
    -c:a aac -b:a 128k \
    -movflags +faststart \
    "$OUT" 2>&1 | tail -3

  local dim
  dim=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height,duration -of csv=p=0 "$OUT")
  echo "OK $OUT  ($dim)"
}

build_reel "content/curated/holly-peete"
build_reel "content/curated/ot-genasis"
