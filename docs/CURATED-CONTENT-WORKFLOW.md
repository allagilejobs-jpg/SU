# Curated Content Carousel Workflow

Create Instagram carousels for Spectrum Unlocked by repurposing celebrity autism interview clips. Format inspired by @autism_feed on Instagram.

---

## Overview

**What this creates:**
- Slide 1: Static cover image (1080x1350) with photo + headline
- Slide 2+: Video clip(s) (1080x1920) with branding overlay

**Tools needed:**
- yt-dlp (video download)
- Whisper (transcription)
- ffmpeg (video processing)
- Playwright (HTML → PNG rendering)

---

## Step-by-Step Process

### Step 1: Download Source Video

```bash
yt-dlp -f best -o "/tmp/video_name.mp4" "YOUTUBE_URL"
```

**Example:**
```bash
yt-dlp -f best -o "/tmp/ot_genasis.mp4" "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

---

### Step 2: Transcribe to Find Best Clip

```bash
/Users/aramide/Library/Python/3.9/bin/whisper /tmp/video.mp4 --model base --output_format srt --output_dir /tmp
```

Search for key moments:
```bash
grep -i -n "autism\|diagnos\|spectrum" /tmp/video.srt
```

View context around a line:
```bash
sed -n '30,60p' /tmp/video.srt
```

**Tip:** Look for emotional moments, key quotes, or turning points in the conversation.

---

### Step 3: Trim the Best Clip

```bash
ffmpeg -y -i /tmp/video.mp4 -ss 00:04:27 -t 00:01:28 -c copy /path/to/clip.mp4
```

**Parameters:**
- `-ss 00:04:27` = Start time (HH:MM:SS)
- `-t 00:01:28` = Duration (1 min 28 sec)
- `-c copy` = Copy without re-encoding (fast)

**Ideal clip length:** 30-90 seconds for Reels

---

### Step 4: Pad to 9:16 Vertical (IMPORTANT!)

**DO NOT CROP** - cropping cuts off people in interview videos!

Use **padding** to keep the full video visible:

```bash
ffmpeg -y -i clip.mp4 \
  -vf "scale=1080:-1,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=#1a1a2e" \
  -c:a copy \
  vertical.mp4
```

**What this does:**
1. `scale=1080:-1` - Scale width to 1080, keep aspect ratio
2. `pad=1080:1920:...` - Add dark padding to make 9:16
3. `(ow-iw)/2:(oh-ih)/2` - Center the video
4. `color=#1a1a2e` - Dark background color (matches Spectrum Unlocked brand)
5. `-c:a copy` - Keeps original audio

**Result:** Full video visible with dark bars above/below

---

### Step 5: Create Branding Overlay

Create an HTML file with green screen background for chroma key compositing.

**brand-overlay.html:**
```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600;700;800;900&display=swap" rel="stylesheet">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      width: 1080px;
      height: 1920px;
      background: #00ff00; /* GREEN SCREEN - will be keyed out */
      font-family: 'Poppins', sans-serif;
      position: relative;
    }
    .brand {
      position: absolute;
      top: 60px;
      left: 50px;
    }
    .brand-main {
      font-size: 28px;
      font-weight: 900;
      color: white;
      letter-spacing: 1px;
      text-shadow: 2px 2px 6px rgba(0,0,0,0.8);
    }
    .brand-sub {
      font-size: 20px;
      font-weight: 700;
      color: #4A90A4;
      letter-spacing: 1px;
      text-shadow: 2px 2px 6px rgba(0,0,0,0.8);
    }
    .headline-box {
      position: absolute;
      top: 160px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(255, 255, 255, 0.95);
      padding: 18px 30px;
      border-radius: 8px;
      max-width: 950px;
      text-align: center;
      box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    .headline {
      font-size: 24px;
      font-weight: 800;
      color: #1a1a2e;
      line-height: 1.35;
    }
    .credit {
      position: absolute;
      bottom: 100px;
      left: 50%;
      transform: translateX(-50%);
      font-size: 20px;
      font-weight: 600;
      color: white;
      text-shadow: 2px 2px 6px rgba(0,0,0,0.8);
    }
  </style>
</head>
<body>
  <div class="brand">
    <div class="brand-main">SPECTRUM</div>
    <div class="brand-sub">UNLOCKED</div>
  </div>
  <div class="headline-box">
    <div class="headline">
      Celebrity Name Opens Up About<br>
      Their Child's Autism Journey
    </div>
  </div>
  <div class="credit">🎥 @username via Source</div>
</body>
</html>
```

**Render to PNG:**
```bash
npx playwright screenshot --viewport-size=1080,1920 brand-overlay.html brand-overlay.png
```

---

### Step 6: Composite Overlay onto Video

