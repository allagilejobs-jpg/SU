# Spectrum Unlocked — Content Creation Playbook

**End-to-end guide for producing curated autism-parent content: sourcing, decisions, pipeline, troubleshooting.**

This is the canonical document. When in doubt, follow this. When you discover something better, update this.

---

## Table of Contents

1. [TL;DR](#tldr)
2. [Content Categories](#1-content-categories)
3. [Sourcing Content](#2-sourcing-content)
4. [The Journey — What We Tried](#3-the-journey--what-we-tried)
5. [The Final Pipeline](#4-the-final-pipeline)
6. [Reel Build (v3)](#5-reel-build-v3)
7. [Carousel Build (v2)](#6-carousel-build-v2)
8. [Website Integration](#7-website-integration)
9. [Lessons Learned](#8-lessons-learned--bugs-and-root-causes)
10. [New Artist Checklist](#9-new-artist-checklist)
11. [Script Reference](#10-script-reference)
12. [Brand System](#11-brand-system)
13. [Troubleshooting](#12-troubleshooting)

---

## TL;DR

Produce a **single Instagram Reel (1080×1920, vertical)** and a **single Instagram Carousel (4 slides, 1080×1350)** from a landscape interview clip of a celebrity talking about their autistic child. Both must be branded (Spectrum Unlocked), captioned (karaoke-style, brand-gold highlight on current word), and ready to post with zero further editing.

**The trick that took the longest to find:** audio/video stream offsets in downloaded MP4s silently break sync when the streams get pulled into a filter graph. Pre-create a clean "synced" source as step 1 of every pipeline, or you'll spend hours debugging lip-sync drift that's really a container-level timing artifact.

**The visual approach that finally worked:** for talking-head interview footage, left-biased or center-biased static crop at a slightly reduced vertical scale (1440 instead of 1920) with blur-fit padding. AI face-tracking (smart reframe) sounds like the right tool but cuts subjects' heads on wide shots. Pure letterbox looks amateur. Blur-fit at full height cuts content off.

---

## 1. Content Categories

The Spectrum Unlocked editorial strategy has the following content types. This playbook currently covers **Curated**. Future sections will cover the others.

| Category | Format | Purpose | Example |
|---|---|---|---|
| **Curated** | Reel + carousel | Repurpose existing TV/podcast clips of celebrities talking about their autistic child | Holly Robinson Peete on OWN, OT Genasis on The Therapist, Faith Evans on Tamron Hall |
| **Original educational** | Carousel only | Teach concepts (IEP, therapies, sensory tools) | "5 sensory hacks that actually work" |
| **Personal stories** | Reel | Founder/creator voice, behind-the-scenes | FJ stories |
| **Seasonal** | Mixed | Tied to calendar events (Autism Month, IEP season) | April campaigns |

Curated content is the **highest-leverage** — existing footage + celebrity social proof + a tight edit + our brand layer = a post that takes hours to make but can run indefinitely.

---

## 2. Sourcing Content

### 2.1 What to look for

A great Curated source has all of:

1. **A real celebrity** — someone whose name has pull in parent Facebook groups (Holly Robinson Peete, OT Genasis, Faith Evans are the current roster). Not a C-list influencer. Not an unknown advocate.
2. **A clear personal autism story** — *their own child*, not "I know someone with autism". Authenticity is the whole point.
3. **At least one quotable moment** — a sentence you could put on a t-shirt. The best ones: *"Do I have autism still?"* *"Maybe he chose you."* *"I had to BEG for a diagnosis."*
4. **TV or podcast origin** — Tamron Hall Show, The Therapist, Red Table Talk, Oprah, etc. Lends credibility.
5. **5–15 minutes of source material** — enough for a best-of cut, not so much that transcription takes forever.
6. **Accessible source footage** — YouTube embed, podcast episode, accessible recording. No DRM walls.

### 2.2 Where to find it

- **YouTube** — by far the most common. Direct downloads via `yt-dlp`.
- **Podcast platforms** — Apple Podcasts, Spotify (audio only; use for voiceover carousels if the footage doesn't exist).
- **Show websites** — sometimes embed an MP4 or Vimeo.
- **Instagram Reels / TikTok clips** — already repurposed, but can be the starting point if the original is unavailable.

### 2.3 Downloading

```bash
python -m yt_dlp \
  -f "bestvideo[height<=720]+bestaudio/best[height<=720]" \
  -o "content/curated/<slug>/_source-landscape.%(ext)s" \
  "<YouTube URL>"
```

Notes:
- **Cap at 720p** — 1080p+ sources are oversized and don't improve the final output (we downscale anyway, and source quality is dominated by the TV broadcast, not the resolution).
- **Merge to MP4** — yt-dlp sometimes hands you `.webm` because audio is Opus. Re-encode to MP4/AAC for pipeline compatibility:
  ```bash
  ffmpeg -i _source-landscape.webm \
    -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
    -c:a aac -b:a 192k -movflags +faststart \
    _source-landscape.mp4
  ```

### 2.4 Fair use / licensing

- Short clips (< 90 seconds) of broadcast interviews used for commentary/education typically fall within fair use on Instagram.
- **Always credit the source** ("via Tamron Hall Show", "via OWN") on the cover slide AND on the brand overlay throughout the clip.
- **Never** reupload entire episodes. Always excerpt with transformation (captions, branding, your commentary in the post caption).
- If a show/network sends a takedown, honor it immediately and pull the post.

---

## 3. The Journey — What We Tried

This section documents the iterative decisions we made building the current pipeline. Future-you: when you wonder "why didn't we just X?", read this. We probably tried X.

### 3.1 Crop / fit strategies (reel format)

Landscape source (1280×720 or 1920×1080) → vertical 1080×1920 target. The source is ~1.78:1 and the target is ~0.56:1. Something has to give.

| Option | What it is | Tradeoff | Verdict |
|---|---|---|---|
| **Center crop** (v1) | Scale source to fill 1920 height, crop sides | Subject large but sides lost. Breaks on wide two-shots where Faith sits on the LEFT of the couch — you get empty couch between speakers | **Baseline only. Fails on talk-show wide shots.** |
| **Blurred background fit** | Full landscape centered at reduced size, blurred copy fills top/bottom bands | Nothing cropped, looks pro | **Works but subject is smaller than user preferred.** Good default for IG Reels generally. |
| **Black letterbox** | Full landscape + black bars | Nothing cropped, but looks amateur on IG | **Rejected.** Reads as "didn't format for the platform". |
| **Loose crop + mini bars** | 4:3 area + small black bars top/bottom | Compromise nobody uses | **Rejected.** Looks indecisive. |
| **Smart reframe (face tracking)** | OpenCV Haar cascade detects speaker face, crop window follows it | Full-bleed when it works; fails on wide two-shots (detects neither face cleanly) and crops heads on gesturing shots | **Built but rejected.** Good idea, wrong tool for wide-angle talk-show footage. |
| **Left-biased static crop at 1440 height** (Faith's final) | Scale source to 1440 height (not 1920), crop 1080 wide with left-biased offset (x=400), blur-fit pad to 1920 | Faith visible on BOTH close-ups AND wide two-shots. Slightly smaller subject than center crop. Blur pad hides the 240px top/bottom bars | **✅ Final for Faith.** |
| **Center crop from clean synced source** (Holly, OT) | Same crop as v1 baseline but on a source with the av offset fixed | Works because their source shots are mostly close-ups, not wide two-shots | **✅ Final for Holly, OT.** |

**Lesson:** There is no one-size-fits-all crop. Examine the shot composition of each artist's source before picking a crop strategy. If the source has wide two-shots where the speaker sits off-center, use the left-biased 1440 approach.

### 3.2 Caption styles tried

For the karaoke captions that appear during the clip.

| Style | Description | Verdict |
|---|---|---|
| **Plain SRT** (first attempt) | Standard subtitle file, white on outline | **Broken** — font size 20 in a 1080×1920 video came out microscopic because no `[Script Info]` block meant libass used default 384×288 PlayRes scaling |
| **Hormozi** | 2–3 words at a time, MASSIVE uppercase, white with thick stroke, gold emphasis on key words | **Built but rejected.** Tonally wrong for emotionally serious autism content. Reads as hustle-bro marketing. |
| **Karaoke highlight (`\kf` sweep)** | Full sentence, gradient highlight sweeps across current word | **Built but replaced.** Two-state coloring (before/after) couldn't produce the look in the user's reference screenshot. |
| **Word-by-word pop** | One word at a time, huge centered, scale-in animation | **Rejected.** Too punchy for serious content. |
| **Opus Clip 2-line bold** | 4 words per line, 2 lines max, uppercase bold sans, gold emphasis | **Rejected after preview.** Still too marketing-y. |
| **Clean broadcast** | Sentence-case 3-line subtitles, white with subtle box | **Rejected.** Too understated, doesn't earn the scroll stop. |
| **3-state Poppins karaoke** (final) | Per-word Dialogue lines with past=white / current=gold (`#E8B86D`) / future=faded blue-grey (`#6B7B8C`), Poppins ExtraBold 68pt, center-anchored at y=1620 | **✅ Final.** Matches the user's reference screenshot. Rock-solid positioning. |

**Lesson:** Don't rely on the `\k` family of ASS karaoke tags for the 3-state effect. They only handle 2 states. Emit one `Dialogue:` line per word position with explicit color overrides on each word.

### 3.3 Cover slide designs tried

Full-bleed magazine vs minimalist branded vs split poster.

| Design | Description | Verdict |
|---|---|---|
| **A1 Magazine** | Full-bleed cover photo of the speaker, dark gradient overlay bottom half, huge headline anchored at bottom, centered play button | **✅ Final.** Strongest scroll-stopper on the IG feed. What every pro account uses. |
| **A2 Minimalist** | Dark navy background, photo in a gold-bordered card, centered headline below | Strong brand identity but the framed photo reduces face dominance, which is the #1 scroll-stopper | **Rejected.** |
| **A3 Split** | Top 60% photo + bottom 40% dark zone with headline | Editorial feel, second-best scroll-stop | **Rejected in favor of A1.** |

**Play button cue:** Every cover includes a centered `▶` circle (140px, white outline, blur backdrop). Universally recognized as "this is a video, not a static post".

### 3.4 Transitions and sync

| Approach | Issue |
|---|---|
| **Hard cuts between cover → clip → ending** | Sounded abrupt; captions cut in mid-word |
| **Parallel xfade (video) + acrossfade (audio)** | Smooth, but initially drifted because I was resetting PTS with `setpts=PTS-STARTPTS` on both streams independently of a source with baked-in av offset |
| **xfade + acrossfade with pre-synced source** | **✅ Final.** 0.5s crossfade cover→clip, 0.8s crossfade clip→ending, audio crossfades match |

**Lesson:** Before touching crossfades, verify your source MP4 has `start_time=0.000000` on both video and audio streams. If it doesn't, fix the source first (step 1 of every pipeline).

### 3.5 Cover photo sourcing (the Faith Evans mistake)

When Faith Evans's folder was initially set up, the `cover-photo.png` was actually a frame of **Tamron Hall** (the show host), not Faith. This made it through multiple iterations of cover rendering before anyone noticed.

**Lesson:** Always verify the cover photo shows the *subject*, not the host/interviewer. If the source footage has both, extract multiple frames at different timestamps and pick one where the subject is clearly centered and recognizable.

### 3.6 Cut selection (Faith's 2-minute best-of)

Faith's source is a 7-minute interview. She talks uninterrupted on two topics (diagnosis fight + nonprofit mission) but her airtime is broken up by:
- Host questions
- Tamron reaction shots (brief cutaways)
- Audience B-roll
- Wide two-shots vs close-ups (camera alternates)

**Naïve approach:** pick 6 segments covering the key quotes and concat them.

**Problem:** Even within a segment, a Tamron reaction cutaway can happen mid-sentence, or the camera cuts to audience during a key line. The naïve cuts include these cutaways.

**Final approach:** Extract source frames densely around each cut boundary, identify exact timestamps where the camera leaves Faith, and **split cuts around those moments**. Faith's final cut is 8 segments (not 6) because cut 3 was split around a Tamron reaction at source t=159.5–160.5 and cut 4 was split around audience B-roll at source t=247.5–252.0.

**Lesson:** Before transcribing, visually scan the source at 2–3 second intervals. Build a map of Faith-visible vs cutaway-to-other timestamps. Then pick cuts that live entirely inside the Faith-visible intervals.

### 3.7 Smart reframe specifically for Faith

Built a smart-reframe script (`_smart_reframe.py`) using OpenCV Haar cascade face detection + EMA smoothing + velocity clamping on the crop center. Ran it on Faith's concatenated cut.

**Result:** Worked great on close-ups (face centered), but on wide two-shots the Haar cascade couldn't reliably detect Faith's small face and fell back to the scene center (empty couch between Faith and Tamron). Also the script was 1080 wide at 1920 scale, so upscaling the 720p source with aggressive zoom meant any moment with a small face had the camera essentially wandering around her body rather than her face.

**Lesson:** Face tracking works when the face is reliably large and detectable. Talk show wide two-shots fail this test. A static left-biased crop at reduced scale is more robust.

### 3.8 Encoding quirks

Two encoding bugs surfaced:

1. **Windows Media Player error `0x80004005`** after a successful ffmpeg build. Root cause: the `ass` subtitle filter and `xfade` filter internally use RGBA or yuv444p and ffmpeg's auto-format negotiation left the output in a pixel format WMP/Clipchamp couldn't decode. **Fix:** add `format=yuv420p` at the end of the filter chain AND explicit `-profile:v high -level 4.0 -pix_fmt yuv420p` encoder args.

2. **Cross-cut lip sync drift** after seemingly-correct build. Root cause: source MP4 has video stream starting at `t=4.037` and audio stream at `t=0`. `setpts=PTS-STARTPTS` on both independently destroys the relative offset. **Fix:** pre-create `_source-synced.mp4` (step 1 of every pipeline) where `atrim` drops the first N seconds of audio to realign with the video's first frame.

---

## 4. The Final Pipeline

Per-artist, the final artifacts are:

```
content/curated/<slug>/
├── _source-landscape.mp4       # (1) raw download from YouTube
├── _source-synced.mp4          # (2) fixed av offset OR best-of cut
├── _source-aligned.json        # (3) forced-aligned word timestamps
│
├── cover-photo.png             # (4) 1080x1920 still of the subject
├── cover-options/
│   └── a1-magazine.html/.png   # (5) chosen cover design
│
├── brand-overlay-v2.html/.png  # (6) top brand bar (1080x1920)
├── ending-slide.html/.png      # (7) ending CTA card (1080x1920)
├── styles/karaoke-brand.ass    # (8) generated karaoke subtitles
│
├── clip-branded-v2.mp4         # (9) crop + overlay + captions baked in
├── FINAL-reel-v3.mp4           # (10) cover + clip + ending, full reel ⭐ SHIP
│
├── carousel-v2/
│   ├── slide-1-cover.html/.png # carousel cover at 1080x1350
│   ├── slide-2-video.mp4       # branded captioned clip reformatted to 1080x1350
│   ├── slide-3-quote.html/.png # big Playfair pull quote
│   ├── slide-4-cta.html/.png   # carousel CTA
│   └── brand-overlay-carousel.png
│
├── captions.md                 # reel + feed caption copy
└── index.html                  # website artist page
```

### 4.1 Reel format

- **1080×1920** vertical (9:16)
- H.264 high profile, level 4.0, yuv420p (WMP/Clipchamp compatible)
- 29.97 fps
- AAC 44.1 kHz stereo 128 kbps
- `+faststart` for instant playback on web/IG
- Target length: **60–120 seconds** (IG's sweet spot; under 90s is ideal for completion rate)
- Structure: `cover (3.0s) → clip → ending CTA (3.5s)` with 0.5s/0.8s crossfades

### 4.2 Carousel format

- **1080×1350** (4:5 portrait, Instagram's tallest carousel aspect)
- **4 slides standard** for all artists:
  1. **Cover** — full-bleed photo (A1 magazine style at 4:5)
  2. **Video** — branded captioned clip, reformatted from the reel's source
  3. **Quote** — big Playfair Display pull quote with attribution
  4. **CTA** — mission headline + save/share/follow + gold "Tag an autism X" button
- **No slide numbers** (e.g. `2/4`) — they add clutter without value
- Swipe cue (`SWIPE →`) in gold on slides 1 and 3 to encourage swipe-through

---

## 5. Reel Build (v3)

### Step 0 — Preconditions

```bash
# Dependencies (one-time)
pip install openai-whisper stable-ts packaging yt-dlp opencv-python
cd /tmp/pw && npm install playwright
mkdir -p content/curated/fonts
curl -sL -o content/curated/fonts/Poppins-Bold.ttf \
  https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Bold.ttf
curl -sL -o content/curated/fonts/Poppins-ExtraBold.ttf \
  https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-ExtraBold.ttf
```

### Step 1 — Create synced source

```bash
bash content/curated/_create-synced-source.sh
```

Detects the video stream's `start_time` and trims the audio by that amount so both streams start at PTS `0.000000`. **This is the single most important step.** Skipping it silently creates lip-sync drift later.

### Step 2 — Forced alignment

```bash
python content/curated/_align_stable_ts.py \
  content/curated/<slug>/_source-synced.mp4 \
  content/curated/<slug>/_source-aligned.json
```

Uses `stable-ts` (which wraps Whisper) to generate word-level timestamps with voice-activity detection and silence-snapping. Model: `small.en` (~500 MB, English-only, fast, accurate enough).

### Step 3 — Generate karaoke ASS

```bash
python content/curated/_karaoke_brand.py \
  content/curated/<slug>/_source-aligned.json \
  content/curated/<slug>/styles/karaoke-brand.ass
```

Emits per-word `Dialogue:` lines with 3-state coloring:
- **Past words:** `#FFFFFF` (white)
- **Current word:** `#E8B86D` (brand gold)
- **Future words:** `#6B7B8C` (muted blue-grey)

Anchored at `\an5\pos(540, 1620)` — center of the caption block in 1080×1920 coordinates. This eliminates vertical jitter when phrase line counts change.

**Tunable constants** (top of `_karaoke_brand.py`):
- `FONT_SIZE = 68`
- `ANCHOR_Y = 1620` — caption center y
- `MAX_WORDS_PER_GROUP = 5` — phrase length
- `MAX_PAUSE = 0.9` — break phrase on longer pauses
- `READ_AHEAD = 0.0` — show phrase N seconds before first word
- `WORD_BIAS = 0.0` — shift word boundaries (negative = earlier)
- `TAIL_HOLD = 0.40` — hold last word this long after group ends

### Step 4 — Build cover

Edit `content/curated/_build-cover-options.py`:
```python
ARTISTS = {
    "<slug>": {
        "brand_main": "SPECTRUM",
        "brand_sub":  "UNLOCKED",
        "name":       "FIRST LAST",
        "headline":   '"Quote line one<br>Quote line two"',
        "credit":     "via [Source Show]",
        "photo":      "cover-photo.png",
    },
}
```

Then:
```bash
python content/curated/_build-cover-options.py   # generates HTMLs
cp content/curated/_render-cover-options.mjs /tmp/pw/render-covers.mjs
cd /tmp/pw && node render-covers.mjs             # renders to PNG
```

### Step 5 — Build brand overlay

Create `content/curated/<slug>/brand-overlay-v2.html` (copy from an existing artist, update headline and credit). Then:

```bash
cp content/curated/_render-brand-overlays.mjs /tmp/pw/render-brand.mjs
cd /tmp/pw && node render-brand.mjs
```

### Step 6 — Build ending slide

Create `content/curated/<slug>/ending-slide.html` at **native 1080×1920** (not 1080×1350 — that was the old carousel-ratio format and it gets letterboxed in the vertical reel). Copy from another artist and update:
- `.label` — "Holly's Mission" / "OT's Truth" / "Faith's Mission"
- `.main-msg` — headline with one italic gold word
- `.sub-msg` — explainer paragraph
- `.cta-text` — "Tag an autism mom" / "Tag an autism dad" / etc.

Then:
```bash
cp content/curated/_render-endings.mjs /tmp/pw/render-endings.mjs
cd /tmp/pw && node render-endings.mjs
```

### Step 7 — Build the reel

```bash
bash content/curated/_build-final-reel-v3.sh
```

This does two things per artist:

**7a. Build `clip-branded-v2.mp4`** — take `_source-synced.mp4`, scale+crop to 1080×1920, composite `brand-overlay-v2.png` on top, burn `styles/karaoke-brand.ass` captions:

```
[0:v] scale=-2:1920, crop=1080:1920:(in_w-1080)/2:0, setsar=1, format=yuv420p [cropped];
[cropped][1:v] overlay=0:0 [branded];
[branded] ass=styles/karaoke-brand.ass:fontsdir=../fonts, format=yuv420p [vout]
```

**For Faith specifically**, use the Faith-specific script `_build-faith-reel.sh` which uses left-biased crop at 1440 height with blur-fit:

```
[0:v] scale=-2:1440, crop=1080:1440:400:0, setsar=1, format=yuv420p [cropped];
[cropped] split=2 [bg][fg];
[bg] scale=1080:1920:force_original_aspect_ratio=increase, crop=1080:1920,
     boxblur=40:1, eq=brightness=-0.15 [bg2];
[fg] pad=1080:1920:0:240:color=black@0 [fg2];
[bg2][fg2] overlay [blurfit];
[blurfit][1:v] overlay=0:0 [branded];
[branded] ass=... [vout]
```

**7b. Concat cover + clip + ending with crossfades:**

```
cover (3.0s) --[xfade 0.5s]--> clip (N s) --[xfade 0.8s]--> ending (3.5s)
```

Audio uses `acrossfade` with matching durations so speech fades smoothly into the silent CTA card.

### Step 8 — Verify

Open `FINAL-reel-v3.mp4` in **VLC** (not Windows Media Player — VLC is more forgiving but don't trust its forgiveness as a pass).

Check:
- [ ] Lip sync is tight
- [ ] Karaoke captions match the speech word-for-word
- [ ] Brand bar is visible at top throughout the clip
- [ ] Speaker is visible and centered (or at least in frame) throughout
- [ ] No empty couch / audience cutaways / Tamron reaction shots (if source is a talk show)
- [ ] Cover credit matches brand overlay credit
- [ ] Ending CTA fills the full frame (not letterboxed)
- [ ] Crossfades are smooth

If any fails, see [Troubleshooting](#12-troubleshooting).

---

## 6. Carousel Build (v2)

### Layout

4 slides, all 1080×1350:

```
[slide 1]  [slide 2]  [slide 3]  [slide 4]
 COVER      VIDEO      QUOTE       CTA
```

No slide numbers. Swipe cue on slides 1 and 3.

### Step 1 — Generate HTMLs for slides 1, 3, 4

```bash
python content/curated/_build-carousels.py
```

Reads `ARTISTS` in the script and writes:
- `<slug>/carousel-v2/slide-1-cover.html` — A1 magazine style at 1080×1350
- `<slug>/carousel-v2/slide-3-quote.html` — Playfair Display pull quote
- `<slug>/carousel-v2/slide-4-cta.html` — mission CTA

### Step 2 — Render HTMLs to PNGs

```bash
cp content/curated/_render-carousels.mjs /tmp/pw/render-carousels.mjs
cd /tmp/pw && node render-carousels.mjs
```

### Step 3 — Build the video slide

```bash
bash content/curated/_build-carousel-videos.sh
```

This:
1. **Crops the existing 1080×1920 `brand-overlay-v2.png`** to 1080×1350 (top crop — all brand content is in the top 420px anyway) → `carousel-v2/brand-overlay-carousel.png`
2. **Builds `slide-2-video.mp4`** by:
   - Scaling `_source-synced.mp4` to height 1350
   - Cropping 1080 wide (center for Holly/OT, left-biased `x=400` for Faith)
   - Overlaying the cropped brand overlay
   - Burning the same `karaoke-brand.ass` file (libass auto-scales the positions from the ASS's `PlayResY=1920` reference to the actual 1350-tall video)

### Step 4 — Verify

Open each carousel video in VLC. Check:
- [ ] 1080×1350 dimensions
- [ ] Brand bar visible at top
- [ ] Captions visible near bottom
- [ ] Speaker visible throughout
- [ ] Sync with audio (same as reel)

---

## 7. Website Integration

Each artist has a page at `content/curated/<slug>/index.html`, styled to match the existing calendar pages. The Curated hub is at `content/curated/index.html`. Both are generated by:

```bash
python content/curated/_build-curated-pages.py
```

The generator reads per-artist data from `ARTISTS` at the top of the script. To add a new artist:

1. Add an entry to `ARTISTS` with `slug`, `name_main`, `name_em`, `name_full`, `source`, `quote`, `reel_file`, `reel_size`, `reel_len`, `reel_desc`, `carousel[]`, `reel_caption`, `feed_caption`, `badges`.
2. Run the script.
3. The hub page auto-includes the new artist card.
4. The root `index.html` nav already has Curated linked, so new artists are reachable via the nav dropdown.

Each artist page has:
- Header band with name + source + quote
- Section 1: **Reel** — embedded `<video>` player + download button + metadata pills
- Section 2: **Carousel** — grid of slides with per-slide download buttons
- Section 3: **Captions** — reel caption + feed caption, copy-to-clipboard buttons

---

## 8. Lessons Learned — Bugs and Root Causes

These are the real bugs we hit. Each one cost at least one round of rebuilding.

### Bug 1 — `1/2` indicator on cover slide

`cover-slide.html` had a hardcoded `<div class="slide-num">1/2</div>` left over from when it was a 2-slide carousel cover. For a reel cover this is meaningless.

**Fix:** delete the div before rendering.
**Prevention:** when copying cover templates across artists, strip any legacy carousel-specific elements.

### Bug 2 — Cover and ending rendered at wrong aspect

The original `cover-slide.html` and `ending-slide.html` were 1080×1350 (carousel ratio). Concatenating them into a 1080×1920 reel letterboxed them with black bars.

**Fix:** rebuild at native 1080×1920.
**Prevention:** the aspect must match the container format. A reel cover is 1080×1920. A carousel cover is 1080×1350. They are different files.

### Bug 3 — Captions invisible on first render

Plain SRT with `Fontsize=20`. Libass fell back to the default 384×288 `PlayRes` and scaled the font ~5× smaller than intended.

**Fix:** generate real ASS with explicit `PlayResX: 1080` / `PlayResY: 1920`.
**Prevention:** always emit ASS, never plain SRT, for burned-in captions.

### Bug 4 — Caption block jittering up/down between phrases

`Alignment=2` (bottom-center anchored) with fixed `MarginV`. When a phrase wrapped to 2 lines, the bottom edge stayed put but the top edge moved up — visually it looked like the captions jumped.

**Fix:** use `\an5\pos(540, y)` per Dialogue line — anchors the *center* of the caption block. 1-line and 2-line phrases both balance around the same midpoint.

### Bug 5 — Literal `\1c&H...&}` text rendered

First attempt at the position prefix did:
```python
parts = ["{\\an5\\pos(...)}"] + [f"{{\\1c{col}}}{txt}" for w in group]
text = " ".join(parts).replace("} {", "} ")
```
The `replace` call stripped the opening `{` from each color override block, so libass rendered them as plain text.

**Fix:**
```python
text = prefix + " ".join(word_parts)
```
ASS handles adjacent override blocks correctly without needing string surgery.

### Bug 6 — Double brand overlay

First v3 build used the existing `FINAL.mp4` (original cropped clip) as input. But `FINAL.mp4` already had the OLD brand overlay baked in. Adding `brand-overlay-v2.png` on top resulted in duplicate brand bars and duplicate headline boxes.

**Fix:** rebuild from `_source-synced.mp4` (no baked overlays), do the center crop ourselves, then add the new overlay.
**Prevention:** treat any file named `FINAL-*` in the folder as an opaque prior deliverable. The pipeline operates on `_source-synced.mp4` (clean).

### Bug 7 — Lip sync drift + captions 4 seconds ahead of speech

Root cause: source MP4 has `video.start_time = 4.037` but `audio.start_time = 0.000`. When `setpts=PTS-STARTPTS` is applied to both streams in `filter_complex`, the relative offset is destroyed and audio ends up 4 seconds ahead of video. The Whisper transcription was also done on the offset audio, so word timestamps were 4 seconds early.

**Fix:** create `_source-synced.mp4` as the canonical input (Step 1 of pipeline). `ffprobe` the video's `start_time`, `atrim` the audio by that amount, reset both streams to start at 0.

**Prevention:** `ffprobe` every source MP4 before building. If video and audio `start_time` differ, fix the source before doing anything else.

### Bug 8 — Windows Media Player `0x80004005`

The `ass` subtitle filter and `xfade` filter can leave the output in an unexpected pixel format (yuv444p or rgba). WMP and Clipchamp only support yuv420p with H.264 high profile.

**Fix:** add explicit `format=yuv420p` to the end of the filter chain AND `-profile:v high -level 4.0 -pix_fmt yuv420p` to the encoder args.

**Prevention:** always encode with these explicit settings. VLC will play anything, but WMP is a canary for compatibility.

### Bug 9 — Smart reframe cut off speaker heads

OpenCV Haar cascade centered the 1080-wide crop on the detected face at full 1920 scale. On gesturing shots where the speaker's head was near the top of the frame, the crop window clipped the head.

**Fix:** didn't adopt smart reframe for Holly/OT. For Faith, used left-biased static crop at 1440 height instead.

**Prevention:** face tracking is the wrong tool for talk-show wide shots. Use a static crop strategy per artist based on shot composition.

### Bug 10 — Faith's cover photo was actually Tamron Hall

The initial `cover-photo.png` for Faith had been extracted from a frame showing the interview host (Tamron Hall), not Faith herself.

**Fix:** re-downloaded the YouTube source, extracted frames at multiple timestamps, picked one showing Faith clearly, regenerated the cover.

**Prevention:** always sanity-check cover photos by opening them and asking "is this actually the subject?" before rendering anything downstream.

### Bug 11 — Faith's cuts included audience B-roll and host reaction shots

The naïve 6-segment cut plan landed partway inside a Tamron reaction cutaway (source t=159.5–160.5) and an audience B-roll cutaway (source t=247.5–252.0).

**Fix:** split cuts 3 and 4 around those ranges, producing 8 segments instead of 6.

**Prevention:** before finalizing cuts, visually scan the source at 1–2 second intervals around every cut boundary. Build a map of "who is on camera" by timestamp. Only cut within Faith-visible ranges.

### Bug 12 — Carousel video slide couldn't inherit reel branding by cropping

Tried to generate the carousel video slide by center-cropping `clip-branded-v2.mp4` (the 1080×1920 reel clip) to 1080×1350. Brand bar lives at top 60–420px and captions live around y=1620. A center crop lost both (285px off top + 285px off bottom).

**Fix:** rebuild the carousel video from `_source-synced.mp4` at 1080×1350 directly, with a cropped 1080×1350 version of the brand overlay. Libass auto-scales the karaoke position from `PlayResY=1920` reference to the actual 1350-tall video.

**Prevention:** don't crop reel output to carousel output. They're different formats and need separate builds from the same source.

---

## 9. New Artist Checklist

Copy this block and work through it for a new artist.

```
## <Artist Name> — new artist setup

[ ] 1. Find the source
    [ ] Celebrity qualifies (has name recognition in autism parent community)
    [ ] Has a clear personal story about their own autistic child
    [ ] Has at least one quotable moment
    [ ] Source is accessible (YouTube URL, podcast episode, etc.)
    [ ] Slug: <slug> (e.g., holly-peete, ot-genasis, faith-evans)

[ ] 2. Set up folder structure
    [ ] mkdir -p content/curated/<slug>/styles
    [ ] mkdir -p content/curated/<slug>/cover-options
    [ ] mkdir -p content/curated/<slug>/carousel-v2

[ ] 3. Download source
    [ ] yt-dlp the source → _source-landscape.mp4
    [ ] ffprobe to verify dimensions
    [ ] Check for audio/video start_time offset

[ ] 4. Pick the cover photo
    [ ] Extract 8–12 candidate frames from the source
    [ ] Pick one showing the subject clearly (NOT the host)
    [ ] Scale/crop to 1080×1920 → cover-photo.png

[ ] 5. Decide on crop strategy
    [ ] Watch 30s of source
    [ ] Is the subject consistently centered on close-ups? → center crop OK
    [ ] Are there wide two-shots where subject is off to one side? → left or right biased crop at 1440 height
    [ ] Is the source talk-show footage with audience/host cutaways? → plan to do a best-of cut first

[ ] 6. Plan cuts (if doing a best-of)
    [ ] Read the transcript (run whisper once for segment text)
    [ ] Pick 4–8 segments covering the strongest quotes
    [ ] Dense-scan source frames around each cut boundary
    [ ] Identify host/audience/B-roll cutaways; split cuts to avoid them
    [ ] Write cuts to a Python script or _cuts.txt

[ ] 7. Run the pipeline
    [ ] bash _create-synced-source.sh  (OR _build-<artist>-cut.py for best-of)
    [ ] python _align_stable_ts.py _source-synced.mp4 _source-aligned.json
    [ ] python _karaoke_brand.py _source-aligned.json styles/karaoke-brand.ass

[ ] 8. Build templates
    [ ] Add artist to ARTISTS dict in _build-cover-options.py
    [ ] python _build-cover-options.py
    [ ] Create brand-overlay-v2.html (copy + edit headline/credit)
    [ ] Create ending-slide.html (copy + edit label/main-msg/sub-msg/cta)
    [ ] Add brand-overlay to _render-brand-overlays.mjs
    [ ] Add ending to _render-endings.mjs
    [ ] Render all via node in /tmp/pw

[ ] 9. Build reel
    [ ] Add artist to _build-final-reel-v3.sh
    [ ] (Faith-like crop? Use _build-faith-reel.sh instead)
    [ ] Run the script
    [ ] Verify in VLC: lip sync, captions, visibility, no cutaways

[ ] 10. Build carousel
    [ ] Add artist to ARTISTS in _build-carousels.py
    [ ] python _build-carousels.py
    [ ] node /tmp/pw/render-carousels.mjs
    [ ] Add artist to _build-carousel-videos.sh
    [ ] bash _build-carousel-videos.sh
    [ ] Verify all 4 slides in VLC / image viewer

[ ] 11. Write captions
    [ ] captions.md with reel caption, feed caption, hashtags

[ ] 12. Update website
    [ ] Add artist to ARTISTS in _build-curated-pages.py
    [ ] python _build-curated-pages.py
    [ ] Verify the hub + artist page render correctly

[ ] 13. Commit to git
    [ ] git add content/curated/<slug>/
    [ ] git add any modified scripts
    [ ] git commit -m "feat: <artist> v3 reel + carousel + website"

[ ] 14. Post
    [ ] Download the reel mp4 via the website page's download button
    [ ] Upload to Instagram as a Reel
    [ ] Download the 4 carousel files
    [ ] Post as a carousel on Instagram
    [ ] Copy the feed caption from the website
    [ ] Schedule/publish
```

---

## 10. Script Reference

All scripts live in `content/curated/` unless noted. The leading `_` means "build/tooling, not a deliverable".

| Script | Purpose | When to run |
|---|---|---|
| `_create-synced-source.sh` | Trim audio to match video's `start_time`, produce `_source-synced.mp4` | Step 1 for every artist |
| `_build-faith-cut.py` | 8-segment best-of cut with crossfades (Faith-specific example) | Only for multi-cut best-of builds |
| `_align_stable_ts.py` | Whisper `small.en` transcribe + stable-ts forced alignment → JSON | After synced source exists |
| `_karaoke_brand.py` | Generate `styles/karaoke-brand.ass` from aligned JSON | After alignment JSON exists |
| `_build-cover-options.py` | Generate HTML for 3 cover designs per artist | After adding artist to `ARTISTS` dict |
| `_render-cover-options.mjs` | Render cover HTMLs to PNG via Playwright | Via `/tmp/pw/render-covers.mjs` |
| `_render-brand-overlays.mjs` | Render `brand-overlay-v2.html` to transparent PNG | Via `/tmp/pw/render-brand.mjs` |
| `_render-endings.mjs` | Render `ending-slide.html` to PNG | Via `/tmp/pw/render-endings.mjs` |
| `_build-final-reel-v3.sh` | Build `clip-branded-v2.mp4` + `FINAL-reel-v3.mp4` (standard center crop) | For Holly, OT, and any artist with centered shots |
| `_build-faith-reel.sh` | Faith-specific reel build with left-biased crop + blur-fit | For artists with wide two-shots where subject sits off-center |
| `_build-carousels.py` | Generate HTMLs for slides 1, 3, 4 (cover, quote, CTA) | After adding artist to `ARTISTS` dict |
| `_render-carousels.mjs` | Render carousel HTMLs to PNG | Via `/tmp/pw/render-carousels.mjs` |
| `_build-carousel-videos.sh` | Build `slide-2-video.mp4` at 1080×1350 from source | After aligned JSON and karaoke ASS exist |
| `_build-curated-pages.py` | Generate Curated hub + per-artist website pages | After all assets exist |
| `_smart_reframe.py` | OpenCV face-tracking crop (experimental, not used in production) | Only for debugging smart-reframe experiments |

### Dependencies

| Tool | Version | Install |
|---|---|---|
| `ffmpeg` | 8.x full build | Already installed via winget |
| Python | 3.14 | `C:\Python314\python.exe` |
| `openai-whisper` | 20250625 | `pip install openai-whisper` |
| `stable-ts` | 2.19+ | `pip install stable-ts` |
| `yt-dlp` | 2026+ | `pip install yt-dlp` |
| `packaging` | any | `pip install packaging` (silero-vad dep) |
| `opencv-python` | 4.13+ | `pip install opencv-python` (only for `_smart_reframe.py`) |
| Node.js | 24+ | already installed |
| `playwright` | 1.59+ | `cd /tmp/pw && npm install playwright` |

### Whisper model

- **`small.en`** (~500 MB) — the right balance of speed and accuracy for English interviews. Cached at `~/.cache/whisper/`.
- Avoid `base.en` — word timestamps are noticeably worse.
- `medium.en` is ~1.5 GB and only marginally more accurate for this use case.

---

## 11. Brand System

| Property | Value |
|---|---|
| **Primary font** | Poppins (Bold, ExtraBold, Black) |
| **Display font** (endings, pull quotes) | Playfair Display (Black, italic for emphasis) |
| **White (text)** | `#FFFFFF` |
| **Gold accent** (current karaoke word, italic emphasis) | `#E8B86D` |
| **Teal sub-brand** ("UNLOCKED") | `#4A90A4` |
| **Dark navy backgrounds** | `#0a0a12`, `#1a1a2e`, `#0f3460` |
| **Muted caption future-word** | `#6B7B8C` |

### Logo lockup

```
SPECTRUM      ← Poppins 900, white, letter-spacing: 2px
UNLOCKED      ← Poppins 800, #4A90A4, letter-spacing: 5-6px, margin-top: -4px
```

Positioned at top-left, 60px padding, in every cover / brand overlay / ending / carousel slide.

### Formats

| Artifact | Dimensions | Aspect |
|---|---|---|
| Reel | 1080×1920 | 9:16 |
| Carousel slide | 1080×1350 | 4:5 |
| Cover photo (source still) | 1080×1920 | 9:16 |
| Brand overlay (reel) | 1080×1920 transparent PNG | 9:16 |
| Brand overlay (carousel) | 1080×1350 transparent PNG | 4:5 |

### Typography scale

| Element | Reel (1920) | Carousel (1350) |
|---|---|---|
| Big display headline | 88–110px | 88px |
| Section label | 30px | 24px |
| Karaoke caption | 68px | auto-scaled by libass |
| Sub-message | 34px | 28px |
| Credit line | 22px | 22px |

---

## 12. Troubleshooting

### "The captions are running ahead of the speech"

- 99% chance you skipped Step 1 (synced source). Check `ffprobe content/curated/<slug>/_source-landscape.mp4`. If video `start_time` is non-zero, the audio will play ahead of video when Whisper transcribes it and ahead of video when the filter graph renders.
- Fix: run `_create-synced-source.sh` and rebuild from `_source-synced.mp4`, not `_source-landscape.mp4`.

### "Lip sync is off"

- Same root cause as captions-ahead: stream offset.
- Verify with: `ffprobe -v error -show_entries stream=index,codec_type,start_time,duration -of default=nw=1 _source-synced.mp4`
- Both streams must show `start_time=0.000000`.

### "Captions jitter up and down"

- You're using `Alignment=2` (bottom-anchored) with `MarginV` instead of `\an5\pos(540, y)` per-line.
- Regenerate the ASS with `_karaoke_brand.py` which uses center-anchored positioning.

### "Captions render as literal `\1c&H...&}` text"

- Someone called `.replace("} {", "} ")` on the generated Dialogue line and stripped opening braces from color overrides.
- Fix: in `_karaoke_brand.py`, use `text = prefix + " ".join(word_parts)` without any replace call.

### "Captions are tiny / invisible"

- You shipped a plain SRT without `[Script Info]` / `PlayResX` / `PlayResY`.
- Only use the `.ass` output of `_karaoke_brand.py`, never an SRT.

### "Windows Media Player won't open the file (0x80004005)"

- Your filter chain isn't ending in `yuv420p`.
- Fix: add `format=yuv420p` at the end of each branch of filter_complex, AND add encoder args `-profile:v high -level 4.0 -pix_fmt yuv420p`.
- Test: VLC and WMP should both open it. If VLC works but WMP doesn't, it's a pixel format issue.

### "The speaker is not visible — just the couch / audience / host"

- Your crop is center-aligned but the speaker is off-center in the source (usually sits on the left of the couch in talk shows).
- Fix A: use left-biased crop with `crop=1080:1440:400:0` + blur-fit pad to 1920.
- Fix B: dense-scan the source at cut boundaries, identify cutaways, and split cuts to avoid them.

### "Brand overlay is doubled / duplicate headlines"

- You built from `FINAL.mp4` (which already had brand overlay baked in) instead of `_source-synced.mp4` (clean).
- Fix: rebuild from `_source-synced.mp4`.

### "Cover photo shows the host / wrong person"

- You didn't verify `cover-photo.png` matches the subject.
- Fix: extract source frames at multiple timestamps, pick one showing the subject clearly, regenerate cover.

### "Ending slide has black bars top and bottom in the reel"

- Your `ending-slide.html` is 1080×1350 (carousel ratio) instead of 1080×1920.
- Fix: rebuild `ending-slide.html` at native 1080×1920. Same applies to `cover-slide.html`.

### "The reel is too zoomed in"

- You used aggressive center crop at full 1920 scale.
- Options:
  - Blur fit: full landscape visible with blurred top/bottom fill
  - Left-biased crop at 1440 scale + blur-fit pad (Faith's approach)
  - Loose crop: scale to 1440 height with center crop + small black bars

### "ffprobe shows NAL unit errors on output"

- The file is probably still being written. Wait for the ffmpeg process to finish.
- Check the file size — if it's still growing, ffmpeg is still working.

### "Playwright can't find playwright module"

- Playwright is installed in `/tmp/pw/node_modules/`, not globally.
- Copy your render `.mjs` script into `/tmp/pw/` and run it from there: `cd /tmp/pw && node <script>.mjs`.

### "Whisper is hallucinating words that aren't said"

- This happens on silent sections or background music. Whisper's language model will fill in plausible sentences.
- Fix: `stable-ts` with `suppress_silence=True` and `vad=True` (already configured in `_align_stable_ts.py`) — snaps word edges to actual speech and drops bogus detections.

---

## Appendix — File structure reference

```
content/curated/
├── PLAYBOOK.md                         ← this file
├── fonts/
│   ├── Poppins-Bold.ttf
│   └── Poppins-ExtraBold.ttf
│
├── _create-synced-source.sh
├── _align_stable_ts.py
├── _karaoke_brand.py
├── _smart_reframe.py                   (experimental)
├── _build-cover-options.py
├── _build-curated-pages.py
├── _build-carousels.py
├── _build-carousel-videos.sh
├── _build-faith-cut.py
├── _build-faith-reel.sh
├── _build-final-reel-v3.sh
├── _render-brand-overlays.mjs
├── _render-carousels.mjs
├── _render-cover-options.mjs
├── _render-endings.mjs
│
├── index.html                          ← Curated hub page
│
├── holly-peete/
│   ├── _source-landscape.mp4
│   ├── _source-synced.mp4
│   ├── _source-aligned.json
│   ├── cover-photo.png
│   ├── cover-options/a1-magazine.html/.png
│   ├── brand-overlay-v2.html/.png
│   ├── ending-slide.html/.png
│   ├── styles/karaoke-brand.ass
│   ├── clip-branded-v2.mp4
│   ├── FINAL-reel-v3.mp4               ⭐ ship this as the Reel
│   ├── carousel-v2/
│   │   ├── slide-1-cover.html/.png
│   │   ├── slide-2-video.mp4           ⭐ ship as carousel slide 2
│   │   ├── slide-3-quote.html/.png
│   │   ├── slide-4-cta.html/.png
│   │   └── brand-overlay-carousel.png
│   ├── captions.md
│   └── index.html                      ← artist page
│
├── ot-genasis/
│   └── ... (same structure)
│
└── faith-evans/
    └── ... (same structure, uses _build-faith-* scripts)
```

---

**Last updated:** 2026-04-08 — v3 reel pipeline + v2 carousel pipeline shipped for Holly Peete, OT Genasis, Faith Evans. All 3 reels + carousels live on the Curated website.
