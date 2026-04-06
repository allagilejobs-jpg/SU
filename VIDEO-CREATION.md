# VIDEO-CREATION.md - Reel Production Guide

**Last Updated:** April 5, 2026

Two methods for creating video reels from slide templates.

---

# Method 1: Voiceover Reel with Captions

Full narrated video with burned-in subtitles. Best for educational content.

**Example:** Sensory Hacks TikTok (`/Monthly/su/tiktok/`)

## What You Get
- MP4 video (1080x1920)
- Voiceover narration synced to slides
- Burned-in captions/subtitles
- Ready for TikTok/Instagram Reels

## Required Tools
- Playwright (HTML → PNG)
- ElevenLabs API (text → speech)
- FFmpeg (video compilation + captions)

---

## Step 1: Create Slide Templates

Create HTML templates at 1080x1920:

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap" rel="stylesheet">
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
  </style>
</head>
<body>
  <div class="slide">
    <!-- Content -->
  </div>
</body>
</html>
```

---

## Step 2: Render to PNG

```bash
# Single slide
npx playwright screenshot --viewport-size=1080,1920 slide.html slide.png

# All slides
for f in slide-*.html; do
  npx playwright screenshot --viewport-size=1080,1920 "$f" "${f%.html}.png"
done
```

---

## Step 3: Write Script with Timestamps

```markdown
# Sensory Hacks Script

**Cover (0:00-0:03)**
"Sensory hacks that actually work"

**Slide 1 - Headphones (0:03-0:16)**
"Number one: Noise-canceling headphones. These are a game-changer 
for overwhelming environments like grocery stores, restaurants, or 
school assemblies. Keep a pair in your bag at all times."

**Slide 2 - Sunglasses (0:16-0:26)**
"Number two: Sunglasses indoors. Fluorescent lights can be torture 
for sensitive eyes. Tinted glasses aren't being dramatic, they're survival."

**Slide 3 - Fidgets (0:26-0:33)**
"Number three: Fidgets in your pocket. Quiet fidgets help with 
focus and regulation without drawing attention."

**Slide 4 - Chewing (0:33-0:52)**
"Number four: Chewing. Chewing provides proprioceptive input that 
calms the nervous system. Try gum, chewy snacks, or silicone chew 
jewelry. Save this and follow for more sensory tips!"

**Total: ~52 seconds**
```

---

## Step 4: Generate Voiceover

Use ElevenLabs to generate MP3:

```bash
# Via Clawdbot TTS or ElevenLabs API
# Save as: voiceover.mp3
```

**Recommended settings:**
- Voice: Warm, conversational
- Stability: 0.5
- Clarity: 0.75

---

## Step 5: Create Captions File (SRT)

Create `captions.srt`:

```srt
1
00:00:00,000 --> 00:00:03,000
Sensory hacks that actually work

2
00:00:03,000 --> 00:00:08,000
Number one: Noise-canceling headphones.

3
00:00:08,000 --> 00:00:12,000
These are a game-changer for
overwhelming environments

4
00:00:12,000 --> 00:00:16,000
Keep a pair in your bag at ALL times.

5
00:00:16,000 --> 00:00:20,000
Number two: Sunglasses indoors.

6
00:00:20,000 --> 00:00:26,000
Fluorescent lights can be torture.
Tinted glasses aren't dramatic, they're survival.
```

---

## Step 6: Calculate Slide Timings

Listen to voiceover and note timestamps:

| Slide | Start | End | Duration |
|-------|-------|-----|----------|
| Cover | 0:00 | 0:03 | 3s |
| Slide 1 | 0:03 | 0:16 | 13s |
| Slide 2 | 0:16 | 0:26 | 10s |
| Slide 3 | 0:26 | 0:33 | 7s |
| Slide 4 | 0:33 | 0:52 | 19s |

---

## Step 7: Compile Video with Voiceover

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
  -c:v libx264 -profile:v high -preset medium -crf 18 \
  -c:a aac -b:a 192k -ar 44100 -ac 2 \
  -pix_fmt yuv420p -movflags +faststart \
  -shortest \
  video-with-voiceover.mp4
```

