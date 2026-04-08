# Dan Orlovsky + Madden — Build Handoff

**Status:** Source downloaded, encode in progress, pipeline NOT yet run.

## What's done

- ✅ Folder structure created: `styles/`, `cover-options/`, `carousel-v2/`
- ✅ YouTube source downloaded: `_source-landscape.webm` (10.3 MB, official ESPN upload titled *"NFL Live celebrates World Autism Awareness Day with Madden Orlovsky"*, YouTube ID `qb9I5TDPACw`)
- ⏳ Conversion to `_source-landscape.mp4` was running when session ended. The webm → mp4 re-encode was still writing (~100 MB and growing) because CRF 18 on a ~10 MB webm source produced a bloated intermediate. **Verify completion and re-encode at CRF 20 or 22 if needed.**

## What's next (fresh session)

1. **Verify source encode finished:**
   ```bash
   ffprobe -v error -show_entries stream=width,height,duration -of csv=p=0 \
     content/curated/dan-orlovsky-madden/_source-landscape.mp4
   ```
   Should show something like `1280,720,NNNN` — if "moov atom not found", the encode is incomplete. Re-run:
   ```bash
   cd content/curated/dan-orlovsky-madden
   ffmpeg -y -i _source-landscape.webm \
     -c:v libx264 -preset medium -crf 22 -pix_fmt yuv420p \
     -c:a aac -b:a 192k -movflags +faststart \
     _source-landscape.mp4
   ```

2. **Create synced source** (Step 1 of pipeline):
   - Add `dan-orlovsky-madden` to `_create-synced-source.sh` if needed, OR run the command manually:
   ```bash
   cd content/curated/dan-orlovsky-madden
   # ffprobe first to check if there's an av offset
   ffprobe -v error -show_entries stream=codec_type,start_time -of default=nw=1 _source-landscape.mp4
   # If video and audio start_time differ, run the sync fix
   ```

3. **Dense-scan source for best cut segments.** This is a ~5-7 min ESPN segment. Pick the emotional peak moments:
   - Madden singing the Eagles fight song
   - Madden's direct-to-camera message: *"Mom, I love you. Hunter, you're my favorite twin. Noah, I do like you. And Lennon, you're a good sister."*
   - Dan Orlovsky's tearful reaction
   - Madden describing his art ("great artwork, great coloring, great handwriting")
   - DeVonta Smith Eagles swag bag moment (optional, secondary YouTube ID `6SLBZSeLf4o`)
   
   Aim for a 60–90 second best-of cut.

4. **Cover photo:** Extract a frame showing Madden (not Dan alone). Try source timestamps where Madden is centered and looking at camera. Save as `cover-photo.png` at 1080×1920.

5. **Run the full pipeline:**
   - `_create-synced-source.sh` (or Faith-style cut script if doing a best-of)
   - `_align_stable_ts.py` → `_source-aligned.json`
   - `_karaoke_brand.py` → `styles/karaoke-brand.ass`
   - Add artist to `_build-cover-options.py` ARTISTS dict:
     ```python
     "dan-orlovsky-madden": {
         "brand_main": "SPECTRUM",
         "brand_sub":  "UNLOCKED",
         "name":       "MADDEN ORLOVSKY",
         "headline":   '"Mom, I love you.<br>I love you all."',
         "credit":     "via ESPN NFL Live",
         "photo":      "cover-photo.png",
     },
     ```
   - Create `brand-overlay-v2.html` (copy Faith's, change headline to `Madden Orlovsky:<br>"I love you, Mom"` and credit to `via ESPN NFL Live`)
   - Create `ending-slide.html` at 1080×1920 (copy Faith's, change `.label` to `MADDEN'S STORY`, `.main-msg` to `Autism is <em>love</em>,<br>spoken out loud.`, CTA button to `Tag a dad`)
   - Render cover, brand overlay, ending via `/tmp/pw`
   - Add artist to `_build-final-reel-v3.sh` and run
   - Add artist to `_build-carousels.py` and `_build-carousel-videos.sh`, run both
   - Add artist to `_build-curated-pages.py` ARTISTS list and regenerate

6. **Crop strategy:** The source is from an ESPN TV studio with Dan and Madden seated at the NFL Live desk. This is primarily a **2-person wide shot** with occasional close-ups. Use the **Faith-style left-biased crop at 1440 height + blur-fit** approach — they sit side by side so neither is centered. Or possibly use a **center crop** if Madden is in the middle of the frame for the key moments (verify with frame extraction).

## Source metadata

- **Primary YouTube:** https://www.youtube.com/watch?v=qb9I5TDPACw
- **Alternate (DeVonta Smith swag bag moment):** https://www.youtube.com/watch?v=6SLBZSeLf4o
- **Alternate (Madden's graphics):** https://www.youtube.com/watch?v=-2vuIXOaa5g
- **Alternate (Pat McAfee Show follow-up with Dan):** https://www.youtube.com/watch?v=MlOoSG43210
- **Context article:** [Today.com](https://www.today.com/parents/dads/dan-orlovsky-son-madden-viral-espn-world-autism-awareness-day-rcna266584)

## Source context for the captions/cover

- **Madden Orlovsky** is 14, autistic, one of triplets, identical twin to brother Hunter
- **Siblings mentioned by name in the quote:** Hunter, Noah, Lennon (sister), Mom
- **Father:** Dan Orlovsky, former Detroit Lions QB, current ESPN NFL Live analyst
- **Event:** World Autism Awareness Day, April 2, 2026
- **Second consecutive year** Madden appeared on NFL Live — first was 2025

## Captions draft (for captions.md)

**Reel caption (Instagram Reels):**
```
"Mom, I love you."
14-year-old Madden Orlovsky spoke directly to his family on NFL Live for World Autism Day. His dad Dan couldn't hold it together. Neither could anyone watching.
#autismparent #danorlovsky #worldautismday #autismdad #nfl
```

**Feed caption (carousel):**
```
"Mom, I love you. Hunter, you're my favorite twin. Noah, I do like you. And Lennon, you're a good sister."

That's what 14-year-old Madden Orlovsky said directly into the camera on ESPN's NFL Live this April 2nd — World Autism Awareness Day — sitting next to his father Dan, the former Detroit Lions QB and current ESPN analyst.

Madden is one of identical triplets, autistic, a die-hard Philadelphia Eagles fan, and — according to himself — someone with "great artwork, great coloring, great handwriting." His drawings decorated the NFL Live studio all morning.

When Dan asked his son if he could tell the camera something he loves, Madden didn't hesitate. He named every person in his family. His dad broke down on air. The entire NFL Live set joined him. Magic Johnson reposted it. Ric Flair reposted it. Pat McAfee had Dan on the next day to talk about it.

This is what autism parenting looks like when the world finally gets to see it: a kid with his own voice, his own art, his own love language, telling everyone he cares about exactly how much they matter.

Autism isn't silent. We just haven't been listening.

🎥 Dan & Madden Orlovsky on ESPN's NFL Live
💛 World Autism Awareness Day 2026

#AutismDad #DanOrlovsky #MaddenOrlovsky #AutismAwareness #NFL #AutismParent #AutismFamily #WorldAutismDay #AutismAcceptance #Neurodivergent
```

---

**Last updated:** 2026-04-08. Pick this up in a fresh session.
