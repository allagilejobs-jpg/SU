"""
Generate carousel assets (1080x1350) for all 3 artists.

Standardized 4-slide layout for all artists:
  slide 1  cover       - A1 magazine style
  slide 2  video       - branded captioned clip (built by ffmpeg, not HTML)
  slide 3  quote       - big Playfair Display pull quote
  slide 4  cta         - mission + save/share/follow CTA

No slide numbers. Each artist's carousel lives in
content/curated/<slug>/carousel-v2/
"""
from pathlib import Path
import subprocess

BASE = Path("C:/Users/Solomon/Desktop/SU/content/curated")

# ---------------------------------------------------------------------------
# Artist data
# ---------------------------------------------------------------------------
ARTISTS = [
    {
        "slug": "holly-peete",
        "name": "Holly Robinson Peete",
        "name_upper": "HOLLY ROBINSON PEETE",
        "source": "via OWN",
        "cover_headline_lines": ['"Do I Have', 'Autism Still?"'],
        "quote_main": '"Do I have autism still?"',
        "quote_attribution": "RJ Peete to his mom on national TV",
        "photo": "cover-photo.png",
        "cta_label": "HOLLY'S MISSION",
        "cta_main": 'Autism is for <em>life.</em><br>So is love.',
        "cta_sub": 'Holly co-founded HollyRod Foundation to support families living with autism. Twenty years of advocacy. Still showing up.',
        "cta_button": "Tag an autism mom",
    },
    {
        "slug": "ot-genasis",
        "name": "OT Genasis",
        "name_upper": "OT GENASIS",
        "source": "via The Therapist",
        "cover_headline_lines": ['"My Son Is', 'On The Spectrum"'],
        "quote_main": '"Maybe he chose you."',
        "quote_attribution": "OT Genasis on his autistic son",
        "photo": "cover-photo.png",
        "cta_label": "OT'S TRUTH",
        "cta_main": 'Maybe he <em>chose</em> you.',
        "cta_sub": "Every autism dad needs to hear this. You weren't given a burden. You were given a son.",
        "cta_button": "Tag an autism dad",
    },
    {
        "slug": "faith-evans",
        "name": "Faith Evans",
        "name_upper": "FAITH EVANS",
        "source": "via Tamron Hall Show",
        "cover_headline_lines": ['"I Had To BEG', 'For A Diagnosis"'],
        "quote_main": '"I had to BEG for a diagnosis."',
        "quote_attribution": "Faith Evans on her son Ryder",
        "quote_main_2": '"No parent should have to beg alone."',
        "quote_attribution_2": "Why Faith built Ryder's Room Inc.",
        "photo": "cover-photo.png",
        "cta_label": "FAITH'S MISSION",
        "cta_main": 'No parent should<br>have to <em>beg.</em>',
        "cta_sub": "Faith Evans built Ryder's Room Inc. so no autism parent has to navigate the fight for a diagnosis alone.",
        "cta_button": "Tag an autism parent",
    },
    {
        "slug": "dan-orlovsky-madden",
        "name": "Madden Orlovsky",
        "name_upper": "MADDEN ORLOVSKY",
        "source": "via ESPN NFL Live",
        "cover_headline_lines": ['"Mom,', 'I Love You."'],
        "quote_main": '"Mom, I love you."',
        "quote_attribution": "14-year-old Madden Orlovsky on NFL Live",
        "photo": "cover-photo.png",
        "cta_label": "MADDEN'S STORY",
        "cta_main": 'Autism is <em>love,</em><br>spoken out loud.',
        "cta_sub": "14-year-old Madden Orlovsky told his family he loved them on national TV. His dad Dan couldn't hold it together. Neither could anyone watching.",
        "cta_button": "Tag a dad",
    },
    {
        "slug": "tisha-campbell",
        "name": "Tisha Campbell",
        "name_upper": "TISHA CAMPBELL",
        "source": "via The Real",
        "cover_headline_lines": ['"This Is A Boy', 'Who Couldn\'t Talk"'],
        "quote_main": '"This is a boy who couldn\'t talk."',
        "quote_attribution": "Tisha Campbell on her son Xen, now college-bound",
        "photo": "cover-photo.png",
        "cta_label": "TISHA'S TRUTH",
        "cta_main": 'Raise them to <em>not</em><br>need you.',
        "cta_sub": "Tisha Campbell's son Xen was diagnosed at 23 months. She raised him for independence. At 18, he chose her house because she was preparing him for college.",
        "cta_button": "Tag a strong mom",
    },
    {
        "slug": "rodney-peete",
        "name": "Rodney Peete",
        "name_upper": "RODNEY PEETE",
        "source": "via CBS Early Show",
        "cover_headline_lines": ['"I Was Stuck', 'In Denial"'],
        "quote_main": '"I was stuck in denial."',
        "quote_attribution": "Rodney Peete on his son RJ's autism diagnosis",
        "photo": "cover-photo.png",
        "cta_label": "RODNEY'S CONFESSION",
        "cta_main": 'Dads process autism<br><em>differently.</em>',
        "cta_sub": "Rodney Peete was stuck in denial. He threw the books Holly gave him under the bed. Then his son's treatment embarrassed him into action — and he wrote \"Not My Boy!\"",
        "cta_button": "Tag an autism dad",
    },
]