Use chroma key (colorkey) to remove green background and overlay branding:

```bash
ffmpeg -y -i vertical.mp4 -i brand-overlay.png \
  -filter_complex "[1:v]colorkey=0x00ff00:0.3:0.2[overlay];[0:v][overlay]overlay=0:0" \
  -c:v libx264 -preset fast -crf 22 -c:a aac -b:a 192k \
  -movflags +faststart \
  FINAL.mp4
```

**Parameters:**
- `colorkey=0x00ff00:0.3:0.2` - Remove green (#00ff00) with similarity 0.3, blend 0.2
- `-preset fast` - Encoding speed
- `-crf 22` - Quality (lower = better, 18-28 is good)
- `-movflags +faststart` - Optimize for web streaming

---

### Step 7: Create Static Cover Slide (Slide 1)

**Extract a frame from the video:**
```bash
ffmpeg -y -i vertical.mp4 -ss 00:00:30 -vframes 1 cover-photo.png
```

**Create cover-slide.html (1080x1350):**
```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600;700;800;900&display=swap" rel="stylesheet">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      width: 1080px;
      height: 1350px;
      background: #0a0a12;
      font-family: 'Poppins', sans-serif;
      position: relative;
      overflow: hidden;
    }
    .main-photo {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 850px;
      background: url('cover-photo.png') center center / cover no-repeat;
    }
    .photo-overlay {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 850px;
      background: linear-gradient(180deg, 
        rgba(0,0,0,0.3) 0%, 
        rgba(0,0,0,0) 30%,
        rgba(0,0,0,0) 60%,
        rgba(10,10,18,1) 100%);
    }
    .brand {
      position: absolute;
      top: 40px;
      left: 40px;
      z-index: 10;
    }
    .brand-main {
      font-size: 26px;
      font-weight: 900;
      color: white;
      letter-spacing: 1px;
      text-shadow: 2px 2px 8px rgba(0,0,0,0.8);
    }
    .brand-sub {
      font-size: 18px;
      font-weight: 700;
      color: #4A90A4;
      background: rgba(0,0,0,0.4);
      padding: 2px 8px;
      display: inline-block;
    }
    .slide-num {
      position: absolute;
      top: 40px;
      right: 40px;
      background: rgba(0,0,0,0.6);
      padding: 8px 16px;
      border-radius: 20px;
      font-size: 18px;
      font-weight: 600;
      color: white;
    }
    .headline-section {
      position: absolute;
      bottom: 100px;
      left: 40px;
      right: 40px;
    }
    .name {
      font-size: 36px;
      font-weight: 800;
      color: #E8B86D;
      margin-bottom: 15px;
      text-shadow: 2px 2px 8px rgba(0,0,0,0.8);
    }
    .headline {
      font-size: 44px;
      font-weight: 900;
      color: white;
      line-height: 1.15;
      text-transform: uppercase;
      text-shadow: 2px 2px 8px rgba(0,0,0,0.8);
    }
    .swipe {
      position: absolute;
      bottom: 40px;
      right: 40px;
      width: 70px;
      height: 35px;
      border: 2px solid rgba(255,255,255,0.6);
      border-radius: 20px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: rgba(255,255,255,0.6);
      font-size: 20px;
    }
  </style>
</head>
<body>
  <div class="main-photo"></div>
  <div class="photo-overlay"></div>
  
  <div class="brand">
    <div class="brand-main">SPECTRUM</div>
    <div class="brand-sub">UNLOCKED</div>
  </div>
  
  <div class="slide-num">1/2</div>
  
  <div class="headline-section">
    <div class="name">CELEBRITY NAME</div>
    <div class="headline">
      POWERFUL QUOTE<br>
      OR HEADLINE
    </div>
  </div>
  
  <div class="swipe">→</div>
</body>
</html>
```

**Render:**
```bash
npx playwright screenshot --viewport-size=1080,1350 cover-slide.html cover-slide.png
```

---

### Step 8: Compress for Telegram/Social (if needed)

If file is over 16MB:

```bash
ffmpeg -y -i FINAL.mp4 \
  -c:v libx264 -preset medium -crf 30 -c:a aac -b:a 128k \
  -movflags +faststart \
  compressed.mp4
```

**Compression tips:**
- CRF 28-32 for smaller files
- Lower audio bitrate (96k-128k)
- Use `-preset slow` for better quality at same size

---

## File Structure

```
/Users/aramide/clawd/SU/content/curated/[celebrity-name]/
├── clip.mp4              # Trimmed original clip
├── vertical.mp4          # Cropped to 9:16
├── brand-overlay.html    # Branding overlay source
├── brand-overlay.png     # Rendered overlay (green screen)
├── FINAL.mp4             # Video with branding composited
├── cover-photo.png       # Frame extracted for cover
├── cover-slide.html      # Cover slide source
└── cover-slide.png       # Static cover image (Slide 1)
```

---

## Quick Reference Commands

```bash
# Full pipeline example for "celebrity-name"

# 1. Download
yt-dlp -f best -o "/tmp/celeb.mp4" "YOUTUBE_URL"

# 2. Transcribe
/Users/aramide/Library/Python/3.9/bin/whisper /tmp/celeb.mp4 --model base --output_format srt --output_dir /tmp

# 3. Find best moment
grep -i -n "autism" /tmp/celeb.srt

# 4. Trim (adjust times)
mkdir -p /Users/aramide/clawd/SU/content/curated/celeb-name
ffmpeg -y -i /tmp/celeb.mp4 -ss 00:02:30 -t 00:01:00 -c copy /Users/aramide/clawd/SU/content/curated/celeb-name/clip.mp4

# 5. Pad to vertical (DO NOT CROP - use padding!)
ffmpeg -y -i clip.mp4 -vf "scale=1080:-1,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=#1a1a2e" -c:a copy vertical.mp4

# 6. Create overlay HTML, then render
npx playwright screenshot --viewport-size=1080,1920 brand-overlay.html brand-overlay.png

# 7. Composite
ffmpeg -y -i vertical.mp4 -i brand-overlay.png \
  -filter_complex "[1:v]colorkey=0x00ff00:0.3:0.2[overlay];[0:v][overlay]overlay=0:0" \
  -c:v libx264 -preset fast -crf 22 -c:a aac -b:a 192k -movflags +faststart FINAL.mp4

# 8. Extract cover frame
ffmpeg -y -i vertical.mp4 -ss 00:00:30 -vframes 1 cover-photo.png

# 9. Create cover HTML, then render
npx playwright screenshot --viewport-size=1080,1350 cover-slide.html cover-slide.png

# 10. Compress if needed
ffmpeg -y -i FINAL.mp4 -c:v libx264 -preset medium -crf 30 -c:a aac -b:a 128k -movflags +faststart compressed.mp4
```

---

## Key Notes

1. **Source captions:** Many interview videos already have captions burned in - no need to add your own!

2. **Dimensions:**
   - Cover slide: 1080x1350 (4:5 ratio for Instagram feed)
   - Video reel: 1080x1920 (9:16 ratio for Reels/TikTok)

3. **Always credit** the original source at the bottom of the overlay

4. **Green screen color:** Use exactly `#00ff00` for clean chroma keying

5. **Ideal clip length:** 30-90 seconds performs best on Reels

---

## Completed Examples

| Celebrity | Quote | Source | Location | Carousel Ready |
|-----------|-------|--------|----------|----------------|
| OT Genasis | "Maybe He Chose You" / "Opens Up About His Son's Autism Diagnosis" | The Therapist (VICELAND) | `content/curated/ot-genasis/` | ✅ Yes |
| Holly Robinson Peete | "Do I Have Autism Still?" (Her son RJ asked) | OWN | `content/curated/holly-peete/` | ✅ Yes |

### Carousel Files (Ready to Post)

**OT Genasis:**
- `carousel-cover-FINAL.png` - Cover slide with SWIPE button
- `carousel-video-FINAL.mp4` - Video with branding (1080x1350, has cover frame)
- `carousel-cta-FINAL.png` - CTA slide

**Holly Robinson Peete:**
- `carousel-cover-FINAL.png` - Cover slide (clarifies it's about her son RJ)
- `carousel-video-FINAL.mp4` - Video with branding (1080x1350, has cover frame)  
- `carousel-cta-FINAL.png` - CTA slide

### Brand Guidelines Learned (2026-04-07)
- **NEVER use puzzle logo (🧩)** - not part of Spectrum Unlocked brand
- Branding: "SPECTRUM" white, "UNLOCKED" teal/green below
- Colors: Navy #1a1a2e, Gold #E8B86D, Teal #4A90A4, Green #5fd4a8
- Fonts: Poppins (primary), Playfair Display (accents)
- Handle: @spectrum_unlocked (with underscore) or @spectrum.unlocked (with dot)

---

## Troubleshooting

**Video too large for Telegram:**
- Increase CRF (28 → 32)
- Lower resolution: add `-vf scale=720:1280` before output

**Chroma key not clean:**
- Ensure overlay background is exactly `#00ff00`
- Adjust colorkey parameters: `colorkey=0x00ff00:0.4:0.3`

**Playwright not rendering fonts:**
- Fonts load from Google Fonts - need internet connection
- Or install fonts locally and reference them

**ffmpeg crop not centered:**
- The formula `crop=ih*9/16:ih` auto-centers
- For manual offset: `crop=w:h:x:y`
