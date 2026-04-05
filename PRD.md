# PRD.md - Product Requirements Document
## Spectrum Unlocked Content System

**Last Updated:** April 5, 2026  
**Owner:** Aramidé Akinsulire  
**Status:** Active (Autism Acceptance Month Campaign)

---

## 1. Overview

### What is Spectrum Unlocked?
Spectrum Unlocked is an autism parenting content brand focused on education, support, and community building. The primary platforms are **Instagram** and **TikTok**.

### What is this repository?
This repo is the **content creation and management system** for Spectrum Unlocked. It includes:
- A 60-day content calendar (March 26 - May 24, 2026)
- HTML templates for carousel graphics
- A visual calendar dashboard
- Brand guidelines and design system
- Automated rendering pipeline for graphics
- Pre-written captions for Instagram and TikTok

### Live Site
**GitHub Pages:** https://allagilejobs-jpg.github.io/SU/

---

## 2. Goals

### Primary Goals
1. **Execute a 60-day content campaign** around Autism Acceptance Month (April 2026)
2. **Streamline content creation** - Templates + automation = faster production
3. **Maintain brand consistency** - All graphics follow the same design system
4. **Enable handoff** - Anyone (human or AI) can continue the work

### Success Metrics
- 60 days of planned content
- Graphics ready at least 1 week ahead
- Consistent posting schedule (2-3 posts/day during campaign)
- Growing engagement on Instagram/TikTok

---

## 3. Content Strategy

### Campaign Phases

| Phase | Dates | Days | Focus |
|-------|-------|------|-------|
| **Phase 1** | Mar 26-31 | 1-6 | Pre-April Build-Up |
| **Phase 2** | Apr 1-30 | 7-36 | Autism Acceptance Month (Peak) |
| **Phase 3** | May 1-24 | 37-60 | Momentum & Evergreen |

### Content Types

#### Carousels (1080x1350, 4:5)
- Educational slideshows (5-7 slides typically)
- Myth-busters, tips, guides, explainers
- Folder: `content/day-XX-topic/`
- PRIMARY content format

#### Reel Slides (1080x1920, 9:16)
- Vertical format for TikTok + Instagram Reels
- Repurposed carousel topics in video format
- Folder: `content/day-XX-topic-reel/` (separate from carousel!)
- Hook-first structure (grab attention immediately)
- Can be used as static slides OR as video frames

#### Filmed Video (No Graphics)
- Reels/TikToks (talking head, POV, storytime)
- Stories (polls, Q&As, casual)
- Vlogs (authentic, unpolished)
- These are filmed, not designed in this repo

### Daily Posting Schedule
The master calendar (`content-calendar-60day.md`) has 2-3 posts per day:
- **Morning:** Usually the main educational carousel (both platforms)
- **Afternoon:** Often Instagram-specific (stories, reels)
- **Evening:** Often TikTok-specific (casual, personal)

**Note:** The HTML calendar only shows the primary carousel per day. The full breakdown is in the markdown file.

---

## 4. Content Structure

### Carousel Slide Structure
Each carousel typically has:
1. **Cover slide** - Hook/title that stops the scroll
2. **Content slides** (3-5) - The actual information
3. **CTA slide** - Call to action (save, share, follow, comment)

### Slide Dimensions
| Format | Dimensions | Ratio | Folder Pattern |
|--------|------------|-------|----------------|
| Instagram Carousel | 1080 x 1350 | 4:5 | `day-XX-topic/` |
| Reel Slides | 1080 x 1920 | 9:16 | `day-XX-topic-reel/` |
| Instagram Story | 1080 x 1920 | 9:16 | - |
| TikTok (static) | 1080 x 1920 | 9:16 | `day-XX-topic-reel/` |

---

## 5. Functional Requirements

### Must Have
- [x] Visual content calendar showing all 60 days
- [x] Day detail modal with captions and slide previews
- [x] Brand guidelines page with colors, fonts, design rules
- [x] HTML templates for carousel slides
- [x] PNG export capability (via Playwright)
- [x] Pre-written captions for both platforms
- [x] Hashtag sets for Instagram and TikTok

### Nice to Have
- [x] Graphic editor for creating new slides
- [x] Template gallery for reusable designs
- [ ] Direct posting integration (not implemented)
- [ ] Analytics dashboard (not implemented)

---

## 6. User Workflows

