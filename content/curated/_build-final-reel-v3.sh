#!/usr/bin/env bash
# Build FINAL-reel-v3.mp4 for both artists:
#   1. Take original cropped FINAL clip
#   2. Burn brand overlay v2 (top brand bar) + karaoke captions
#   3. Concat: a1-magazine cover (3s) + branded captioned clip + ending CTA (3.5s)
#   4. Crossfade transitions: 0.5s in, 0.8s out
set -e

build_branded_clip() {
  # Build clip from CLEAN landscape source (no baked overlays).
  # Crop matches the original FINAL.mp4 framing the user prefers:
  #   scale source so height=1920, center-crop 1080 wide.
  # Then overlay new brand bar + burn karaoke captions.
  local DIR="$1"
  local OUT="clip-branded-v2.mp4"

  echo ">>> branded clip: $DIR/$OUT <<<"
  pushd "$DIR" >/dev/null

  ffmpeg -y -i "_source-synced.mp4" -i "brand-overlay-v2.png" \
    -filter_complex "
      [0:v]scale=-2:1920,crop=1080:1920:(in_w-1080)/2:0,setsar=1,format=yuv420p[cropped];
      [cropped][1:v]overlay=0:0[branded];
      [branded]ass=styles/karaoke-brand.ass:fontsdir=../fonts,format=yuv420p[vout]
    " \
    -map "[vout]" -map "0:a" \
    -c:v libx264 -preset medium -crf 20 \
    -profile:v high -level 4.0 -pix_fmt yuv420p \
    -c:a aac -b:a 128k -movflags +faststart \
    "$OUT" 2>&1 | tail -2

  popd >/dev/null
  ffprobe -v error -select_streams v:0 -show_entries stream=width,height,duration -of csv=p=0 "$DIR/$OUT"
}

build_reel() {
  local DIR="$1"
  local COVER="$DIR/cover-options/a1-magazine.png"
  local CLIP="$DIR/clip-branded-v2.mp4"
  local ENDING="$DIR/ending-slide.png"
  local OUT="$DIR/FINAL-reel-v3.mp4"

  echo ">>> reel: $OUT <<<"

  local CLIP_DUR
  CLIP_DUR=$(ffprobe -v error -select_streams v:0 -show_entries stream=duration -of csv=p=0 "$CLIP")

  local COVER_DUR=3.0
  local ENDING_DUR=3.5
  local XFADE_IN=0.5
  local XFADE_OUT=0.8

  local OFF1
  OFF1=$(awk -v c=$COVER_DUR -v x=$XFADE_IN 'BEGIN{printf "%.3f", c - x}')
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
      [0:v]scale=1080:1920,setsar=1,fps=29.97,format=yuv420p,trim=duration=${COVER_DUR},setpts=PTS-STARTPTS[v0];
      [1:v]scale=1080:1920,setsar=1,fps=29.97,format=yuv420p,setpts=PTS-STARTPTS[v1];
      [2:v]scale=1080:1920,setsar=1,fps=29.97,format=yuv420p,trim=duration=${ENDING_DUR},setpts=PTS-STARTPTS[v2];
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
    -profile:v high -level 4.0 -pix_fmt yuv420p \
    -c:a aac -b:a 128k -movflags +faststart \
    "$OUT" 2>&1 | tail -2

  ffprobe -v error -select_streams v:0 -show_entries stream=width,height,duration -of csv=p=0 "$OUT"
}

build_branded_clip "content/curated/holly-peete"
build_branded_clip "content/curated/ot-genasis"
build_branded_clip "content/curated/faith-evans"
build_branded_clip "content/curated/dan-orlovsky-madden"
build_branded_clip "content/curated/tisha-campbell"
build_branded_clip "content/curated/rodney-peete"
build_branded_clip "content/curated/pete-wright"

build_reel "content/curated/holly-peete"
build_reel "content/curated/ot-genasis"
build_reel "content/curated/faith-evans"
build_reel "content/curated/dan-orlovsky-madden"
build_reel "content/curated/tisha-campbell"
build_reel "content/curated/rodney-peete"
build_reel "content/curated/pete-wright"

echo
echo "DONE"
