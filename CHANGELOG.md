# Changelog - Spectrum Unlocked

## 2026-05-14

### Added - Complete Pinterest Playbook
**Commit:** pending at edit time

**What Changed:**
- Added `pinterest-playbook.html` as the full shareable Pinterest playbook for Copilot.
- Kept `pinterest-brand-kit.html` as a redirect to the new playbook URL.
- Included Spectrum Unlocked Pinterest strategy, brand rules, colors, typography, lockup guidance, copy formulas, content pillars, Pinterest SEO patterns, what to look out for, final QA checks, and do and do not guidance.
- Added 9 reusable Pinterest pin variants with live mini previews.
- Added a variation matrix and base HTML pattern for creating native 1000 by 1500 Pinterest pins.
- Linked the Pinterest Playbook from the home page top navigation and Brand & Guides dropdown.

**Files Added:**
- `pinterest-playbook.html`
- `pinterest-brand-kit.html`

**Files Updated:**
- `index.html`
- `CHANGELOG.md`

---

## 2026-04-05

### Added - Reel Content System
**New Feature:** Vertical reel slides (1080x1920) alongside existing carousels

**What Changed:**
- Created reel folders with `-reel` suffix convention
- Reel slides use 9:16 vertical format for TikTok/Instagram Reels
- Carousels remain in original folders (NOT overwritten)

**New Reel Content:**
- `content/day-21-audhd-reel/` - AuDHD: When Autism Meets ADHD (6 slides)
- `content/day-24-anxiety-reel/` - Autism & Anxiety (6 slides)

**Folder Structure Logic:**
```
content/
├── day-21-audhd/           # Carousel (1080x1350) - UNCHANGED
├── day-21-audhd-reel/      # Reel (1080x1920) - NEW
├── day-24-anxiety/         # Carousel - UNCHANGED
├── day-24-anxiety-reel/    # Reel - NEW
```

**Reel Slide Naming:**
- `slide-01-hook` - Opening hook (grab attention)
- `slide-02-what` - Define the topic
- `slide-03-signs` - Signs/symptoms
- `slide-04-tips` / `slide-04-helps` - Actionable advice
- `slide-XX-cta` - Call to action

**Documentation Updated:**
- ARCHITECTURE.md - Added Section 13: Reel Content System
- PRD.md - Updated Content Types and Slide Dimensions
- CHANGELOG.md - This entry

**Files Added:**
- `content/day-21-audhd-reel/*.html` (6 templates)
- `content/day-21-audhd-reel/*.png` (6 rendered slides)
- `content/day-21-audhd-reel/captions.md`
- `content/day-24-anxiety-reel/*.html` (6 templates)
- `content/day-24-anxiety-reel/*.png` (6 rendered slides)
- `content/day-24-anxiety-reel/captions.md`

---

## 2026-04-04

### Added - One-Click Edit from Calendar
**Commit:** 36466ad

**New Workflow:**
1. Open calendar, click any day
2. Hover over any slide thumbnail
3. Click ✏️ Edit button
4. Editor opens with that graphic loaded and ready to edit!

**How it works:**
- Editor receives URL params (day, slide, folder, slideName)
- Fetches the original HTML template
- Auto-detects template type from slide name:
  - `cover` → Cover template
  - `cta` → CTA template
  - `myth*` → Myth Buster
  - `vs` → VS Compare
  - `checklist` → Checklist
  - etc.
- Loads matching Fabric.js template
- Extracts text content from HTML and populates canvas
- Header shows "Editing: Day X - Slide Y"

---

### Fixed - Critical Editor Issues (Testing Pass)
**Commit:** 7557bbf

**Bugs Found & Fixed:**

1. **Load Project Feature** (CRITICAL)
   - Problem: Save button worked but no way to load saved projects!
   - Fix: Added 📂 Load button and `loadProjectFile()` function
   - Now can load .json project files back into editor

2. **Mobile Responsiveness** 
   - Problem: Editor unusable on tablets/phones (3-column grid)
   - Fix: Added responsive CSS, collapsible sidebars, mobile toggles
   - Sidebars now accessible via ☰ Menu and 🎨 Props buttons

