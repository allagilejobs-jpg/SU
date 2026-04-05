# ARCHITECTURE.md - Technical Documentation
## Spectrum Unlocked Content System

**Last Updated:** April 5, 2026

---

## 1. Repository Structure

```
/Users/aramide/clawd/SU/
├── index.html                    # Home/landing page
├── calendar-60day.html           # Visual calendar dashboard (MAIN TOOL)
├── content-calendar-60day.md     # Master content plan (SOURCE OF TRUTH)
├── brand-guidelines.html         # Design system documentation
├── create-graphic.html           # Graphic creation tool
├── editor.html                   # Live HTML editor with preview
├── template-gallery.html         # Reusable template library
│
├── content/                      # All day-by-day content
│   ├── day-01-tiktok-myths/
│   ├── day-02-acceptance-vs-awareness/
│   ├── ...
│   └── day-XX-topic/
│       ├── slide-01-cover.html   # HTML template
│       ├── slide-01-cover.png    # Rendered PNG
│       ├── slide-02-*.html/png
│       ├── ...
│       └── captions.md           # Platform captions
│
├── graphics/                     # Standalone graphics (non-calendar)
├── research/                     # Content research files
├── weekly-ideas/                 # AI-generated content ideas
├── docs/                         # Additional documentation
│
├── reel-*/                       # Reel/video slide templates
├── sensory-hacks/                # Sensory hacks mini-series
├── tiktok/                       # TikTok-specific content
│
├── js/                           # JavaScript modules
│   └── instagram-sizes.js        # Size constants
│
├── render-server.js              # Local server for rendering
├── render.sh                     # Rendering script
├── start.sh                      # Start local dev server
├── Start Editor.command          # macOS double-click launcher
│
├── CHANGELOG.md                  # Change history
├── PRD.md                        # Product requirements
├── ARCHITECTURE.md               # This file
└── package.json                  # Node dependencies
```

---

## 2. Key Files Explained

### `content-calendar-60day.md` (Source of Truth)
- Complete 60-day content plan in markdown
- Contains morning/afternoon/evening posts for each day
- Includes hooks, topics, hashtags, format details
- **This is what you reference when creating content**

### `calendar-60day.html` (Visual Dashboard)
- Interactive calendar showing all days
- Click a day to see details, captions, slide previews
- Shows "ready" vs "planned" status
- Contains `dayData` JavaScript object with all content metadata
- **This is what you use to post content**

### `content/day-XX-*/` (Day Folders)
Each day folder contains:
```
day-11-masking/
├── captions.md           # Instagram + TikTok captions
├── slide-01-cover.html   # HTML source
├── slide-01-cover.png    # Rendered 1080x1350 PNG
├── slide-02-what.html
├── slide-02-what.png
├── slide-03-why.html
├── slide-03-why.png
├── ...
└── slide-06-cta.html/png
```

### `captions.md` Format
```markdown
# Day XX - Date
## 🔄 Both Platforms | Carousel

### Topic
**Title Here**

### Hook
"The scroll-stopping first line"

---

## 📸 Instagram Caption
[Full caption with emojis, line breaks]

---
#hashtag1 #hashtag2 ...

---

## 📱 TikTok Caption
[Shorter caption]
#hashtag1 #hashtag2 #fyp

---

## Content Notes
- Why it works
- Format notes
- Post timing
```

---

## 3. HTML Slide Template Structure

### Basic Template
```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&family=Playfair+Display:wght@700&display=swap" rel="stylesheet">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    
    .slide {
      width: 1080px;
      height: 1350px;
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
      padding: 60px;
      display: flex;
      flex-direction: column;
      font-family: 'Poppins', sans-serif;
      color: white;
    }
    
    /* Add your styles */
  </style>
</head>
<body>
  <div class="slide">
    <!-- Content here -->
  </div>
</body>
</html>
```

