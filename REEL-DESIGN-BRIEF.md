# REEL DESIGN BRIEF - Fix Required

**Date:** April 5, 2026  
**Issue:** Most reels don't follow the established design standard  
**Reference:** `content/day-04-sensory-hacks-reel/` is the GOLD STANDARD

---

## The Problem

18 slideshow reels were created but most look flat/rushed. They don't match the polished style of Day 4 Sensory Hacks.

**Bad reels look like:** Resized carousels with basic text  
**Good reels look like:** Day 4 - visually rich, engaging, TikTok-native

---

## GOLD STANDARD: Day 4 Design Elements

### Hook Slide (slide-01-hook.html)
```
- Background: gradient + decorative circles (::before, ::after pseudo-elements)
- Large emoji: 120px font-size
- Bold hook text: 72px, font-weight 800
- Gold highlight on key words: #E8B86D
- Subtext: 36px, 0.9 opacity
- Swipe indicator: bottom, teal (#4A90A4), with arrow animation
- Brand: @spectrum_unlocked at bottom, 24px, 0.6 opacity
```

### Content Slides (numbered tips/points)
```
- Number badge: top-right corner, 100px circle, gold background (#E8B86D), dark text
- Large emoji: 150px, centered
- Title: 64px, gold (#E8B86D), font-weight 800
- Description: 38px, 0.95 opacity, max-width 900px
- Tip box: colored border (teal #4A90A4), rounded corners, 32px text
- Brand at bottom
```

### CTA Slide
```
- Large emoji: 100px+
- Main CTA text: 56-64px, bold
- Action items with emoji bullets
- Colored badges for "Follow" "Save" "Share"
- Brand at bottom
```

---

## Design Specifications

### Colors
| Name | Hex | Usage |
|------|-----|-------|
| Gold | #E8B86D | Highlights, titles, badges |
| Teal | #4A90A4 | Borders, swipe indicators, tip boxes |
| Green | #27AE60 | Success, positive badges |
| Red | #E74C3C | Stop, warnings, strikethrough |
| BG Start | #1a1a2e | Gradient start |
| BG Mid | #16213e | Gradient middle |
| BG End | #0f3460 | Gradient end |

### Typography
| Element | Size | Weight |
|---------|------|--------|
| Hook text | 64-72px | 800 |
| Slide title | 56-64px | 800 |
| Description | 36-42px | 400-600 |
| Tip/badge text | 28-32px | 600 |
| Brand | 24px | 600 |
| Emoji | 100-150px | - |

### Decorative Elements (REQUIRED)
```css
/* Background circles - add visual depth */
.slide::before {
  content: '';
  position: absolute;
  top: -150px;
  right: -150px;
  width: 400px;
  height: 400px;
  background: #E8B86D;
  border-radius: 50%;
  opacity: 0.1;
}

.slide::after {
  content: '';
  position: absolute;
  bottom: -100px;
  left: -100px;
  width: 300px;
  height: 300px;
  background: #4A90A4;
  border-radius: 50%;
  opacity: 0.1;
}
```

---

## Reels That Need Fixing

### Priority 1 - Definitely Broken
| Day | Folder | Issue |
|-----|--------|-------|
| 2 | day-02-acceptance-reel | Flat, no decorative elements, basic layout |
| 8 | day-08-waad-reel | Check quality |
| 14 | day-14-visual-supports-reel | Batch created, likely flat |
| 21 | day-21-audhd-reel | Batch created |
| 24 | day-24-anxiety-reel | Batch created |
| 28 | day-28-nature-reel | Batch created |
| 31 | day-31-siblings-reel | Batch created |
| 35 | day-35-toolkit-reel | Batch created |
| 38 | day-38-summer-reel | Batch created |
| 42 | day-42-ot-reel | Batch created |
| 45 | day-45-speech-reel | Batch created |
| 49 | day-49-marriage-reel | Batch created |
| 52 | day-52-support-reel | Batch created |
| 56 | day-56-camp-reel | Batch created |
| 59 | day-59-independence-reel | Batch created |

### Known Good (Reference These)
| Day | Folder | Notes |
|-----|--------|-------|
| 4 | day-04-sensory-hacks-reel | **GOLD STANDARD** - Copy this style |
| 10 | day-10-iep-reel | Good quality |
| 17 | day-17-sleep-reel | Good quality |

---

## Fix Instructions

For EACH reel folder that needs fixing:

### 1. Hook Slide (slide-01-hook.html)
- Add `::before` and `::after` decorative circles
- Large emoji (120px+)
- Bold hook text with gold highlights
- Swipe indicator at bottom

### 2. Content Slides
- If listing items: Add number badge (top-right circle)
- Large emoji per slide (100-150px)
- Title in gold
- Description text below
- Tip box with border for key takeaways

### 3. CTA Slide
- Clear call to action
- Multiple action prompts (follow, save, comment)
- Colored badges

### 4. Render
```bash
cd /Users/aramide/clawd/SU/content/day-XX-topic-reel/
for f in slide-*.html; do
  npx playwright screenshot --viewport-size=1080,1920 "$f" "${f%.html}.png"
done
```

### 5. Verify
Compare visually to Day 4. Does it look as polished? If not, iterate.

---

## Reference Files

**Copy HTML structure from:**
- `content/day-04-sensory-hacks-reel/slide-01-hook.html` (hook)
- `content/day-04-sensory-hacks-reel/slide-02-hack1.html` (numbered content)
- `content/day-04-sensory-hacks-reel/slide-07-cta.html` (CTA)

**Content calendar (topics/hooks):**
- `content-calendar-60day.md`

---

## Checklist Per Reel

- [ ] Hook slide has decorative background circles
- [ ] Emojis are large (100px+)
- [ ] Key text uses gold (#E8B86D) highlights
- [ ] Content slides have number badges (if listing)
- [ ] Tip boxes have colored borders
- [ ] CTA slide has clear action prompts
- [ ] All PNGs rendered at 1080x1920
- [ ] Visual quality matches Day 4

---

## After Fixing

1. Render all PNGs
2. Commit: `git add -A && git commit -m "fix: Rebuild reels to match Day 4 design standard"`
3. Push: `git push`

---

*This brief is at: https://allagilejobs-jpg.github.io/SU/REEL-DESIGN-BRIEF.md*
