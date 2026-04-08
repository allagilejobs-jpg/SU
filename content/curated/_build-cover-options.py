"""
Generate 3 cover slide designs × 2 artists = 6 HTML files at native 1080x1920.
Each cover includes a play-button cue so viewers know it's a video.
"""
from pathlib import Path

BASE = Path("C:/Users/Solomon/Desktop/SU/content/curated")

ARTISTS = {
    "holly-peete": {
        "brand_main": "SPECTRUM",
        "brand_sub":  "UNLOCKED",
        "name":       "RJ PEETE",
        "headline":   '"Do I Have<br>Autism Still?"',
        "credit":     "via OWN",
        "photo":      "cover-photo.png",
    },
    "ot-genasis": {
        "brand_main": "SPECTRUM",
        "brand_sub":  "UNLOCKED",
        "name":       "OT GENASIS",
        "headline":   '"My Son Is<br>On The Spectrum"',
        "credit":     "via The Therapist",
        "photo":      "cover-photo.png",
    },
    "faith-evans": {
        "brand_main": "SPECTRUM",
        "brand_sub":  "UNLOCKED",
        "name":       "FAITH EVANS",
        "headline":   '"I Had To BEG<br>For A Diagnosis"',
        "credit":     "via Tamron Hall Show",
        "photo":      "cover-photo.png",
    },
}

# ---------------------------------------------------------------------------
# Shared CSS bits
# ---------------------------------------------------------------------------
FONTS = '<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600;700;800;900&family=Playfair+Display:wght@800;900&display=swap" rel="stylesheet">'

# Pulsing play button (universal "this is a video" cue)
PLAY_BUTTON_CSS = """
.play-btn {
  position: absolute;
  width: 160px;
  height: 160px;
  border-radius: 50%;
  background: rgba(255,255,255,0.18);
  border: 4px solid rgba(255,255,255,0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 40px rgba(0,0,0,0.4), 0 0 0 14px rgba(255,255,255,0.08);
  backdrop-filter: blur(8px);
}
.play-btn::after {
  content: '';
  display: block;
  width: 0;
  height: 0;
  border-left: 50px solid white;
  border-top: 32px solid transparent;
  border-bottom: 32px solid transparent;
  margin-left: 12px;
  filter: drop-shadow(0 2px 8px rgba(0,0,0,0.4));
}
"""