---

## Step 8: Burn In Captions

```bash
ffmpeg -y \
  -i video-with-voiceover.mp4 \
  -vf "subtitles=captions.srt:force_style='FontName=Poppins,FontSize=24,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=2,Shadow=1,Alignment=2,MarginV=100'" \
  -c:v libx264 -crf 18 \
  -c:a copy \
  -movflags +faststart \
  FINAL-with-captions.mp4
```

**Caption styling options:**
- `FontSize=24` — Adjust size
- `PrimaryColour=&HFFFFFF` — White text
- `OutlineColour=&H000000` — Black outline
- `Outline=2` — Outline thickness
- `MarginV=100` — Distance from bottom (avoid UI overlap)

---

## Folder Structure

```
project-folder/
├── templates/
│   ├── cover.html
│   ├── slide-01.html
│   └── ...
├── graphics/
│   ├── cover.png
│   ├── slide-01.png
│   └── ...
├── script.md
├── voiceover.mp3
├── captions.srt
├── video-with-voiceover.mp4
└── FINAL-with-captions.mp4
```

---

# Method 2: Background Music Reel

Slideshow with background music, no voiceover. Best for emotional/visual content.

**Example:** Day 8 WAAD Reel (`/SU/content/day-08-waad-reel/`)

## What You Get
- MP4 video (1080x1920)
- Background music track
- Even slide timing (no narration to sync)
- Ready for TikTok/Instagram Reels

## Required Tools
- Playwright (HTML → PNG)
- FFmpeg (video compilation)
- Royalty-free music file

---

## Step 1: Create & Render Slides

Same as Method 1 — create HTML templates, render to PNG.

```bash
for f in slide-*.html; do
  npx playwright screenshot --viewport-size=1080,1920 "$f" "${f%.html}.png"
done
```

---

## Step 2: Get Background Music

### Royalty-Free Music Sources

#### 1. Pixabay Music (FREE - No Attribution Required)
**URL:** https://pixabay.com/music/

**Why use it:**
- 100% free for commercial use
- No attribution required
- No sign-up needed to download
- Large library of high-quality tracks

**How to use:**
1. Go to https://pixabay.com/music/
2. Use search: "inspiring piano", "emotional", "uplifting", "corporate"
3. Filter by: Mood, Genre, Duration
4. Click track to preview
5. Click "Download" → Choose quality (MP3)
6. Save to your project folder

**Best search terms for Spectrum Unlocked:**
- "inspiring piano" - emotional/awareness content
- "gentle acoustic" - soft educational content
- "uplifting corporate" - professional feel
- "emotional cinematic" - impactful moments
- "soft ambient" - calm, supportive content

---

#### 2. Uppbeat (FREE Tier Available)
**URL:** https://uppbeat.io/

**Why use it:**
- Curated for content creators
- High-quality tracks
- 10 free downloads/month (free tier)
- Clear licensing

**How to use:**
1. Create free account at uppbeat.io
2. Browse by mood/genre
3. Download (credits refresh monthly)
4. Attribution required for free tier

---

#### 3. YouTube Audio Library (FREE)
**URL:** https://studio.youtube.com/channel/audio

**Why use it:**
- Free for any YouTube/social content
- Large selection
- Filter by mood, genre, duration
- Some require attribution, some don't

**How to use:**
1. Sign into YouTube Studio
2. Go to Audio Library (left menu)
3. Filter: Free Music → Mood → Duration
4. Check license (attribution required?)
5. Download MP3

---

#### 4. Epidemic Sound (PAID - Best Quality)
**URL:** https://www.epidemicsound.com/

**Why use it:**
- Highest quality library
- Used by major creators
- Full commercial license
- $15/month personal plan

---

#### 5. Artlist (PAID - Unlimited)
**URL:** https://artlist.io/

**Why use it:**
- Unlimited downloads
- High-quality cinematic music
- Full commercial license
- ~$10/month billed annually

---

#### 6. TikTok/Instagram Built-In Music
**When to use:**
- Quick posts without custom video
- Want trending sounds
- Don't need external video file

