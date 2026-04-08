#!/usr/bin/env bash
# Faith-specific reel build: left-biased crop + blur fit.
#
# Source: 1280x720 landscape (_source-synced.mp4 — already the best-of cut)
# Target: 1080x1920 vertical
#
# Crop strategy: scale to height=1440 (not 1920), then left-bias the 1080-wide
# crop so Faith is always visible whether the shot is a close-up (her face at
# source x~640) or a wide two-shot (her face at source x~300). The result is
# 1080x1440; then blur-fill top and bottom 240px each to reach 1080x1920.
#
# This avoids the center-crop failure where wide two-shots captured the empty
# couch between Faith and Tamron, and the audience B-roll center-crop.
set -e

DIR="content/curated/faith-evans"

# ============================================================
# Step 1: Build clip-branded-v2.mp4 = left-bias cropped + blur-fit
#         + brand overlay + karaoke captions
# ============================================================
echo ">>> Building branded clip with left-biased crop + blur fit..."

pushd "$DIR" >/dev/null

ffmpeg -y -i "_source-synced.mp4" -i "brand-overlay-v2.png" \
  -filter_complex "
    [0:v]scale=-2:1440,crop=1080:1440:400:0,setsar=1,format=yuv420p[cropped];
    [cropped]split=2[bg][fg];
    [bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=40:1,eq=brightness=-0.15[bg2];
    [fg]pad=1080:1920:0:240:color=black@0[fg2];
    [bg2][fg2]overlay=shortest=1:format=auto[blurfit];
    [blurfit][1:v]overlay=0:0[branded];
    [branded]ass=styles/karaoke-brand.ass:fontsdir=../fonts,format=yuv420p[vout]
  " \
  -map "[vout]" -map "0:a" \
  -c:v libx264 -preset medium -crf 20 \
  -profile:v high -level 4.0 -pix_fmt yuv420p \
  -c:a aac -b:a 128k -movflags +faststart \
  "clip-branded-v2.mp4" 2>&1 | tail -3

popd >/dev/null

ffprobe -v error -select_streams v:0 -show_entries stream=width,height,duration -of csv=p=0 "$DIR/clip-branded-v2.mp4"

# ============================================================
# Step 2: Build FINAL-reel-v3.mp4 = cover + branded clip + ending CTA
#         with seamless crossfades
# ============================================================
echo
echo ">>> Building final reel with crossfades..."

CLIP="$DIR/clip-branded-v2.mp4"
CLIP_DUR=$(ffprobe -v error -select_streams v:0 -show_entries stream=duration -of csv=p=0 "$CLIP")
OFF1=$(awk 'BEGIN{printf "%.3f", 3.0 - 0.5}')
OFF2=$(awk -v cl=$CLIP_DUR 'BEGIN{printf "%.3f", 3.0 + cl - 0.5 - 0.8}')

ffmpeg -y \
  -loop 1 -t 3.0 -i "$DIR/cover-options/a1-magazine.png" \
  -i "$CLIP" \
  -loop 1 -t 3.5 -i "$DIR/ending-slide.png" \
  -f lavfi -t 3.0 -i anullsrc=channel_layout=stereo:sample_rate=44100 \
  -f lavfi -t 3.5 -i anullsrc=channel_layout=stereo:sample_rate=44100 \
  -filter_complex "
    [0:v]scale=1080:1920,setsar=1,fps=29.97,format=yuv420p,trim=duration=3.0,setpts=PTS-STARTPTS[v0];
    [1:v]scale=1080:1920,setsar=1,fps=29.97,format=yuv420p,setpts=PTS-STARTPTS[v1];
    [2:v]scale=1080:1920,setsar=1,fps=29.97,format=yuv420p,trim=duration=3.5,setpts=PTS-STARTPTS[v2];
    [v0][v1]xfade=transition=fade:duration=0.5:offset=${OFF1}[v01];
    [v01][v2]xfade=transition=fade:duration=0.8:offset=${OFF2}[vout];
    [3:a]asetpts=PTS-STARTPTS[a0];
    [1:a]aresample=44100,asetpts=PTS-STARTPTS[a1];
    [4:a]asetpts=PTS-STARTPTS[a2];
    [a0][a1]acrossfade=d=0.5[a01];
    [a01][a2]acrossfade=d=0.8[aout]
  " \
  -map "[vout]" -map "[aout]" \
  -c:v libx264 -preset medium -crf 20 \
  -profile:v high -level 4.0 -pix_fmt yuv420p \
  -c:a aac -b:a 128k -movflags +faststart \
  "$DIR/FINAL-reel-v3.mp4" 2>&1 | tail -3

echo
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,duration -of csv=p=0 "$DIR/FINAL-reel-v3.mp4"
