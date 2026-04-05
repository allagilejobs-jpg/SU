# VIDEO-CREATION.md - TikTok/Reel Video Production

**Last Updated:** April 5, 2026

This documents the complete process for creating actual video reels (MP4) with voiceover and captions for Spectrum Unlocked.

---

## Overview

**What this creates:**
- MP4 video files (1080x1920, 9:16)
- Voiceover narration (ElevenLabs TTS)
- Timed slides synced to audio
- Ready to upload to TikTok/Instagram Reels

**What you need:**
- HTML slide templates (1080x1920)
- Playwright (for screenshots)
- ElevenLabs API (for voiceover)
- FFmpeg (for video compilation)

---

## Step-by-Step Process

### Step 1: Create HTML Slide Templates

Create slide templates at 1080x1920 (9:16 vertical):

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800;900&display=swap" rel="stylesheet">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    .slide {
      width: 1080px;
      height: 1920px;
      background: linear-gradient(165deg, #1a1a2e 0%, #16213e 40%, #0f3460 100%);
      padding: 80px 60px;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      font-family: 'Poppins', sans-serif;
      color: white;
      text-align: center;
    }
    /* Add slide-specific styles */
  </style>
</head>
<body>
  <div class="slide">
    <!-- Slide content -->
  </div>
</body>
</html>
```

### Step 2: Render HTML to PNG

```bash
# Single slide
npx playwright screenshot --viewport-size=1080,1920 slide.html slide.png

# All slides in folder
for f in slide-*.html; do
  npx playwright screenshot --viewport-size=1080,1920 "$f" "${f%.html}.png"
done
```

### Step 3: Write the Script

Create a script with timestamps for each slide:

```markdown
# Sensory Hacks Script

**Cover (0:00-0:03)**
"Sensory hacks that actually work"

**Slide 1 - Headphones (0:03-0:16)**
"Number one: Noise-canceling headphones. These are a game-changer for overwhelming environments like grocery stores, restaurants, or school assemblies. Keep a pair in your bag at all times."

**Slide 2 - Sunglasses (0:16-0:26)**
"Number two: Sunglasses indoors. Fluorescent lights can be torture for sensitive eyes. Tinted glasses or sunglasses aren't being dramatic - they're survival."

**Slide 3 - Fidgets (0:26-0:33)**
"Number three: Fidgets in your pocket. Quiet fidgets help with focus and regulation without drawing attention."

**Slide 4 - Chewing (0:33-0:52)**
"Number four: Chewing. Chewing provides proprioceptive input that calms the nervous system. Try gum, chewy snacks, or silicone chew jewelry. Save this and follow for more sensory tips!"

**Total: ~52 seconds**
```

### Step 4: Generate Voiceover (ElevenLabs)

Use ElevenLabs TTS to generate the voiceover MP3:

```bash
# Via Clawdbot TTS tool or ElevenLabs API
# Save as: voiceover.mp3
```

**Voice settings:**
- Voice: Choose a warm, conversational voice
- Stability: 0.5
- Clarity: 0.75

### Step 5: Calculate Slide Timings

Listen to the voiceover and note exact timestamps for each slide transition:

| Slide | Start | End | Duration |
|-------|-------|-----|----------|
| Cover | 0:00 | 0:03 | 3s |
| Slide 1 | 0:03 | 0:16 | 13s |
| Slide 2 | 0:16 | 0:26 | 10s |
| Slide 3 | 0:26 | 0:33 | 7s |
| Slide 4 | 0:33 | 0:52 | 19s |

### Step 6: Compile Video with FFmpeg

```bash
ffmpeg -y \
  -loop 1 -t 3 -i cover.png \
  -loop 1 -t 13 -i slide-01.png \
  -loop 1 -t 10 -i slide-02.png \
  -loop 1 -t 7 -i slide-03.png \
  -loop 1 -t 19 -i slide-04.png \
  -i voiceover.mp3 \
  -filter_complex "\
    [0:v]fps=30,format=yuv420p[v0]; \
    [1:v]fps=30,format=yuv420p[v1]; \
    [2:v]fps=30,format=yuv420p[v2]; \
    [3:v]fps=30,format=yuv420p[v3]; \
    [4:v]fps=30,format=yuv420p[v4]; \
    [v0][v1][v2][v3][v4]concat=n=5:v=1:a=0[outv]; \
    [5:a]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo[outa]" \
  -map "[outv]" -map "[outa]" \
  -c:v libx264 -profile:v high -level 4.2 -preset medium -crf 18 \
  -c:a aac -b:a 192k -ar 44100 -ac 2 \
  -pix_fmt yuv420p -movflags +faststart \
  -shortest \
  output-FINAL.mp4
