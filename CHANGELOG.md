# Changelog - Spectrum Unlocked

## 2026-04-04

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