3. **Unsaved Work Warning**
   - Problem: Work lost on accidental page close
   - Fix: Added `beforeunload` event to warn users

4. **Updated Instructions**
   - Added Save/Load documentation
   - Added warning about no auto-save

**Also Added:**
- `EDITOR-TEST-CHECKLIST.md` for comprehensive testing

---

### Fixed - Font Rendering on PNG Export
**Commit:** c72aa81

**Issue:** Fonts (Playfair Display, Poppins) might not render correctly in downloaded PNGs

**Fixed:**
- Added `preloadFonts()` function that runs when editor loads
- Preloads all font weights used (Playfair 600/700/800, Poppins 400-800)
- Export functions now await `document.fonts.ready` before capturing
- Force re-render of all text objects before export
- Added timing delays to ensure canvas renders complete

Fonts now reliably appear in exported PNG files!

---

### Fixed - Missing Day 37 CTA Image
**Commit:** c0813ac

**Issue:** Day 37 (May Goals) was missing slide-06-cta.png

**Fixed:**
- Rendered slide-06-cta.png from HTML template
- Updated calendar slides count from 5 to 6
- Added 'cta' to Day 37 slideNames array
- Removed empty day-36-hero-content folder

---

### Updated - Brand Guidelines with Templates & Categories Documentation
**Commit:** 0e8903c

**Enhanced `brand-guidelines.html`:**
- Added new "Templates & Categories System" section explaining the content creation concept
- Visual diagram showing how templates + categories combine
- Updated template count from 8 to 11
- Added visual mockups for 3 new templates: Content Box, Tip Cards, Sign Cards
- Added VS Compare mockup preview
- New grid displaying all 11 templates with icons and descriptions
- Added "Content Categories" section with all 4 category groups (Education, Practical, Emotional, Family)
- Usage tips for combining templates and categories in the editor

---

### Added - Brand Guidelines Page
**Commit:** 3bc80a4

**New file:** `brand-guidelines.html`

Complete brand documentation including:
- Brand overview and mission
- Color palette with hex codes and accessibility rationale
- Typography system (Playfair Display + Poppins)
- 8 template style rules with visual previews
- Layout, spacing, and composition guidelines
- Logic and reasoning behind all design decisions

---

### Rebuilt - TRUE Fabric.js Interactive Editor
**Commit:** f81440e

**Major upgrade to `editor.html`:**
- Double-click text to edit directly on canvas
- Click to select, drag to reposition any element
- Delete key removes selected element
- Real-time property panel (font, size, color, weight)
- Quick-add buttons (text, badge, list item, shape, emoji)
- 60 days of content with captions
- Search/filter day selector

---

### Added - Comprehensive Fabric.js Template Editor
**Commits:** 7177b5d, 71c6bdb

**Changes:**
- Created full template editor at `/editor.html`
- 8 template types: Cover, Myth-Buster, Checklist, VS Compare, Grid, CTA, Stats, Quote
- Click-to-edit text directly on canvas
- Dynamic list items (add/remove)
- Multi-slide carousel support (1-15+ slides)
- Color theme customization (background + accent)
- Canvas size options (Instagram 1080×1350, TikTok 1080×1920, Square 1080×1080)
- High-quality PNG export (single + all slides)
- Full 60-day calendar data integration
- Search/filter days by title
- Caption copy buttons (Instagram + TikTok)
- Auto-detect template type from content
- Zoom controls
- Responsive mobile view with sidebar toggles

**Files affected:**
- `editor.html` (new)

---

### Added - Download functionality for 60-day calendar graphics
**Commit:** 87e86f1

**Changes:**
- Added "Download All Slides" button to the calendar modal
- Made individual slide images clickable to download
- Each slide now has a hover effect indicating it's downloadable
- Downloads automatically name files with day and slide number

**Files affected:**
- `calendar-60day.html`

**Details:**
Users can now:
1. Click any slide image to download it individually
2. Click "Download All Slides" to download the entire carousel
3. Hover over images to see download indication (slight zoom + shadow)