### Design Constants
```css
/* Colors */
--teal: #4A90A4;
--gold: #E8B86D;
--green: #27AE60;
--bg-primary: #1a1a2e;
--bg-secondary: #16213e;
--bg-tertiary: #0f3460;

/* Typography */
font-family: 'Poppins', sans-serif;      /* Body */
font-family: 'Playfair Display', serif;  /* Headings */

/* Dimensions */
width: 1080px;
height: 1350px;  /* Instagram carousel 4:5 */
padding: 60px;   /* Standard slide padding */
```

---

## 4. Rendering Pipeline

### Method 1: Playwright CLI (Recommended)
```bash
# Single slide
npx playwright screenshot --viewport-size=1080,1350 slide-01-cover.html slide-01-cover.png

# All slides in a folder
for f in slide-*.html; do
  npx playwright screenshot --viewport-size=1080,1350 "$f" "${f%.html}.png"
done
```

### Method 2: Local Render Server
```bash
# Start the server
./start.sh
# or
node render-server.js

# Visit http://localhost:3000
# Use the editor to preview and export
```

### Method 3: Editor GUI
1. Open `editor.html` in browser
2. Paste/edit HTML
3. Click "Export PNG"
4. Uses html2canvas library

### Rendering Requirements
- Node.js v18+
- Playwright: `npm install -D playwright`
- Chromium browser (Playwright installs this)

---

## 5. Calendar Dashboard (`calendar-60day.html`)

### JavaScript Data Structure
The calendar uses a `dayData` object to store content metadata:

```javascript
const dayData = {
  1: {
    title: "3 Things TikTok Gets WRONG About Autism",
    folder: "day-01-tiktok-myths",
    slides: 5,
    igCaption: "Full Instagram caption...",
    igHashtags: "#autism #autismawareness ...",
    tiktokCaption: "Short TikTok caption..."
  },
  2: { ... },
  // etc.
};

const slideNames = {
  1: ["cover", "myth1", "myth2", "myth3", "cta"],
  2: ["cover", "what", "why", "how", "cta"],
  // Maps day number to slide name suffixes
};
```

### Adding a New Day
1. Create the day folder in `content/`
2. Add entry to `dayData` object
3. Add entry to `slideNames` object
4. Update the day card HTML to include `onclick="openDay(X)"`
5. Update stats bar numbers

### Day Card HTML Structure
```html
<div class="day-card ready" onclick="openDay(11)">
  <div class="day-top">
    <div class="day-num">11</div>
    <div class="day-info">
      <div class="weekday">Saturday</div>
      <div class="date">Apr 5</div>
    </div>
    <span class="platform-badge both">🔄</span>
  </div>
  <div class="day-content">
    <div class="day-title">High-Masking Autism</div>
    <div class="day-hook">The hidden struggle</div>
  </div>
  <div class="day-status">
    <span class="status-dot ready"></span>
    <span>6 slides ready</span>
  </div>
</div>
```

### Status Classes
- `.ready` - Green border, content is done
- `.hero` - Gold border, special/important day
- No class - Planned but not created

---

## 6. File Naming Conventions

### Day Folders
```
day-XX-short-topic-name/
```
- XX = zero-padded day number (01, 02, ... 60)
- Use lowercase, hyphens for spaces
- Keep it short but descriptive

### Slide Files
```
slide-01-cover.html
slide-01-cover.png
slide-02-what.html
slide-02-what.png
```
- Numbered in order (01, 02, 03...)
- Descriptive suffix (cover, what, why, tips, cta)
- HTML and PNG have matching names

### Image Assets
- Use descriptive names
- Lowercase, hyphens
- Include dimensions if relevant: `icon-headphones-64.png`

---

## 7. GitHub Pages Deployment

### Repository
- **Repo:** https://github.com/allagilejobs-jpg/SU
- **Pages URL:** https://allagilejobs-jpg.github.io/SU/

### Deployment
GitHub Pages automatically deploys from the main branch. Just push:
```bash
git add -A
git commit -m "Your message"
git push
```

Changes are live within 1-2 minutes.

### Important Files for Pages
- `index.html` - Landing page
- `calendar-60day.html` - Main calendar
- `content/` - All graphics (served as static files)
- `brand-guidelines.html` - Design reference

---