**How to use:**
1. Upload your video (without music)
2. Add sound from TikTok/Instagram library
3. Sync timing in app
4. Post directly

**Limitation:** Can't download video with this audio

---

### Music Selection Guide

| Content Type | Mood | Search Terms |
|--------------|------|--------------|
| Awareness days | Emotional, hopeful | "inspiring piano", "emotional cinematic" |
| Educational | Calm, focused | "soft ambient", "gentle acoustic" |
| Tips/hacks | Upbeat, energetic | "uplifting corporate", "positive" |
| Personal stories | Emotional, intimate | "sad piano", "emotional strings" |
| Celebrations | Happy, triumphant | "happy upbeat", "celebration" |

### Duration Matching

For a 24-second video (6 slides × 4 seconds):
- Find music 25-60 seconds long
- FFmpeg `-shortest` flag will trim to video length
- Longer tracks work fine (auto-trimmed)

### File Format
- Download as **MP3** (most compatible)
- Bitrate: 192kbps or higher
- Save to project folder as: `background-music.mp3` or descriptive name like `inspiring-piano.mp3`

---

### Example: Day 8 WAAD Music
**File:** `inspiring-piano.mp3`
**Source:** Pixabay Music
**Search term:** "inspiring piano"
**Duration:** 79 seconds (trimmed to 24s by FFmpeg)
**License:** Free, no attribution required

---

## Step 3: Create Slideshow Video

With even timing (e.g., 4 seconds per slide):

```bash
ffmpeg -y \
  -loop 1 -t 4 -i slide-01-cover.png \
  -loop 1 -t 4 -i slide-02-humanity.png \
  -loop 1 -t 4 -i slide-03-value.png \
  -loop 1 -t 4 -i slide-04-acceptance.png \
  -loop 1 -t 4 -i slide-05-pledge.png \
  -loop 1 -t 4 -i slide-06-cta.png \
  -filter_complex "\
    [0:v]fps=30,format=yuv420p[v0]; \
    [1:v]fps=30,format=yuv420p[v1]; \
    [2:v]fps=30,format=yuv420p[v2]; \
    [3:v]fps=30,format=yuv420p[v3]; \
    [4:v]fps=30,format=yuv420p[v4]; \
    [5:v]fps=30,format=yuv420p[v5]; \
    [v0][v1][v2][v3][v4][v5]concat=n=6:v=1:a=0[outv]" \
  -map "[outv]" \
  -c:v libx264 -profile:v high -preset medium -crf 18 \
  -pix_fmt yuv420p -movflags +faststart \
  slideshow.mp4
```

---

## Step 4: Add Background Music

```bash
ffmpeg -y \
  -i slideshow.mp4 \
  -i inspiring-piano.mp3 \
  -c:v copy \
  -c:a aac -b:a 192k -ar 44100 -ac 2 \
  -shortest \
  -movflags +faststart \
  FINAL-with-music.mp4
```

**Note:** `-shortest` ends video when the shorter stream ends (matches music to video length or vice versa).

---

## Slide Timing Guidelines

| Content Type | Timing | Total (6 slides) |
|--------------|--------|------------------|
| Inspirational | 4-5s each | 24-30s |
| Educational | 5-6s each | 30-36s |
| Quick tips | 3-4s each | 18-24s |
| Emotional | 5-7s each | 30-42s |

---

## Folder Structure

```
day-08-waad-reel/
├── slide-01-cover.html
├── slide-01-cover.png
├── slide-02-humanity.html
├── slide-02-humanity.png
├── ...
├── inspiring-piano.mp3
├── slideshow.mp4
├── FINAL-with-music.mp4
└── captions.md
```

---

# Video Specifications (Both Methods)

| Setting | Value |
|---------|-------|
| Resolution | 1080 x 1920 |
| Aspect Ratio | 9:16 |
| Frame Rate | 30 fps |
| Video Codec | H.264 High Profile |
| CRF | 18 (high quality) |
| Audio Codec | AAC |
| Audio Bitrate | 192 kbps |
| Sample Rate | 44100 Hz |
| Channels | Stereo |

---