FONT_LINK = '<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800;900&family=Playfair+Display:wght@700;800;900:ital@0;1&display=swap" rel="stylesheet">'

# ---------------------------------------------------------------------------
# Slide 1: Cover (adapted from A1 magazine, 1080x1350)
# ---------------------------------------------------------------------------
def slide_cover(a):
    headline_html = "<br>".join(a["cover_headline_lines"])
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">{FONT_LINK}
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{
  width:1080px; height:1350px; font-family:'Poppins',sans-serif;
  position:relative; overflow:hidden;
  background:#0a0a12;
}}
.bg-photo {{
  position:absolute; inset:0; width:100%; height:100%;
  background-image:url('../{a["photo"]}');
  background-size:cover; background-position:center 15%;
}}
.gradient-top {{
  position:absolute; top:0; left:0; right:0; height:30%;
  background:linear-gradient(180deg, rgba(10,10,18,0.85) 0%, rgba(10,10,18,0) 100%);
}}
.gradient-bottom {{
  position:absolute; bottom:0; left:0; right:0; height:65%;
  background:linear-gradient(180deg, rgba(10,10,18,0) 0%, rgba(10,10,18,0.55) 30%, rgba(10,10,18,0.95) 72%, rgba(10,10,18,1) 100%);
}}
.brand {{ position:absolute; top:60px; left:50px; }}
.brand-main {{ font-size:40px; font-weight:900; color:white; letter-spacing:2px; text-shadow:0 2px 12px rgba(0,0,0,0.8); }}
.brand-sub {{ font-size:24px; font-weight:800; color:#4A90A4; letter-spacing:6px; margin-top:-4px; text-shadow:0 2px 12px rgba(0,0,0,0.8); }}
.headline-block {{
  position:absolute; left:60px; right:60px; bottom:200px;
}}
.name {{ font-size:34px; font-weight:800; color:#E8B86D; letter-spacing:4px; margin-bottom:16px; text-shadow:0 4px 16px rgba(0,0,0,0.8); }}
.headline {{
  font-size:88px; font-weight:900; color:white; line-height:0.98;
  letter-spacing:-2px; text-shadow:0 6px 24px rgba(0,0,0,0.85);
}}
.credit {{ position:absolute; bottom:90px; left:60px; font-size:22px; font-weight:600; color:rgba(255,255,255,0.75); text-shadow:0 2px 8px rgba(0,0,0,0.8); }}
.swipe {{ position:absolute; bottom:90px; right:60px; font-size:22px; font-weight:700; color:#E8B86D; text-shadow:0 2px 8px rgba(0,0,0,0.8); }}
.play-btn {{
  position:absolute; top:50%; left:50%; transform:translate(-50%,-50%);
  width:140px; height:140px; border-radius:50%;
  background:rgba(255,255,255,0.18);
  border:4px solid rgba(255,255,255,0.95);
  display:flex; align-items:center; justify-content:center;
  box-shadow:0 0 40px rgba(0,0,0,0.4), 0 0 0 12px rgba(255,255,255,0.08);
  backdrop-filter:blur(8px);
}}
.play-btn::after {{
  content:''; width:0; height:0;
  border-left:42px solid white;
  border-top:28px solid transparent;
  border-bottom:28px solid transparent;
  margin-left:10px;
  filter:drop-shadow(0 2px 8px rgba(0,0,0,0.4));
}}
</style></head>
<body>
  <div class="bg-photo"></div>
  <div class="gradient-top"></div>
  <div class="gradient-bottom"></div>
  <div class="brand"><div class="brand-main">SPECTRUM</div><div class="brand-sub">UNLOCKED</div></div>
  <div class="play-btn"></div>
  <div class="headline-block">
    <div class="name">{a["name_upper"]}</div>
    <div class="headline">{headline_html}</div>
  </div>
  <div class="credit">{a["source"]}</div>
  <div class="swipe">SWIPE →</div>
</body></html>
"""

# ---------------------------------------------------------------------------
# Slide 3: Quote card (1080x1350) - big Playfair pull quote
# ---------------------------------------------------------------------------
def slide_quote(a, quote, attribution):
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">{FONT_LINK}
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{
  width:1080px; height:1350px; font-family:'Poppins',sans-serif;
  background:linear-gradient(165deg, #1a1a2e 0%, #16213e 40%, #0f3460 100%);
  color:white; position:relative; overflow:hidden;
  display:flex; flex-direction:column; align-items:center; justify-content:center;
  padding:120px 80px;
}}
body::before {{
  content:''; position:absolute; top:-200px; right:-200px;
  width:700px; height:700px;
  background:radial-gradient(circle, rgba(232,184,109,0.18) 0%, transparent 70%);
}}
body::after {{
  content:''; position:absolute; bottom:-200px; left:-200px;
  width:700px; height:700px;
  background:radial-gradient(circle, rgba(74,144,164,0.2) 0%, transparent 70%);
}}
.brand {{ position:absolute; top:60px; left:60px; }}
.brand-main {{ font-size:36px; font-weight:900; color:white; letter-spacing:2px; }}
.brand-sub {{ font-size:22px; font-weight:800; color:#4A90A4; letter-spacing:5px; margin-top:-4px; }}
.quote-mark {{
  font-family:'Playfair Display', serif;
  font-size:280px; font-weight:900; color:#E8B86D;
  line-height:0.6; opacity:0.3;
  margin-bottom:-40px;
  position:relative; z-index:1;
}}
.quote {{
  font-family:'Playfair Display', serif;
  font-size:88px; font-weight:900; color:white;
  line-height:1.08; letter-spacing:-2px;
  text-align:center;
  position:relative; z-index:2;
  max-width:900px;
  margin-bottom:50px;
}}
.attribution {{
  font-size:26px; font-weight:600; color:rgba(255,255,255,0.8);
  text-align:center; letter-spacing:0.5px;
  position:relative; z-index:2;
  max-width:800px;
}}
.swipe {{ position:absolute; bottom:60px; right:60px; font-size:20px; font-weight:700; color:#E8B86D; letter-spacing:1px; }}
</style></head>
<body>
  <div class="brand"><div class="brand-main">SPECTRUM</div><div class="brand-sub">UNLOCKED</div></div>
  <div class="quote-mark">"</div>
  <div class="quote">{quote}</div>
  <div class="attribution">— {attribution}</div>
  <div class="swipe">SWIPE →</div>
</body></html>
"""

# ---------------------------------------------------------------------------
# Slide 4: CTA / Ending (1080x1350)
# ---------------------------------------------------------------------------
def slide_cta(a):
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">{FONT_LINK}
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  width:1080px; height:1350px;
  background:linear-gradient(165deg, #1a1a2e 0%, #16213e 40%, #0f3460 100%);
  font-family:'Poppins',sans-serif; color:white;
  padding:120px 80px;
  position:relative; overflow:hidden;
  display:flex; flex-direction:column;
  align-items:center; justify-content:center; text-align:center;
}}
body::before {{
  content:''; position:absolute; top:-180px; right:-180px;
  width:580px; height:580px;
  background:#E8B86D; border-radius:50%; opacity:0.1;
}}
body::after {{
  content:''; position:absolute; bottom:-140px; left:-140px;
  width:440px; height:440px;
  background:#4A90A4; border-radius:50%; opacity:0.1;
}}
.brand {{ position:absolute; top:60px; left:60px; }}
.brand-main {{ font-size:36px; font-weight:900; color:white; letter-spacing:2px; }}
.brand-sub {{ font-size:22px; font-weight:800; color:#4A90A4; letter-spacing:5px; margin-top:-4px; }}
.label {{
  font-size:24px; font-weight:700; color:#4A90A4;
  text-transform:uppercase; letter-spacing:5px;
  margin-bottom:40px;
  position:relative; z-index:1;
}}
.main-msg {{
  font-family:'Playfair Display', serif;
  font-size:92px; font-weight:900; line-height:1.03;
  margin-bottom:40px; max-width:900px;
  position:relative; z-index:1;
}}
.main-msg em {{ color:#E8B86D; font-style:italic; }}
.sub-msg {{
  font-size:28px; font-weight:500; line-height:1.45;
  max-width:820px; opacity:0.92;
  margin-bottom:55px;
  position:relative; z-index:1;
}}
.actions {{
  display:flex; gap:70px;
  position:relative; z-index:1;
  margin-bottom:50px;
}}
.action {{
  display:flex; flex-direction:column; align-items:center; gap:8px;
  font-size:22px; font-weight:700;
}}
.action-icon {{ font-size:56px; }}
.cta-box {{
  background:linear-gradient(135deg, #E8B86D 0%, #d4a85d 100%);
  color:#1a1a2e; padding:26px 56px;
  border-radius:18px;
  position:relative; z-index:1;
  box-shadow:0 10px 36px rgba(232,184,109,0.35);
}}
.cta-text {{ font-size:32px; font-weight:900; }}
.handle {{
  position:absolute; bottom:60px;
  font-size:26px; font-weight:700; color:#E8B86D; letter-spacing:1px;
}}
</style></head>
<body>
  <div class="brand"><div class="brand-main">SPECTRUM</div><div class="brand-sub">UNLOCKED</div></div>
  <div class="label">{a["cta_label"]}</div>
  <div class="main-msg">{a["cta_main"]}</div>
  <div class="sub-msg">{a["cta_sub"]}</div>
  <div class="actions">
    <div class="action"><span class="action-icon">&#128190;</span><span>Save</span></div>
    <div class="action"><span class="action-icon">&#128228;</span><span>Share</span></div>
    <div class="action"><span class="action-icon">&#10133;</span><span>Follow</span></div>
  </div>
  <div class="cta-box"><div class="cta-text">{a["cta_button"]}</div></div>
  <div class="handle">@spectrum_unlocked</div>
</body></html>
"""

# ---------------------------------------------------------------------------
# Build all HTML files
# ---------------------------------------------------------------------------
# Standardized 3-slide carousel for all artists:
#   slide 1 - cover (A1 magazine style at 1080x1350)
#   slide 2 - video (handled by ffmpeg, not HTML)
#   slide 3 - CTA / ending
def build_html_for_artist(a):
    slug = a["slug"]
    out_dir = BASE / slug / "carousel-v2"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Remove any stale slide files from previous layouts
    for stale in [
        "slide-2-quote.html", "slide-2-quote.png",
        "slide-3-cta.html",   "slide-3-cta.png",
        "slide-4-quote.html", "slide-4-quote.png",
        "slide-5-cta.html",   "slide-5-cta.png",
    ]:
        p = out_dir / stale
        if p.exists():
            p.unlink()

    files_written = []
    (out_dir / "slide-1-cover.html").write_text(slide_cover(a), encoding="utf-8")
    files_written.append("slide-1-cover.html")
    # slide-2 is the video (built by ffmpeg separately)
    (out_dir / "slide-3-quote.html").write_text(
        slide_quote(a, a["quote_main"], a["quote_attribution"]),
        encoding="utf-8",
    )
    files_written.append("slide-3-quote.html")
    (out_dir / "slide-4-cta.html").write_text(slide_cta(a), encoding="utf-8")
    files_written.append("slide-4-cta.html")
    return files_written

for a in ARTISTS:
    files = build_html_for_artist(a)
    print(f"{a['slug']}: {len(files)} HTML files: {files}")
