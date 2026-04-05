# Instagram & TikTok Size Specifications 2026

## Spectrum Unlocked Content Formats

### Primary Formats We Use
| Format | Dimensions | Ratio | Folder Pattern | Use Case |
|--------|------------|-------|----------------|----------|
| **Carousel** | 1080 x 1350 | 4:5 | `day-XX-topic/` | Educational slideshows, lists, guides |
| **Reel Slides** | 1080 x 1920 | 9:16 | `day-XX-topic-reel/` | TikTok, Instagram Reels, Stories |

### When to Use Each

**Use Carousel (1080x1350):**
- In-depth educational content
- Myth-busting with explanations
- Checklists and guides
- Content meant to be saved/shared
- Instagram feed priority

**Use Reel Slides (1080x1920):**
- Quick, punchy content
- Hook-first structure ("POV:", questions)
- TikTok-first content
- Trending topics needing fast turnaround
- Repurposing carousel topics for video

---

## All Instagram Formats

### Feed Posts
| Format | Dimensions | Ratio | Use Case |
|--------|------------|-------|----------|
| Portrait (Recommended) | 1080 x 1350 | 4:5 | Best engagement, takes more screen space |
| Tall (New Rec) | 1080 x 1440 | 3:4 | Maximum vertical feed space |
| Square | 1080 x 1080 | 1:1 | Classic, works everywhere |
| Landscape | 1080 x 566 | 1.91:1 | Wide shots, less common |

### Stories & Reels
| Format | Dimensions | Ratio | Notes |
|--------|------------|-------|-------|
| Stories/Reels | 1080 x 1920 | 9:16 | Full screen vertical |
| Safe Zone | 1080 x 1440 | - | Keep text/logos here (bottom 480px gets covered) |

### Profile
| Format | Dimensions | Ratio |
|--------|------------|-------|
| Profile Picture | 320 x 320 | 1:1 |

---

## TikTok Formats

| Format | Dimensions | Ratio | Notes |
|--------|------------|-------|-------|
| Video/Slides | 1080 x 1920 | 9:16 | Standard vertical |
| Safe Zone | 1080 x 1560 | - | Avoid bottom 360px (UI overlays) |

---

## Rendering Commands

```bash
# Carousel slide (4:5)
npx playwright screenshot --viewport-size=1080,1350 slide.html slide.png

# Reel slide (9:16)
npx playwright screenshot --viewport-size=1080,1920 slide.html slide.png

# All carousels in folder
for f in slide-*.html; do npx playwright screenshot --viewport-size=1080,1350 "$f" "${f%.html}.png"; done

# All reels in folder
for f in slide-*.html; do npx playwright screenshot --viewport-size=1080,1920 "$f" "${f%.html}.png"; done
```

---

## Key Tips
1. **Always use 1080px width** — prevents pixelation
2. **Portrait/Tall posts get more engagement** — take more screen space
3. **Carousel posts** — all images must be same aspect ratio
4. **Reels safe zone** — keep important content in top 1440px (IG) / 1560px (TikTok)
5. **Reel folders use `-reel` suffix** — keeps carousel and reel content separate

## Preview Sizes (for web editor at 4x scale)
| Format | Preview Size | Export Size |
|--------|--------------|-------------|
| Portrait/Carousel | 270 x 337 | 1080 x 1350 |
| Tall | 270 x 360 | 1080 x 1440 |
| Square | 270 x 270 | 1080 x 1080 |
| Landscape | 270 x 141 | 1080 x 566 |
| Stories/Reels | 180 x 320 | 1080 x 1920 |