# Quick Reference

## Render all slides
```bash
for f in slide-*.html; do npx playwright screenshot --viewport-size=1080,1920 "$f" "${f%.html}.png"; done
```

## Create slideshow (no audio)
```bash
ffmpeg -loop 1 -t 4 -i slide-01.png -loop 1 -t 4 -i slide-02.png ... \
  -filter_complex "concat=n=X:v=1:a=0" -c:v libx264 -crf 18 slideshow.mp4
```

## Add audio to video
```bash
ffmpeg -i video.mp4 -i audio.mp3 -c:v copy -c:a aac -shortest output.mp4
```

## Burn in captions
```bash
ffmpeg -i video.mp4 -vf "subtitles=captions.srt" -c:a copy output.mp4
```

## Check video info
```bash
ffprobe -v quiet -print_format json -show_format -show_streams video.mp4
```

---

# When to Use Each Method

| Method | Best For | Examples |
|--------|----------|----------|
| **Voiceover + Captions** | Educational content, tutorials, tips, explainers | Sensory Hacks, IEP tips, Sleep strategies |
| **Background Music** | Emotional content, awareness days, visual stories | WAAD, acceptance pledges, community spotlights |

---

# Method 3: Karaoke-Style Captions

Word-by-word animated captions where each word highlights as it's spoken. Premium TikTok style.

**Example:** Sensory Hacks with karaoke captions (`/Monthly/su/tiktok/captioned/`)

## What You Get
- MP4 video with animated word-by-word captions
- Current word highlighted in gold with glow
- Spoken words turn white
- Upcoming words dimmed
- Synced perfectly to voiceover

---

## The Karaoke Style

### Caption Styling
```css
/* Current word (highlighted) */
color: #E8B86D;
font-weight: 800;
transform: scale(1.1);
display: inline-block;
text-shadow: 0 0 30px rgba(232,184,109,0.6);

/* Already spoken words */
color: white;

/* Upcoming words (not yet spoken) */
color: rgba(255,255,255,0.4);
```

### Visual Effect
```
"Keep noise-canceling headphones in your bag"
      ↓ (word 3 highlighted)
"Keep noise-canceling HEADPHONES in your bag"
                      ^^^^^^^^
                      Gold + Glow + Scaled
```

---

## Process Overview

1. **Transcribe voiceover** → Get word-level timestamps
2. **Create phrase segments** → Group words by timing
3. **Generate frames** → One PNG per word state
4. **Concat with FFmpeg** → Stitch frames + audio

---

## Step 1: Define Phrases with Timing

Create a phrases array with start/end times and words:

```javascript
const phrases = [
  { start: 0, end: 3, slide: 'cover', words: ['Sensory', 'hacks', 'that', 'actually', 'work.'] },
  { start: 3, end: 4, slide: 'slide1', words: ['Number', 'one.'] },
  { start: 4, end: 9, slide: 'slide1', words: ['Keep', 'noise-canceling', 'headphones', 'in', 'your', 'bag', 'at', 'all', 'times.'] },
  // ... more phrases
];
```

---

## Step 2: Word Highlight Function

```javascript
function generateWordHTML(words, highlightIndex) {
  return words.map((word, i) => {
    if (i === highlightIndex) {
      // Current word - gold with glow
      return `<span style="color:#E8B86D;font-weight:800;transform:scale(1.1);display:inline-block;text-shadow:0 0 30px rgba(232,184,109,0.6);">${word}</span>`;
    } else if (i < highlightIndex) {
      // Already spoken - white
      return `<span style="color:white;">${word}</span>`;
    } else {
      // Upcoming - dimmed
      return `<span style="color:rgba(255,255,255,0.4);">${word}</span>`;
    }
  }).join(' ');
}
```

---

## Step 3: Generate Frame HTML