### Creating Content for a New Day

1. **Check the calendar** - What's scheduled?
   - Read `content-calendar-60day.md` for full details
   - Or check `calendar-60day.html` for visual overview

2. **Create the day folder**
   ```
   content/day-XX-topic-name/
   ```

3. **Create HTML slide templates**
   - Use existing slides as reference
   - Follow brand guidelines (colors, fonts, spacing)
   - Name format: `slide-01-cover.html`, `slide-02-content.html`, etc.

4. **Render to PNG**
   ```bash
   npx playwright screenshot --viewport-size=1080,1350 slide.html slide.png
   ```
   Or use the render server: `./start.sh` then visit the editor

5. **Create captions.md**
   - Instagram caption (longer, more hashtags)
   - TikTok caption (shorter, 3-5 hashtags)
   - Content notes

6. **Update the calendar HTML**
   - Add entry to `dayData` object in `calendar-60day.html`
   - Update stats (Days Ready count)

7. **Commit and push**
   ```bash
   git add -A && git commit -m "Add Day XX content" && git push
   ```

### Posting Content

1. Open `calendar-60day.html` (live site or local)
2. Click on the day you're posting
3. Modal shows:
   - Slide previews (click to download)
   - Instagram caption (copy)
   - TikTok caption (copy)
4. Download slides, paste caption, post!

---

## 7. Design System

### Colors
| Name | Hex | Usage |
|------|-----|-------|
| Teal | `#4A90A4` | Primary accent, links, highlights |
| Gold | `#E8B86D` | Secondary accent, CTAs, emphasis |
| Green | `#27AE60` | Success, "ready" status |
| Dark BG | `#1a1a2e` | Primary background |
| Deep BG | `#0f0f1a` | Darker sections |
| Secondary BG | `#16213e` | Cards, elevated surfaces |

### Fonts
- **Headings:** Playfair Display (serif, elegant)
- **Body:** Poppins (sans-serif, readable)

### Slide Design Rules
- Dark gradient backgrounds (not pure black)
- High contrast text (white on dark)
- Generous padding (40-60px)
- Clear visual hierarchy
- Emojis for visual interest
- Brand colors for accents

---

## 8. Writing Guidelines

### Voice & Tone
- **Supportive, not preachy**
- **Educational, not condescending**
- **Inclusive** - Speak to parents, adults, allies
- **Honest** - Acknowledge hard truths
- **Hopeful** - But not toxic positivity

### Caption Rules
- **NEVER use em dashes (—)** - Use commas, colons, or line breaks
- Hook in first line
- Break up text with line breaks and emojis
- End with a question or CTA
- Instagram: 10-15 hashtags
- TikTok: 3-5 hashtags

---

## 9. Automation & Cron Jobs

The following cron jobs support this project (managed via Clawdbot):

| Job | Schedule | Purpose |
|-----|----------|---------|
| SU Daily Posting Reminder | 9am daily | Reminds what to post today |
| SU Weekly Content Brainstorm | 8pm Sundays | Generates 7 fresh post ideas |
| SU Content Research | 12pm Wednesdays | Finds trending topics, hashtags |

---

## 10. Known Issues & Limitations

1. **Calendar day-of-week labels are off by one** - Dates are correct, weekday names are wrong (shows Saturday for Sunday, etc.)

2. **HTML calendar is simplified** - Only shows primary post per day, not the full morning/afternoon/evening breakdown

3. **No direct posting** - Manual copy/paste to platforms required

4. **Rendering requires Playwright** - Must have Node.js and Playwright installed

---

## 11. Future Roadmap

- [ ] Fix day-of-week labels in calendar
- [ ] Add remaining Phase 3 content (Days 26-60)
- [ ] Video script templates for reels
- [ ] Story templates with interactive elements
- [ ] Engagement tracking spreadsheet
- [ ] A/B testing different hooks

---

## 12. Handoff Checklist

For another AI or developer taking over:

1. **Read this PRD** - You're doing it!
2. **Read ARCHITECTURE.md** - Technical details
3. **Check `content-calendar-60day.md`** - Full content plan
4. **Look at existing day folders** - See the pattern
5. **Review brand guidelines** - `brand-guidelines.html`
6. **Check cron jobs** - For automation context
7. **Ask questions** - Better to clarify than assume

---

*This document should be updated whenever major changes are made to the project.*