```

**Command breakdown:**
- `-loop 1 -t X -i image.png` — Loop image for X seconds
- `-filter_complex` — Process and concatenate video streams
- `fps=30,format=yuv420p` — 30fps, standard color format
- `concat=n=5:v=1:a=0` — Concatenate 5 video inputs, no audio concat
- `-c:v libx264 -profile:v high` — H.264 High profile (TikTok compatible)
- `-crf 18` — High quality (lower = better, 18-23 recommended)
- `-c:a aac -b:a 192k` — AAC audio at 192kbps
- `-movflags +faststart` — Optimize for streaming
- `-shortest` — End video when shortest stream ends (matches audio)

---

## Video Specifications

### TikTok/Reels Requirements
| Setting | Value |
|---------|-------|
| Resolution | 1080 x 1920 |
| Aspect Ratio | 9:16 |
| Frame Rate | 30 fps |
| Video Codec | H.264 High Profile |
| Audio Codec | AAC |
| Audio Sample Rate | 44100 Hz |
| Audio Channels | Stereo |
| Audio Bitrate | 192 kbps |
| Ideal Length | 30-60 seconds |

### Quality Settings
| Setting | Value | Notes |
|---------|-------|-------|
| CRF | 18 | Lower = better quality, larger file |
| Preset | medium | Balance of speed/quality |
| Level | 4.2 | Broad compatibility |

---

## Folder Structure

```
content/day-XX-topic-reel/
├── slide-01-hook.html       # HTML template
├── slide-01-hook.png        # Rendered PNG
├── slide-02-content.html
├── slide-02-content.png
├── ...
├── script.md                # Voiceover script with timestamps
├── voiceover.mp3            # ElevenLabs audio
├── captions.md              # Social media captions
└── day-XX-topic-FINAL.mp4   # Final video
```

---

## Adding Captions/Subtitles

### Option 1: Burn-in with FFmpeg

Create an SRT file:
```srt
1
00:00:00,000 --> 00:00:03,000
Sensory hacks that actually work

2
00:00:03,000 --> 00:00:08,000
Number one: Noise-canceling headphones
```

Then burn in:
```bash
ffmpeg -i video.mp4 -vf subtitles=captions.srt output-captioned.mp4
```

### Option 2: Use TikTok/CapCut Auto-Captions
- Upload video to TikTok
- Use built-in auto-caption feature
- Edit for accuracy

---

## Tips & Lessons Learned

1. **Verify PNG format** — Use `file *.png` to confirm they're actual PNGs, not renamed JPEGs

2. **Audio/video sync** — If out of sync, check your slide timings match voiceover timestamps exactly

3. **Cover slide** — Should be 2-3 seconds max, just the intro hook

4. **Transition timing** — Transition to next slide when the voiceover starts talking about it

5. **Test on phone** — Always preview on mobile before posting

6. **File size** — Aim for under 100MB for smooth uploads

7. **Hashtags** — TikTok: 5-8 hashtags, Instagram: 10-15

8. **Best posting times (EST):**
   - Morning: 7-9 AM
   - Lunch: 12-2 PM
   - Evening: 7-10 PM

---

## Quick Reference Commands

```bash
# Render all slides
for f in slide-*.html; do npx playwright screenshot --viewport-size=1080,1920 "$f" "${f%.html}.png"; done

# Check video info
ffprobe -v quiet -print_format json -show_format -show_streams video.mp4

# Extract audio from existing video
ffmpeg -i video.mp4 -vn -acodec copy audio.aac

# Add audio to slideshow
ffmpeg -i slideshow.mp4 -i audio.mp3 -c:v copy -c:a aac -shortest output.mp4
```

---

## Example Project: Sensory Hacks

**Location:** `/Users/aramide/clawd/Monthly/su/tiktok/`

**Files:**
- `templates/` — HTML slide templates
- `graphics_hd/` — Rendered 1080x1920 PNGs
- `sensory-hacks-voiceover.mp3` — ElevenLabs narration
- `sensory-hacks-script.md` — Script with timestamps
- `caption.md` — Ready-to-post caption
- `sensory-hacks-FINAL.mp4` — Final video

---

*This process creates professional-quality video reels from static slide templates.*
