#!/bin/bash
# Build script for Life on the Spectrum reel
# Run from inside the reel folder

set -e

cd "$(dirname "$0")"

echo "Step 1: Render slides to PNG (already done — skip if PNGs exist)"
for f in slide-*.html; do
  [ ! -f "${f%.html}.png" ] && npx playwright screenshot --viewport-size=1080,1920 "$f" "${f%.html}.png"
done

echo ""
echo "Step 2: Check required files"
required=(voiceover.mp3 music.mp3 captions.srt)
for f in "${required[@]}"; do
  if [ ! -f "$f" ]; then
    echo "  MISSING: $f"
    echo ""
    echo "Required files before compiling video:"
    echo "  1. voiceover.mp3  - Generated from ElevenLabs (see SCRIPT.md)"
    echo "  2. music.mp3      - Downloaded from Pixabay (see SCRIPT.md)"
    echo "  3. captions.srt   - Already created"
    exit 1
  fi
done

echo "  All files present."
echo ""

echo "Step 3: Build slideshow with voiceover"
ffmpeg -y \
  -loop 1 -t 3 -i slide-01-hook.png \
  -loop 1 -t 3 -i slide-02-doc.png \
  -loop 1 -t 7 -i slide-03-scene.png \
  -loop 1 -t 5 -i slide-04-why.png \
  -loop 1 -t 4 -i slide-05-stats.png \
  -loop 1 -t 5 -i slide-06-cta.png \
  -i voiceover.mp3 \
  -i music.mp3 \
  -filter_complex "\
    [0:v]fps=30,format=yuv420p,fade=t=in:st=0:d=0.3[v0]; \
    [1:v]fps=30,format=yuv420p,fade=t=in:st=0:d=0.3[v1]; \
    [2:v]fps=30,format=yuv420p,fade=t=in:st=0:d=0.4[v2]; \
    [3:v]fps=30,format=yuv420p,fade=t=in:st=0:d=0.3[v3]; \
    [4:v]fps=30,format=yuv420p,fade=t=in:st=0:d=0.3[v4]; \
    [5:v]fps=30,format=yuv420p,fade=t=in:st=0:d=0.3[v5]; \
    [v0][v1][v2][v3][v4][v5]concat=n=6:v=1:a=0[outv]; \
    [6:a]volume=1.0[voice]; \
    [7:a]volume=0.25,aloop=loop=-1:size=2e9[bgm]; \
    [voice][bgm]amix=inputs=2:duration=first:dropout_transition=2,aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo[outa]" \
  -map "[outv]" -map "[outa]" \
  -c:v libx264 -profile:v high -preset medium -crf 18 \
  -c:a aac -b:a 192k -ar 44100 -ac 2 \
  -pix_fmt yuv420p -movflags +faststart \
  -t 27 \
  video-no-captions.mp4

echo ""
echo "Step 4: Burn in captions"
ffmpeg -y \
  -i video-no-captions.mp4 \
  -vf "subtitles=captions.srt:force_style='FontName=Poppins,FontSize=20,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=2,Shadow=1,Alignment=2,MarginV=220,Bold=1'" \
  -c:v libx264 -crf 18 \
  -c:a copy \
  -movflags +faststart \
  FINAL-bbc-africa-autism-reel.mp4

echo ""
echo "DONE!"
echo "Output: FINAL-bbc-africa-autism-reel.mp4"
echo "Upload to Instagram Reels, TikTok, YouTube Shorts."