# ---------------------------------------------------------------------------
# DESIGN A1: Magazine cover (full-bleed photo, gradient, big bottom headline)
# ---------------------------------------------------------------------------
def design_a1(a):
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">{FONTS}
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{
  width:1080px; height:1920px; font-family:'Poppins',sans-serif;
  position:relative; overflow:hidden;
  background:#0a0a12;
}}
.bg-photo {{
  position:absolute; inset:0; width:100%; height:100%;
  background-image:url('{a["photo"]}');
  background-size:cover; background-position:center top;
}}
.gradient-top {{
  position:absolute; top:0; left:0; right:0; height:30%;
  background:linear-gradient(180deg, rgba(10,10,18,0.85) 0%, rgba(10,10,18,0) 100%);
}}
.gradient-bottom {{
  position:absolute; bottom:0; left:0; right:0; height:60%;
  background:linear-gradient(180deg, rgba(10,10,18,0) 0%, rgba(10,10,18,0.55) 35%, rgba(10,10,18,0.95) 75%, rgba(10,10,18,1) 100%);
}}
.brand {{ position:absolute; top:90px; left:60px; }}
.brand-main {{ font-size:42px; font-weight:900; color:white; letter-spacing:2px; text-shadow:0 2px 12px rgba(0,0,0,0.8); }}
.brand-sub  {{ font-size:26px; font-weight:800; color:#4A90A4; letter-spacing:6px; margin-top:-4px; text-shadow:0 2px 12px rgba(0,0,0,0.8); }}
.headline-block {{
  position:absolute; left:60px; right:60px; bottom:280px;
}}
.name {{ font-size:38px; font-weight:800; color:#E8B86D; letter-spacing:4px; margin-bottom:18px; text-shadow:0 4px 16px rgba(0,0,0,0.8); }}
.headline {{
  font-size:96px; font-weight:900; color:white; line-height:0.98;
  letter-spacing:-2px; text-shadow:0 6px 24px rgba(0,0,0,0.85);
}}
.credit {{ position:absolute; bottom:130px; left:60px; right:60px; font-size:24px; font-weight:600; color:rgba(255,255,255,0.75); text-shadow:0 2px 8px rgba(0,0,0,0.8); }}
.play-btn {{ top:50%; left:50%; transform:translate(-50%,-50%); }}
{PLAY_BUTTON_CSS}
</style></head>
<body>
  <div class="bg-photo"></div>
  <div class="gradient-top"></div>
  <div class="gradient-bottom"></div>
  <div class="brand"><div class="brand-main">{a["brand_main"]}</div><div class="brand-sub">{a["brand_sub"]}</div></div>
  <div class="play-btn"></div>
  <div class="headline-block">
    <div class="name">{a["name"]}</div>
    <div class="headline">{a["headline"]}</div>
  </div>
  <div class="credit">{a["credit"]}</div>
</body></html>
"""

# ---------------------------------------------------------------------------
# DESIGN A2: Navy minimalist (existing brand style, native 1080x1920)
# ---------------------------------------------------------------------------
def design_a2(a):
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">{FONTS}
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{
  width:1080px; height:1920px; font-family:'Poppins',sans-serif;
  position:relative; overflow:hidden;
  background:linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%);
}}
.deco-circle-1 {{
  position:absolute; top:-150px; right:-200px; width:600px; height:600px;
  border-radius:50%; background:radial-gradient(circle, rgba(232,184,109,0.18) 0%, transparent 70%);
}}
.deco-circle-2 {{
  position:absolute; bottom:-200px; left:-200px; width:700px; height:700px;
  border-radius:50%; background:radial-gradient(circle, rgba(74,144,164,0.22) 0%, transparent 70%);
}}
.brand {{ position:absolute; top:90px; left:60px; }}
.brand-main {{ font-size:44px; font-weight:900; color:white; letter-spacing:2px; }}
.brand-sub  {{ font-size:26px; font-weight:800; color:#4A90A4; letter-spacing:6px; margin-top:-4px; }}
.photo-frame {{
  position:absolute; top:240px; left:50%; transform:translateX(-50%);
  width:880px; height:880px; border-radius:24px; overflow:hidden;
  border:4px solid rgba(232,184,109,0.55);
  box-shadow:0 24px 80px rgba(0,0,0,0.6);
  background-image:url('{a["photo"]}');
  background-size:cover; background-position:center top;
}}
.play-btn {{ top:680px; left:50%; transform:translate(-50%,-50%); }}
.headline-block {{
  position:absolute; bottom:240px; left:60px; right:60px; text-align:center;
}}
.name {{ font-size:34px; font-weight:800; color:#E8B86D; letter-spacing:5px; margin-bottom:14px; }}
.headline {{
  font-size:74px; font-weight:900; color:white; line-height:1.05;
  letter-spacing:-1px;
}}
.credit {{ position:absolute; bottom:130px; left:0; right:0; text-align:center; font-size:24px; font-weight:600; color:rgba(255,255,255,0.7); }}
{PLAY_BUTTON_CSS}
</style></head>
<body>
  <div class="deco-circle-1"></div>
  <div class="deco-circle-2"></div>
  <div class="brand"><div class="brand-main">{a["brand_main"]}</div><div class="brand-sub">{a["brand_sub"]}</div></div>
  <div class="photo-frame"></div>
  <div class="play-btn"></div>
  <div class="headline-block">
    <div class="name">{a["name"]}</div>
    <div class="headline">{a["headline"]}</div>
  </div>
  <div class="credit">{a["credit"]}</div>
</body></html>
"""

# ---------------------------------------------------------------------------
# DESIGN A3: Split layout (top 60% photo, bottom 40% headline)
# ---------------------------------------------------------------------------
def design_a3(a):
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">{FONTS}
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{
  width:1080px; height:1920px; font-family:'Poppins',sans-serif;
  position:relative; overflow:hidden;
  background:#0a0a12;
}}
.photo {{
  position:absolute; top:0; left:0; right:0; height:1180px;
  background-image:url('{a["photo"]}');
  background-size:cover; background-position:center 25%;
}}
.photo::after {{
  content:''; position:absolute; bottom:0; left:0; right:0; height:280px;
  background:linear-gradient(180deg, rgba(10,10,18,0) 0%, rgba(10,10,18,0.95) 80%, #0a0a12 100%);
}}
.brand {{ position:absolute; top:90px; left:60px; z-index:5; }}
.brand-main {{ font-size:42px; font-weight:900; color:white; letter-spacing:2px; text-shadow:0 4px 14px rgba(0,0,0,0.8); }}
.brand-sub  {{ font-size:26px; font-weight:800; color:#4A90A4; letter-spacing:6px; margin-top:-4px; text-shadow:0 4px 14px rgba(0,0,0,0.8); }}
.play-btn {{ top:560px; left:50%; transform:translate(-50%,-50%); z-index:5; }}
.bottom {{
  position:absolute; left:0; right:0; bottom:0; top:1180px;
  background:linear-gradient(180deg, #0a0a12 0%, #1a1a2e 100%);
  padding:80px 60px 130px;
  border-top:3px solid rgba(232,184,109,0.55);
}}
.name {{ font-size:38px; font-weight:800; color:#E8B86D; letter-spacing:5px; margin-bottom:24px; }}
.headline {{
  font-size:96px; font-weight:900; color:white; line-height:0.98;
  letter-spacing:-2px;
}}
.credit {{
  position:absolute; bottom:60px; left:60px; right:60px;
  font-size:24px; font-weight:600; color:rgba(255,255,255,0.7);
}}
{PLAY_BUTTON_CSS}
</style></head>
<body>
  <div class="photo"></div>
  <div class="brand"><div class="brand-main">{a["brand_main"]}</div><div class="brand-sub">{a["brand_sub"]}</div></div>
  <div class="play-btn"></div>
  <div class="bottom">
    <div class="name">{a["name"]}</div>
    <div class="headline">{a["headline"]}</div>
    <div class="credit">{a["credit"]}</div>
  </div>
</body></html>
"""

DESIGNS = {
    "a1-magazine": design_a1,
    "a2-minimalist": design_a2,
    "a3-split": design_a3,
}

for slug, content in ARTISTS.items():
    out_dir = BASE / slug / "cover-options"
    out_dir.mkdir(parents=True, exist_ok=True)
    for d_name, d_fn in DESIGNS.items():
        html = d_fn(content)
        # Photo path needs to be relative from cover-options/ → ../cover-photo.png
        html = html.replace("url('cover-photo.png')", "url('../cover-photo.png')")
        p = out_dir / f"{d_name}.html"
        p.write_text(html, encoding="utf-8")
        print(f"wrote {p}")