```javascript
function generateHTML(slideContent, wordsHTML) {
  return `<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800;900&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{
  width:1080px;
  height:1920px;
  font-family:'Poppins',sans-serif;
  color:white;
  background:linear-gradient(165deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%);
  position:relative;
}
.caption-area{
  position:absolute;
  bottom:300px;
  left:60px;
  right:60px;
  text-align:center;
}
.caption-text{
  font-size:48px;
  font-weight:600;
  line-height:1.6;
  text-shadow:3px 3px 8px rgba(0,0,0,0.9);
}
</style></head>
<body>
${slideContent}
<div class="caption-area">
  <div class="caption-text">${wordsHTML}</div>
</div>
</body></html>`;
}
```

---

## Step 4: Render All Frames

```javascript
const { chromium } = require('playwright');

async function renderFrames() {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1080, height: 1920 });
  
  let segments = [];
  let segNum = 0;
  
  for (const phrase of phrases) {
    const duration = phrase.end - phrase.start;
    const secPerWord = duration / phrase.words.length;
    
    for (let wordIdx = 0; wordIdx < phrase.words.length; wordIdx++) {
      const wordsHTML = generateWordHTML(phrase.words, wordIdx);
      const html = generateHTML(slideContents[phrase.slide], wordsHTML);
      
      // Save HTML
      fs.writeFileSync(`karaoke/seg_${segNum}.html`, html);
      
      // Screenshot
      await page.goto('file://' + `karaoke/seg_${segNum}.html`);
      await page.screenshot({ path: `karaoke/seg_${segNum}.png` });
      
      segments.push({ file: `seg_${segNum}.png`, duration: secPerWord });
      segNum++;
    }
  }
  
  await browser.close();
  return segments;
}
```

---

## Step 5: Generate FFmpeg Concat File

```javascript
function generateConcatFile(segments) {
  let concat = '';
  segments.forEach(seg => {
    concat += `file 'karaoke/${seg.file}'\n`;
    concat += `duration ${seg.duration}\n`;
  });
  // Add last file again (ffmpeg quirk)
  concat += `file 'karaoke/${segments[segments.length-1].file}'\n`;
  
  fs.writeFileSync('concat.txt', concat);
}
```

**concat.txt example:**
```
file 'karaoke/seg_0.png'
duration 0.6
file 'karaoke/seg_1.png'
duration 0.6
file 'karaoke/seg_2.png'
duration 0.6
...
```

---

## Step 6: Compile Video with FFmpeg

```bash
ffmpeg -y \
  -f concat -safe 0 -i concat.txt \
  -i voiceover.mp3 \
  -c:v libx264 -profile:v high -preset medium -crf 18 \
  -c:a aac -b:a 192k \
  -pix_fmt yuv420p \
  -movflags +faststart \
  -shortest \
  karaoke-output.mp4
```

---

## Folder Structure

```
captioned/
├── generate-karaoke-v2.js    # Main script
├── karaoke/                   # Generated frames
│   ├── seg_000.html
│   ├── seg_000.png
│   ├── seg_001.html
│   ├── seg_001.png
│   └── ...
├── concat.txt                 # FFmpeg concat file
├── voiceover.mp3              # Audio
└── karaoke-output.mp4         # Final video
```

---

## Quick Run Commands

```bash
# Install dependencies
npm install playwright
npx playwright install chromium

# Generate frames
node generate-karaoke-v2.js

# Compile video
ffmpeg -f concat -safe 0 -i concat.txt -i voiceover.mp3 \
  -c:v libx264 -c:a aac -shortest karaoke-output.mp4
```

---

## Tips

1. **Timing accuracy** — Get word-level timestamps from Whisper or manual transcription
2. **Font size** — 48px works well for readability on mobile
3. **Caption position** — `bottom: 300px` keeps captions above TikTok UI
4. **Glow intensity** — Adjust `text-shadow` blur radius for more/less glow
5. **Frame count** — Expect 50-100+ frames for a 30-60 second video

---

## When to Use Karaoke Style

| Use Karaoke | Use Regular Captions |
|-------------|---------------------|
| High-production content | Quick turnaround |
| Educational explainers | Simple tips |
| Trending audio remakes | Background music reels |
| Want premium look | Time-constrained |

---

*Karaoke captions take more effort but create highly engaging, premium-feeling content.*

---

*All three methods create professional TikTok/Instagram Reels from static slide templates.*
