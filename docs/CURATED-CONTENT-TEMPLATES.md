# Curated Content Templates - Spectrum Unlocked

Complete guide for creating curated celebrity autism content for Instagram carousels and reels.

---

## 📐 Format Specifications

| Format | Dimensions | Aspect Ratio | Use Case |
|--------|------------|--------------|----------|
| Carousel | 1080 × 1350 | 4:5 | Multi-slide Instagram posts |
| Reel | 1080 × 1920 | 9:16 | Instagram/TikTok vertical video |

---

## 🎨 Brand Guidelines Reference

### Colors
| Name | Hex | Usage |
|------|-----|-------|
| Deep Navy | #1a1a2e | Primary background |
| Midnight Blue | #16213e | Gradient midpoint |
| Ocean Deep | #0f3460 | Gradient endpoint |
| Gold | #E8B86D | Accents, names, CTAs |
| Teal | #4A90A4 | Links, handle, secondary |

### Fonts
- **Playfair Display** (700, 800) - Headlines, names, quotes
- **Poppins** (400, 600, 700) - Body text, UI elements

### Spacing
- **Edge padding:** 60px
- **Border radius:** 16-20px
- **Section gap:** 40px

### Required Elements
- Brand icon (🧩) + "SPECTRUM / UNLOCKED"
- @spectrum_unlocked handle
- "Swipe →" indicator (carousel)
- Credit line for source
- Decorative circles (gold/teal, 10% opacity)

---

## 📁 Template Files Location

```
/Users/aramide/clawd/SU/content/curated/templates/
├── carousel/
│   ├── cover-template.html      # Cover slide (1080x1350)
│   ├── video-template.html      # Video slide (1080x1350)
│   └── cta-template.html        # CTA slide (1080x1350)
├── reel/
│   └── video-template.html      # Video overlay (1080x1920)
└── assets/
    └── (celebrity photos go here)
```

---

## 🔄 CAROUSEL WORKFLOW (1080x1350)

### Step 1: Download Source Video
```bash
yt-dlp -f best -o "/tmp/[name].mp4" "YOUTUBE_URL"
```

### Step 2: Transcribe & Find Best Clip
```bash
/Users/aramide/Library/Python/3.9/bin/whisper /tmp/[name].mp4 --model base --output_format srt --output_dir /tmp

# Search for key moments
grep -i -n "autism\|diagnos" /tmp/[name].srt
```

### Step 3: Trim Best Clip
```bash
ffmpeg -y -i /tmp/[name].mp4 -ss HH:MM:SS -t DURATION -c copy /path/clip.mp4
```

### Step 4: Download Celebrity Photo
```bash
# From Wikipedia or other source
curl -L -o /path/cover-photo.jpg "IMAGE_URL"
```

### Step 5: Create Cover Slide
1. Copy `templates/carousel/cover-template.html`
2. Edit: celebrity name, headline, photo path
3. Render:
```bash
npx playwright screenshot --viewport-size=1080,1350 cover.html cover.png
```

### Step 6: Create Video Slide
1. Copy `templates/carousel/video-template.html`
2. Edit: celebrity name, headline, credit
3. Render frame:
```bash
npx playwright screenshot --viewport-size=1080,1350 video-frame.html video-frame.png
```

4. Create base video (scaled to fit, NOT stretched):
```bash
ffmpeg -y -i clip.mp4 \
  -vf "scale=960:780:force_original_aspect_ratio=decrease,pad=1080:1350:60:200:color=#1a1a2e" \
  -c:v libx264 -preset fast -crf 23 -c:a copy \
  base-video.mp4
```

5. Composite frame overlay (NO scaling of overlay):
```bash
ffmpeg -y -i base-video.mp4 \
  -i video-frame.png \
  -filter_complex "[1:v]colorkey=0x00ff00:0.4:0.1[frame];[0:v][frame]overlay=0:0" \
  -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k \
  -movflags +faststart \
  final-video.mp4
```

### Step 7: Use CTA Slide
Use the pre-made CTA template: `templates/carousel/cta-template.html`

---

## 🎬 REEL WORKFLOW (1080x1920)

### Steps 1-4: Same as Carousel

### Step 5: Create Video Slide
1. Copy `templates/reel/video-template.html`
2. Edit: celebrity name, headline, credit
3. Render frame:
```bash
npx playwright screenshot --viewport-size=1080,1920 video-frame.html video-frame.png
```

4. Create base video:
```bash
ffmpeg -y -i clip.mp4 \
  -vf "scale=960:1200:force_original_aspect_ratio=decrease,pad=1080:1920:60:200:color=#1a1a2e" \
  -c:v libx264 -preset fast -crf 23 -c:a copy \
  base-video.mp4
```

5. Composite:
```bash
ffmpeg -y -i base-video.mp4 \
  -i video-frame.png \
  -filter_complex "[1:v]colorkey=0x00ff00:0.4:0.1[frame];[0:v][frame]overlay=0:0" \
  -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k \
  -movflags +faststart \
  final-reel.mp4
```

---

## ⚠️ CRITICAL RULES

### Never Stretch Text/Overlays
- HTML templates are created at EXACT target dimensions
- PNG overlays are rendered at EXACT dimensions
- Overlays are composited at position 0,0 with NO scaling
- Only the SOURCE VIDEO is scaled to fit within its designated area

### Video Area Calculations

**Carousel (1080x1350):**
- Total: 1080 × 1350
- Top section: 200px (brand + headline)
- Video area: 960 × 780 (with 60px side padding)
- Video position: x=60, y=200
- Bottom section: 190px (name + credit + handle)

**Reel (1080x1920):**
- Total: 1080 × 1920
- Top section: 280px
- Video area: 960 × 1200
- Video position: x=60, y=280
- Bottom section: 260px

### Green Screen for Overlays
- Use #00ff00 (pure green) for areas where video shows through
- Colorkey settings: `colorkey=0x00ff00:0.4:0.1`
- Overlay is placed AFTER video base is created

---

## 📝 Template Variables

When copying templates, replace these placeholders:

| Placeholder | Example |
|-------------|---------|
| `[CELEBRITY_NAME]` | OT Genasis |
| `[HEADLINE]` | Opens Up About His Son's Autism Diagnosis |
| `[QUOTE]` | "Maybe he chose you" |
| `[CREDIT]` | The Therapist |
| `[PHOTO_PATH]` | cover-photo.jpg |

---

## ✅ Quality Checklist

Before delivering:
- [ ] Dimensions exactly 1080x1350 (carousel) or 1080x1920 (reel)
- [ ] No stretched text or graphics
- [ ] Brand colors correct (#1a1a2e, #E8B86D, #4A90A4)
- [ ] @spectrum_unlocked handle present
- [ ] Credit line for source
- [ ] No green screen flash at video start
- [ ] Video fits within frame, not cropped awkwardly

---

## 📂 Output Structure

```
/Users/aramide/clawd/SU/content/curated/[celebrity-name]/
├── clip.mp4                    # Trimmed source clip
├── cover-photo.jpg             # Celebrity photo
├── carousel/
│   ├── cover.html              # Cover slide source
│   ├── cover.png               # Cover slide rendered
│   ├── video-frame.html        # Video frame source
│   ├── video-frame.png         # Video frame rendered
│   └── FINAL-video.mp4         # Final video slide
├── reel/
│   ├── video-frame.html        # Reel frame source
│   ├── video-frame.png         # Reel frame rendered
│   └── FINAL-reel.mp4          # Final reel
└── captions.md                 # Instagram/TikTok captions
```

---

*Last updated: April 7, 2026*