## 8. Local Development

### Quick Start
```bash
cd /Users/aramide/clawd/SU

# Option 1: Use the start script
./start.sh

# Option 2: Simple Python server
python3 -m http.server 8000

# Option 3: Node server for rendering
node render-server.js
```

### Editor Tools
- `editor.html` - Full HTML editor with live preview
- `create-graphic.html` - Template-based graphic creator
- `html-editor.html` - Simplified editor

### Useful Commands
```bash
# Render a slide
npx playwright screenshot --viewport-size=1080,1350 slide.html slide.png

# Render all slides in current directory
for f in slide-*.html; do npx playwright screenshot --viewport-size=1080,1350 "$f" "${f%.html}.png"; done

# Check what days are ready
ls content/ | grep "day-" | wc -l
```

---

## 9. Integration with Clawdbot

### Workspace Location
```
/Users/aramide/clawd/SU/
```

### Related Cron Jobs
| Job ID | Name | Schedule | Action |
|--------|------|----------|--------|
| 544b0294... | SU Daily Posting Reminder | 9am daily | Checks calendar, sends Telegram reminder |
| 89bdc5a0... | SU Weekly Content Brainstorm | 8pm Sun | Generates 7 post ideas, saves to `weekly-ideas/` |
| 68dc7b83... | SU Content Research | 12pm Wed | Researches trends, saves to `research/` |

### TOOLS.md Reference
The main Clawdbot workspace has SU documentation in `TOOLS.md` with:
- Repo locations
- Workflow instructions
- Rendering commands

---

## 10. Troubleshooting

### Slides Not Rendering
1. Check Playwright is installed: `npx playwright --version`
2. Install browsers: `npx playwright install chromium`
3. Check viewport size matches slide dimensions

### Calendar Not Showing Content
1. Verify `dayData` has the day entry
2. Check `slideNames` mapping exists
3. Ensure folder name in `dayData.folder` matches actual folder
4. Look for JavaScript errors in browser console

### Fonts Not Loading
- Google Fonts requires internet connection
- Check the `<link>` tag in HTML head
- Verify font-family matches exactly

### Images Too Large
- PNGs are typically 300-500KB each
- Carousel with 6 slides ≈ 2-3MB total
- Consider optimizing with: `optipng -o7 *.png`

---

## 11. Content Checklist for New Days

When creating content for a new day:

- [ ] Read the plan in `content-calendar-60day.md`
- [ ] Create folder: `content/day-XX-topic/`
- [ ] Create `slide-01-cover.html` (hook/title)
- [ ] Create content slides (3-5 typically)
- [ ] Create `slide-XX-cta.html` (call to action)
- [ ] Render all slides to PNG
- [ ] Create `captions.md` with both platform captions
- [ ] Add to `dayData` in `calendar-60day.html`
- [ ] Add to `slideNames` in `calendar-60day.html`
- [ ] Update stats bar (Days Ready count)
- [ ] Update day card status to "ready"
- [ ] Commit and push to GitHub

---

## 12. Quick Reference

### Slide Dimensions
| Platform | Size | Ratio |
|----------|------|-------|
| Instagram Carousel | 1080 x 1350 | 4:5 |
| Instagram Story | 1080 x 1920 | 9:16 |
| TikTok | 1080 x 1920 | 9:16 |

### Color Palette
| Color | Hex | RGB |
|-------|-----|-----|
| Teal | #4A90A4 | 74, 144, 164 |
| Gold | #E8B86D | 232, 184, 109 |
| Green | #27AE60 | 39, 174, 96 |
| Red | #E74C3C | 231, 76, 60 |
| BG Primary | #1a1a2e | 26, 26, 46 |
| BG Secondary | #16213e | 22, 33, 62 |
| BG Tertiary | #0f3460 | 15, 52, 96 |

### Font Stack
```css
/* Headings */
font-family: 'Playfair Display', Georgia, serif;

/* Body */
font-family: 'Poppins', -apple-system, BlinkMacSystemFont, sans-serif;
```

---

*This architecture document should be updated when structural changes are made.*
