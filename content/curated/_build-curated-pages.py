"""
Build the Curated hub + per-artist pages, styled to match the calendar pages.
Output:
  content/curated/index.html
  content/curated/<slug>/index.html
"""
from pathlib import Path

BASE = Path("C:/Users/Solomon/Desktop/SU/content/curated")

# ---------------------------------------------------------------------------
# Shared CSS (calendar-style visual language)
# ---------------------------------------------------------------------------
CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Poppins', sans-serif; background: #1a1a2e; color: #eee; min-height: 100vh; padding-bottom: 60px; }

.main-nav { background: #0f0f1a; padding: 15px 20px; display: flex; justify-content: center; gap: 15px; flex-wrap: wrap; position: sticky; top: 0; z-index: 100; }
.main-nav a { color: #aaa; text-decoration: none; padding: 10px 20px; border-radius: 25px; font-weight: 600; font-size: 14px; transition: all 0.2s; }
.main-nav a:hover, .main-nav a.active { background: #4A90A4; color: white; }
.nav-dropdown { position: relative; }
.dropdown-toggle { cursor: pointer; }
.dropdown-menu { display: none; position: absolute; right: 0; top: 100%; background: #0f0f1a; border: 1px solid #2a2a4a; border-radius: 12px; padding: 15px; min-width: 280px; max-height: 70vh; overflow-y: auto; z-index: 200; box-shadow: 0 10px 40px rgba(0,0,0,0.5); }
.nav-dropdown:hover .dropdown-menu, .dropdown-menu:hover { display: block; }
.dropdown-group { margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px solid #2a2a4a; }
.dropdown-group:last-child { margin-bottom: 0; padding-bottom: 0; border-bottom: none; }
.dropdown-label { color: #E8B86D; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 8px; padding: 0 10px; }
.dropdown-menu a { display: block; color: #ccc; text-decoration: none; padding: 6px 10px; border-radius: 8px; font-size: 13px; font-weight: 500; transition: all 0.2s; }
.dropdown-menu a:hover { background: #4A90A4; color: white; }

.header { background: linear-gradient(135deg, #4A90A4 0%, #2C5F6E 100%); padding: 36px 20px; text-align: center; }
.header .source-tag { display: inline-block; font-size: 12px; font-weight: 700; color: rgba(255,255,255,0.85); letter-spacing: 4px; text-transform: uppercase; margin-bottom: 10px; }
.header h1 { font-family: 'Playfair Display', serif; font-size: 2.4rem; margin-bottom: 10px; line-height: 1.1; }
.header h1 .em { color: #E8B86D; font-style: italic; }
.header p { opacity: 0.92; font-size: 1.05rem; max-width: 720px; margin: 0 auto; line-height: 1.55; }

.container { max-width: 1100px; margin: 0 auto; padding: 30px 20px; }

.section-card { background: #16213e; border-radius: 16px; margin-bottom: 22px; overflow: hidden; box-shadow: 0 5px 20px rgba(0,0,0,0.2); }
.section-header { background: #0f3460; padding: 16px 22px; display: flex; align-items: center; gap: 14px; }
.section-num { background: #E8B86D; color: #1a1a2e; width: 42px; height: 42px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 18px; flex-shrink: 0; }
.section-info h3 { font-size: 1rem; color: #E8B86D; }
.section-info .sub { font-size: 0.82rem; opacity: 0.7; margin-top: 2px; }
.section-content { padding: 22px; }

.reel-grid { display: grid; grid-template-columns: 320px 1fr; gap: 28px; align-items: start; }
.reel-player { background: black; border-radius: 12px; overflow: hidden; aspect-ratio: 9/16; }
.reel-player video { width: 100%; height: 100%; display: block; }
.reel-info p { line-height: 1.65; opacity: 0.85; margin-bottom: 18px; font-size: 0.95rem; }
.meta-row { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 22px; }
.meta { font-size: 11px; font-weight: 700; padding: 6px 12px; border-radius: 12px; background: rgba(74,144,164,0.25); color: #4A90A4; border: 1px solid rgba(74,144,164,0.4); letter-spacing: 0.5px; }
.meta.gold { background: rgba(232,184,109,0.18); color: #E8B86D; border-color: rgba(232,184,109,0.4); }

.btn { display: inline-flex; align-items: center; gap: 10px; background: linear-gradient(135deg, #E8B86D 0%, #D4A84B 100%); color: #1a1a2e; text-decoration: none; padding: 13px 26px; border-radius: 10px; font-weight: 800; font-size: 14px; transition: transform 0.15s, box-shadow 0.15s; box-shadow: 0 6px 20px rgba(232,184,109,0.25); }
.btn:hover { transform: translateY(-2px); box-shadow: 0 10px 28px rgba(232,184,109,0.4); }

.carousel-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 18px; }
.slide { background: #0f3460; border-radius: 12px; overflow: hidden; border: 1px solid rgba(255,255,255,0.06); display: flex; flex-direction: column; }
.slide-thumb { aspect-ratio: 4/5; background: black; position: relative; overflow: hidden; }
.slide-thumb img, .slide-thumb video { width: 100%; height: 100%; object-fit: cover; display: block; }
.slide-thumb .play-overlay { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.18); pointer-events: none; }
.slide-thumb .play-overlay::after { content: ''; width: 0; height: 0; border-left: 22px solid white; border-top: 14px solid transparent; border-bottom: 14px solid transparent; margin-left: 6px; filter: drop-shadow(0 2px 6px rgba(0,0,0,0.5)); }
.slide-body { padding: 14px 16px 16px; display: flex; flex-direction: column; gap: 8px; }
.slide-num { font-size: 10px; font-weight: 700; color: #E8B86D; letter-spacing: 1.5px; }
.slide-title { font-size: 13px; font-weight: 700; line-height: 1.35; }
.slide-desc { font-size: 11px; opacity: 0.6; line-height: 1.4; }
.slide-dl { margin-top: auto; }
.slide-dl a { display: flex; align-items: center; justify-content: center; gap: 6px; padding: 9px; background: rgba(232,184,109,0.15); color: #E8B86D; text-decoration: none; border-radius: 8px; font-weight: 700; font-size: 11px; border: 1px solid rgba(232,184,109,0.3); transition: all 0.15s; }
.slide-dl a:hover { background: rgba(232,184,109,0.25); }

.caption-box { background: #0a1628; border: 1px solid #0f3460; border-radius: 10px; padding: 18px 18px 18px 18px; font-size: 0.92rem; line-height: 1.7; color: #ddd; white-space: pre-wrap; word-wrap: break-word; position: relative; margin-bottom: 16px; font-family: 'Poppins', sans-serif; }
.caption-box .label { font-size: 10px; font-weight: 700; color: #4A90A4; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 12px; display: block; }
.copy-btn { position: absolute; top: 14px; right: 14px; background: #27AE60; color: white; border: none; padding: 7px 14px; border-radius: 8px; font-family: 'Poppins', sans-serif; font-weight: 600; font-size: 0.75rem; cursor: pointer; transition: all 0.2s; }
.copy-btn:hover { background: #2ecc71; transform: scale(1.05); }
.caption-text { padding-right: 70px; }

.toast { position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%); background: #27AE60; color: white; padding: 14px 28px; border-radius: 10px; font-weight: 600; box-shadow: 0 10px 40px rgba(0,0,0,0.3); opacity: 0; transition: opacity 0.3s; z-index: 1000; }
.toast.show { opacity: 1; }

/* Hub-specific */
.artist-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 22px; }
.artist-card { background: #16213e; border-radius: 16px; overflow: hidden; text-decoration: none; color: inherit; transition: transform 0.2s, box-shadow 0.2s; box-shadow: 0 5px 20px rgba(0,0,0,0.2); display: flex; flex-direction: column; }
.artist-card:hover { transform: translateY(-4px); box-shadow: 0 12px 32px rgba(0,0,0,0.4), 0 0 0 1px rgba(232,184,109,0.4); }
.artist-photo { aspect-ratio: 4/5; background-size: cover; background-position: center top; position: relative; }
.artist-photo::after { content: ''; position: absolute; inset: 0; background: linear-gradient(180deg, rgba(22,33,62,0) 55%, rgba(22,33,62,0.95) 100%); }
.artist-body { padding: 20px 22px 24px; display: flex; flex-direction: column; flex: 1; }
.artist-source { font-size: 11px; color: #E8B86D; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 8px; }
.artist-name { font-family: 'Playfair Display', serif; font-size: 1.5rem; font-weight: 700; margin-bottom: 12px; color: white; }
.artist-quote { font-size: 14px; line-height: 1.55; color: rgba(255,255,255,0.78); font-style: italic; margin-bottom: 16px; flex: 1; }
.artist-badges { display: flex; gap: 8px; flex-wrap: wrap; }

.notice-box { background: rgba(232,184,109,0.08); border: 1px solid rgba(232,184,109,0.25); border-radius: 10px; padding: 14px 18px; margin-bottom: 18px; font-size: 0.88rem; line-height: 1.55; color: #E8B86D; }
.notice-box strong { display: block; margin-bottom: 4px; }

@media (max-width: 800px) {
  .reel-grid { grid-template-columns: 1fr; }
  .reel-player { max-width: 280px; margin: 0 auto; }
  .header h1 { font-size: 1.8rem; }
}
"""

NAV_HTML = """
  <nav class="main-nav">
    <a href="{root}index.html">🏠 Home</a>
    <a href="{root}calendar-30day.html">📅 30-Day</a>
    <a href="{root}calendar-60day.html">📅 60-Day</a>
    <a href="{root}calendar-90day.html">📅 90-Day</a>
    <a href="{root}personal.html">💛 Personal</a>
    <a href="{curated_root}index.html"{curated_active}>🎬 Curated</a>
    <a href="{root}brand-guidelines.html">📋 Brand</a>
    <a href="{root}guides.html">📖 Guides</a>
    <div class="nav-dropdown">
      <a href="#" class="dropdown-toggle">📂 All Pages ▾</a>
      <div class="dropdown-menu">
        <div class="dropdown-group">
          <div class="dropdown-label">Curated</div>
          <a href="{curated_root}index.html">🎬 All Curated</a>
          <a href="{curated_root}holly-peete/index.html">⭐ Holly Robinson Peete</a>
          <a href="{curated_root}ot-genasis/index.html">⭐ OT Genasis</a>
          <a href="{curated_root}faith-evans/index.html">⭐ Faith Evans</a>
        </div>
        <div class="dropdown-group">
          <div class="dropdown-label">Calendars</div>
          <a href="{root}calendar-30day.html">📅 30-Day Calendar</a>
          <a href="{root}calendar-60day.html">📅 60-Day Calendar</a>
          <a href="{root}calendar-90day.html">📅 90-Day Calendar</a>
        </div>
        <div class="dropdown-group">
          <div class="dropdown-label">Brand & Guides</div>
          <a href="{root}brand-guidelines.html">📋 Brand Guidelines</a>
          <a href="{root}guides.html">📖 Guides</a>
        </div>
      </div>
    </div>
  </nav>
"""

COPY_SCRIPT = """
<script>
function copyText(btn) {
  const box = btn.closest('.caption-box');
  const text = box.querySelector('.caption-text').textContent.trim();
  navigator.clipboard.writeText(text).then(() => {
    const orig = btn.textContent;
    btn.textContent = '✓ Copied!';
    showToast('Caption copied');
    setTimeout(() => { btn.textContent = orig; }, 1500);
  });
}
function showToast(msg) {
  let t = document.querySelector('.toast');
  if (!t) { t = document.createElement('div'); t.className = 'toast'; document.body.appendChild(t); }
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 1800);
}
</script>
"""

# ---------------------------------------------------------------------------
# Artist data
# ---------------------------------------------------------------------------
ARTISTS = [
    {
        "slug": "holly-peete",
        "name_main": "Holly Robinson",
        "name_em":   "Peete",
        "name_full": "Holly Robinson Peete",
        "source":    "via OWN",
        "quote":     '"Do I have autism still?" — RJ Peete asks his mom on national TV. Her answer changed everything.',
        "reel_file": "FINAL-reel-v3.mp4",
        "reel_size": "~52 MB",
        "reel_len":  "119s",
        "reel_desc": "Cover slide → branded captioned clip with Spectrum Unlocked top bar and karaoke captions in the brand gold → ending CTA. Built with the v3 pipeline (forced-aligned word timing, native 1080×1920 throughout, seamless crossfade transitions).",
        "reel_status": "ready",
        "carousel": [
            {"file": "carousel-v2/slide-1-cover.png",  "kind": "image", "title": "Cover",        "desc": "Full-bleed photo + play cue (1080×1350)"},
            {"file": "carousel-v2/slide-2-video.mp4",  "kind": "video", "title": "Branded clip", "desc": "Karaoke captions + brand bar (119s)"},
            {"file": "carousel-v2/slide-3-quote.png",  "kind": "image", "title": "Quote card",   "desc": "Big Playfair Display pull quote"},
            {"file": "carousel-v2/slide-4-cta.png",    "kind": "image", "title": "CTA / Ending", "desc": "Save / Share / Follow + Tag prompt"},
        ],
        "reel_caption": '''"Do I have autism still?"
RJ Peete asked his mom Holly. Her answer changed everything.
#autismparent #hollyrobinsonpeete #autismacceptance #neurodivergent''',
        "feed_caption": '''"Do I have autism still?"

Holly Robinson Peete's son RJ asked her this question on national TV. Her answer broke the internet — and broke open a conversation millions of autism families needed.

Holly has been one of the most public, vocal autism parents in entertainment for over 20 years. Her son RJ is now an adult, and she's used every platform she's been given to advocate for autism acceptance.

She co-founded the HollyRod Foundation with her husband Rodney Peete to support families living with autism and Parkinson's disease.

This clip is a reminder: autism doesn't go away. But with love, understanding, and support, autistic kids grow into the brilliant adults they were always meant to be.

🎥 Holly Robinson Peete on OWN
💛 Follow @hollyrpeete + @hollyrodfdn

#AutismParent #HollyRobinsonPeete #RJPeete #HollyRodFoundation #AutismAcceptance #AutismAdvocacy #AutismFamily #AutismCommunity #NeurodivergentKids #AutismMom''',
        "badges": [
            ('<span class="meta gold">Reel ready</span>'),
            ('<span class="meta">Carousel ready</span>'),
        ],
    },
    {
        "slug": "ot-genasis",
        "name_main": "OT",
        "name_em":   "Genasis",
        "name_full": "OT Genasis",
        "source":    "via The Therapist (VICELAND)",
        "quote":     '"Maybe he chose you." — OT Genasis\'s most powerful moment about his autistic son.',
        "reel_file": "FINAL-reel-v3.mp4",
        "reel_size": "~28 MB",
        "reel_len":  "91s",
        "reel_desc": "Cover slide → branded captioned clip with Spectrum Unlocked top bar and karaoke captions in the brand gold → ending CTA. Built with the v3 pipeline (forced-aligned word timing, native 1080×1920 throughout, seamless crossfade transitions).",
        "reel_status": "ready",
        "carousel": [
            {"file": "carousel-v2/slide-1-cover.png",  "kind": "image", "title": "Cover",        "desc": "Full-bleed photo + play cue (1080×1350)"},
            {"file": "carousel-v2/slide-2-video.mp4",  "kind": "video", "title": "Branded clip", "desc": "Karaoke captions + brand bar (86s)"},
            {"file": "carousel-v2/slide-3-quote.png",  "kind": "image", "title": "Quote card",   "desc": "Big Playfair Display pull quote"},
            {"file": "carousel-v2/slide-4-cta.png",    "kind": "image", "title": "CTA / Ending", "desc": "Save / Share / Follow + Tag prompt"},
        ],
        "reel_caption": '''"Maybe he chose you."
OT Genasis's most powerful moment about his autistic son.
#autismparent #otgenasis #autismacceptance #blackfathers''',
        "feed_caption": '''"Maybe he chose you."

OT Genasis sat down on The Therapist (VICELAND) and opened up about raising his autistic son. What he said next changed how a lot of dads see this journey.

He talked about the early confusion. The grief. The questions. And then a thought that flipped everything: maybe his son didn't get autism. Maybe his son CHOSE him to be his dad.

That reframe — from "why me" to "why HIM" — is something a lot of autism dads carry quietly. OT Genasis just said it out loud.

If you're a dad navigating this, you're not alone. The fact that you're here, learning, showing up — that's the proof.

🎥 OT Genasis on The Therapist (VICELAND)
💛 You were chosen too.

#AutismDad #OTGenasis #AutismAcceptance #BlackFathers #AutismParent #AutismAdvocacy #FatherhoodJourney #NeurodivergentKids #AutismCommunity #AutismFamily''',
        "badges": [
            ('<span class="meta gold">Reel ready</span>'),
            ('<span class="meta">Carousel ready</span>'),
        ],
    },
    {
        "slug": "faith-evans",
        "name_main": "Faith",
        "name_em":   "Evans",
        "name_full": "Faith Evans",
        "source":    "via Tamron Hall Show",
        "quote":     '"I had to BEG for a diagnosis." — Faith Evans on fighting for her son Ryder\'s diagnosis and starting Ryder\'s Room.',
        "reel_file": "FINAL-reel-v3.mp4",
        "reel_size": "~60 MB",
        "reel_len":  "1:33",
        "reel_desc": "Best-of cut from Faith Evans\'s 7-minute Tamron Hall interview — 8 segments forming a complete narrative arc in under 2 minutes. Cover slide → branded captioned clip with Spectrum Unlocked top bar, karaoke captions, and left-biased blur-fit crop to keep Faith centered on both close-up and wide two-shot camera angles → ending CTA. Tamron reaction cutaway and audience B-roll were surgically removed.",
        "reel_status": "ready",
        "carousel": [
            {"file": "carousel-v2/slide-1-cover.png",  "kind": "image", "title": "Cover",        "desc": "Full-bleed photo + play cue (1080×1350)"},
            {"file": "carousel-v2/slide-2-video.mp4",  "kind": "video", "title": "Branded clip", "desc": "8-segment best-of with karaoke captions (88s)"},
            {"file": "carousel-v2/slide-3-quote.png",  "kind": "image", "title": "Quote card",   "desc": "Big Playfair Display pull quote"},
            {"file": "carousel-v2/slide-4-cta.png",    "kind": "image", "title": "CTA / Ending", "desc": "Save / Share / Follow + Tag prompt"},
        ],
        "reel_caption": '''Faith Evans had to BEG her doctor for her son's autism diagnosis.
She built Ryder's Room so no parent has to beg alone. 💛
#autismparent #autismdiagnosis #faithevans #autismacceptance #ryderroom''',
        "feed_caption": '''Faith Evans had to BEG her son's doctor for an autism diagnosis.

Her son Ryder was just under 3. She knew he should be talking. She knew something wasn't right. But the doctor kept telling her to wait — every child develops differently.

So she begged. And begged. Until finally she got the written diagnosis she needed to access services.

This is the part most people don't understand: in California (and many other states), you can't access early intervention, regional center supports, or therapy coverage WITHOUT a written diagnosis. Faith was paying for therapies out of pocket because the system wouldn't recognize her son until a doctor signed a piece of paper.

What changed everything? Another parent.

Not a doctor. Not a specialist. Another autism parent who said "I'll come with you. Go beg here. Do this. I know more than you know right now and I'll walk this with you."

That parent became Faith's first advocate. And today, Faith is paying it forward through Ryder's Room Inc. — her nonprofit built to make sure no autism parent has to beg alone.

If you're early in this journey: there are parents 6 months ahead of you who are willing to share what they've learned. Find them. They will save you months of confusion.

🎥 Faith on the Tamron Hall Show
💛 Follow @therealfaithevans + @ryders_room

#AutismParent #AutismDiagnosis #FaithEvans #RyderRoom #AutismAcceptance #BegForADiagnosis #AutismAdvocacy #NewlyDiagnosed #AutismCommunity #YouAreNotAlone''',
        "badges": [
            ('<span class="meta gold">Reel ready</span>'),
            ('<span class="meta">Carousel ready</span>'),
        ],
    },
    {
        "slug": "pete-wright",
        "name_main": "Pete",
        "name_em":   "Wright, Esq.",
        "name_full": "Pete Wright, Esq.",
        "source":    "via Wrightslaw.com",
        "quote":     '"Best is a four-letter word." — Pete Wright, founder of Wrightslaw.com, on the single word parents should never say in an IEP meeting.',
        "reel_file": "FINAL-reel-v3.mp4",
        "reel_size": "~18 MB",
        "reel_len":  "1:37",
        "reel_desc": "5-beat best-of cut from Pete Wright\'s 44-minute \"Top 10 IEP Mistakes\" interview with Dr. Roseann Capanna-Hodge. First reel in the roster from a non-celebrity expert — pure advocacy wisdom. Pete\'s personal origin (DC public schools wrote him off as \"retarded\" in kindergarten → his mom fought for a top-tier psychoeducational evaluation → she found Diana Hanbury King who taught him to read) → his signature IEP lesson (\"best\" is a four-letter word; it closes the door to quality services because by law your child is only entitled to FAPE, not to what is best) → the iconic hand-across-the-table moment where Pete trained parents to stop before they said the word \"best.\" This is the first artist with a 2-stage crop pipeline: source is a split-screen podcast (Dr. Roseann on left, Pete on right), so we pre-crop to just Pete\'s window (560x365 at x=680,y=155) before blur-fit to 1080x1920. Pete becomes the full-frame star, host\'s reactions are lost (acceptable for an expertise-focused reel). At 1:37, the longest reel in the roster — warranted by expertise-heavy content.",
        "reel_status": "ready",
        "carousel": [
            {"file": "carousel-v2/slide-1-cover.png",  "kind": "image", "title": "Cover",        "desc": "Pete against sunset + play cue (1080×1350)"},
            {"file": "carousel-v2/slide-2-video.mp4",  "kind": "video", "title": "Branded clip", "desc": "5-beat IEP advocacy lesson with karaoke (92s)"},
            {"file": "carousel-v2/slide-3-quote.png",  "kind": "image", "title": "Quote card",   "desc": "Big Playfair Display pull quote"},
            {"file": "carousel-v2/slide-4-cta.png",    "kind": "image", "title": "CTA / Ending", "desc": "Save / Share / Follow + Tag prompt"},
        ],
        "reel_caption": '''"Best is a four-letter word."
Pete Wright — the man who built Wrightslaw after DC public schools told his mom he was "retarded" in kindergarten — on the ONE word parents should never say at an IEP meeting. 💛
#IEP #Wrightslaw #specialeducation #autismparent #advocacy''',
        "feed_caption": '''"Best is a four-letter word."

Pete Wright, Esq. — the man who co-authored "Wrightslaw: Special Education Law" and trained a generation of parents how to advocate for their kids — has one rule he wants every IEP parent to follow:

Never say the word "best."

"When parents would come in to see me and they had an IEP meeting coming up, what I found so common with so many was that they wanted the school district to give the child a program that is best for their child. But if you say that at a meeting, you have now closed the door to your child getting quality services. Because by law, by case law, by statute, your child is not entitled to what is best. Your child is only entitled to a free, appropriate public education."

"When they would use the word best, I would stop them. I'd put my hand up, right? I'd reach my hand across the table right almost to their face. I wanted to create a visceral gut reaction to that word. I wanted it paired with somebody coming and putting their hand in their face. So that they stopped saying it before it even came out of their mouth — because they knew that was a four-letter word."

"Best is a four-letter word."

The most powerful part of Pete's story? He gets WHY the system writes kids off — because it wrote him off. DC public schools told his parents in kindergarten that he was "ineligible, male retarded, emotionally disturbed, and really not much could be done about it." His mom said forget about it. She got him a top-of-the-line psychoeducational evaluation from George Washington University, found Diana Hanbury King (an Orton-Gillingham specialist who was world famous), and by sixth grade Pete was testing two years above grade level in every domain.

"I am your adult dyslexic. That is the product of intense early intervention."

That's why Pete fights for other people's kids. And that's why every parent going into an IEP meeting should know his rule.

🎥 Pete Wright on "Top 10 IEP Mistakes" with Dr. Roseann Capanna-Hodge
📖 Wrightslaw.com — the canonical resource for special education law
🏛️ Pete argued the landmark Florence County School District v. Carter case in the US Supreme Court

#IEP #Wrightslaw #SpecialEducationLaw #IEPAdvocate #AutismParent #DyslexiaDad #ParentAdvocacy #FAPE #IDEA #SpecialEducation''',
        "badges": [
            ('<span class="meta gold">Reel ready</span>'),
            ('<span class="meta">Carousel ready</span>'),
        ],
    },
    {
        "slug": "rodney-peete",
        "name_main": "Rodney",
        "name_em":   "Peete",
        "name_full": "Rodney Peete",
        "source":    "via CBS Early Show",
        "quote":     '"I was stuck in denial." — Rodney Peete on his son RJ\'s autism diagnosis and the journey from denial to writing "Not My Boy!"',
        "reel_file": "FINAL-reel-v3.mp4",
        "reel_size": "~17 MB",
        "reel_len":  "1:04",
        "reel_desc": "7-beat best-of cut from Rodney Peete\'s 2010 CBS Early Show appearance with wife Holly Robinson Peete, promoting his book \"Not My Boy!\" The unfiltered DAD confession: the doctor\'s devastating prognosis → \"I was stuck in denial\" → he threw the books Holly gave him under the bed → his son\'s treatment embarrassed him into action → Holly\'s context (\"I went on the warpath and he retreated, we met in the middle\") → victory (doing things the doctor said he\'d never do). Uniform blur-fit crop preserves the 2-shot of Rodney and Holly on the Early Show couch. Note: SD source (640x480) upscaled.",
        "reel_status": "ready",
        "carousel": [
            {"file": "carousel-v2/slide-1-cover.png",  "kind": "image", "title": "Cover",        "desc": "Rodney solemn close-up + play cue (1080×1350)"},
            {"file": "carousel-v2/slide-2-video.mp4",  "kind": "video", "title": "Branded clip", "desc": "7-beat denial arc with karaoke captions (58s)"},
            {"file": "carousel-v2/slide-3-quote.png",  "kind": "image", "title": "Quote card",   "desc": "Big Playfair Display pull quote"},
            {"file": "carousel-v2/slide-4-cta.png",    "kind": "image", "title": "CTA / Ending", "desc": "Save / Share / Follow + Tag prompt"},
        ],
        "reel_caption": '''"I was stuck in denial."
Rodney Peete — former NFL QB and Holly Robinson Peete's husband — threw the autism books his wife gave him under the bed. Then his son's treatment embarrassed him into action. 💛
#autismdad #rodneypeete #notmyboy #autismacceptance #autismawareness''',
        "feed_caption": '''"I was stuck in denial for a period of time, I really was."

Rodney Peete — former NFL quarterback, husband to actress Holly Robinson Peete — on his son RJ's autism diagnosis.

The doctor told them RJ would never play sports. Would never be able to say "I love you" to his parents.

"I was stuck in being that father and that man who wanted to fix my son and really didn't pay attention to the signs, didn't pay attention to the education that I needed in order to communicate with him."

While Holly was rolling up her sleeves, reading every book, talking to families, talking to doctors, and sending them to Rodney — he was throwing them under the bed unread.

"It came to a point where I really had to almost get embarrassed by the treatment that was being given to him, and understand that I needed to put away all my expectations, come down to his level, and understand what autism is."

Holly puts it this way: "I went on the warpath and he sort of retreated. We were blessed to meet in the middle."

That reckoning became Rodney's book, "Not My Boy! A Father, a Son, and One Family's Journey with Autism."

Today? RJ is doing a lot of things that doctor said he would never ever do.

This is what the dad's journey through autism acceptance actually looks like — and why it's different from the mom's journey. Both are real. Both are needed.

🎥 Rodney & Holly Robinson Peete on CBS Early Show Saturday Edition, 2010
📖 "Not My Boy!" by Rodney Peete with Danelle Morton

#AutismDad #RodneyPeete #HollyRobinsonPeete #NotMyBoy #AutismAcceptance #AutismAwareness #AutismParenting #FathersJourney #AutismFamily #HollyRod''',
        "badges": [
            ('<span class="meta gold">Reel ready</span>'),
            ('<span class="meta">Carousel ready</span>'),
        ],
    },
    {
        "slug": "tisha-campbell",
        "name_main": "Tisha",
        "name_em":   "Campbell",
        "name_full": "Tisha Campbell",
        "source":    "via The Real",
        "quote":     '"This is a boy who couldn\'t talk." — Tisha Campbell on her son Xen, diagnosed at 23 months and now college-bound.',
        "reel_file": "FINAL-reel-v3.mp4",
        "reel_size": "~22 MB",
        "reel_len":  "1:21",
        "reel_desc": "6-beat best-of cut from Tisha Campbell\'s 2020 appearance on The Real, where she became emotional announcing that her autistic son Xen had been accepted to his top choice college. Diagnosis at 23 months → mission of independence → Xen chose mom\'s house over dad\'s because she was \"preparing him for college\" → dream of being a zoologist → 10-year-old brother Zeke adds \"mom, you\'re in my safe place.\" Uniform blur-fit crop preserves all shot compositions including the wide 5-person panel and the 2-shot cutaways to co-host Adrienne Bailon.",
        "reel_status": "ready",
        "carousel": [
            {"file": "carousel-v2/slide-1-cover.png",  "kind": "image", "title": "Cover",        "desc": "Tisha smiling + play cue (1080×1350)"},
            {"file": "carousel-v2/slide-2-video.mp4",  "kind": "video", "title": "Branded clip", "desc": "6-beat best-of with karaoke captions (77s)"},
            {"file": "carousel-v2/slide-3-quote.png",  "kind": "image", "title": "Quote card",   "desc": "Big Playfair Display pull quote"},
            {"file": "carousel-v2/slide-4-cta.png",    "kind": "image", "title": "CTA / Ending", "desc": "Save / Share / Follow + Tag prompt"},
        ],
        "reel_caption": '''"This is a boy who couldn't talk."
Tisha Campbell's son Xen was diagnosed with autism at 23 months. At 18, he got into his top choice college. He chose mom's house because she was preparing him. 💛
#autismmom #tishacampbell #autismawareness #autismparenting #raisethemstrong''',
        "feed_caption": '''"This is a boy who couldn't talk."

Tisha Campbell's son Xen was diagnosed with autism at 23 months old. On The Real, she broke down announcing that he had just been accepted to his top choice college — a school he'd talked about since he was eight. He wants to be a zoologist.

But the most powerful part wasn't the college acceptance. It was how he got there.

"Once I got the diagnosis," Tisha said, "I wanted him to be as independent of me as possible."

At 18, Xen chose to live at her house over his father's. When his 10-year-old brother Zeke asked him why, Xen said: "Because she's preparing me for my life. She's preparing me for college. Here, we don't have maids. I do everything on my own. I open the car door for mommy. She allows me to be more of a man at her house."

Then Zeke turned to Tisha and said, "Mom, you're in my safe place."

"What 10-year-old says that to somebody?" Tisha whispered.

People said Xen wasn't going to get into that school. He didn't wait for her. He didn't wait for his dad. He just did it. Straight-A student. Always on the Dean's list.

This is autism advocacy in its most powerful form: raising them to not need you. Loving them so hard they learn to stand on their own. Refusing to accept the limits the world tried to place on them.

🎥 Tisha Campbell on The Real, 2020
💛 Her memoir "The A Word: A Mother's Journey Through Autism and Love" is coming

#AutismMom #TishaCampbell #AutismParenting #XenMartin #AutismAwareness #IndependentAutism #RaiseThemStrong #AutismAdvocacy #AutismCommunity #AutismAcceptance''',
        "badges": [
            ('<span class="meta gold">Reel ready</span>'),
            ('<span class="meta">Carousel ready</span>'),
        ],
    },
    {
        "slug": "dan-orlovsky-madden",
        "name_main": "Dan & Madden",
        "name_em":   "Orlovsky",
        "name_full": "Dan & Madden Orlovsky",
        "source":    "via ESPN NFL Live",
        "quote":     '"Mom, I love you. Hunter, you\'re my favorite twin." — 14-year-old Madden Orlovsky speaking directly to his family on NFL Live for World Autism Awareness Day 2026.',
        "reel_file": "FINAL-reel-v3.mp4",
        "reel_size": "~20 MB",
        "reel_len":  "1:12",
        "reel_desc": "5-beat best-of cut from Dan Orlovsky\'s 12-minute NFL Live segment with his 14-year-old autistic son Madden. Context → art wall → couch interview → THE QUOTE + Dan\'s on-air breakdown → aftermath smile. Uniform blur-fit crop preserves the ESPN split-screen layout so Dan\'s tearful reaction shot survives intact — the emotional peak would have been destroyed by a standard center crop.",
        "reel_status": "ready",
        "carousel": [
            {"file": "carousel-v2/slide-1-cover.png",  "kind": "image", "title": "Cover",        "desc": "Madden on couch + play cue (1080×1350)"},
            {"file": "carousel-v2/slide-2-video.mp4",  "kind": "video", "title": "Branded clip", "desc": "5-beat best-of with karaoke captions (67s)"},
            {"file": "carousel-v2/slide-3-quote.png",  "kind": "image", "title": "Quote card",   "desc": "Big Playfair Display pull quote"},
            {"file": "carousel-v2/slide-4-cta.png",    "kind": "image", "title": "CTA / Ending", "desc": "Save / Share / Follow + Tag prompt"},
        ],
        "reel_caption": '''"Mom, I love you."
14-year-old Madden Orlovsky spoke directly to his family on NFL Live for World Autism Day. His dad Dan couldn't hold it together. Neither could anyone watching. 💛
#autismparent #danorlovsky #worldautismday #autismdad #nfl''',
        "feed_caption": '''"Mom, I love you. Hunter, you're my favorite twin. Noah, I do like you. And Lennon, you're a good sister."

That's what 14-year-old Madden Orlovsky said directly into the camera on ESPN's NFL Live this April 2nd — World Autism Awareness Day — sitting next to his father Dan, the former Detroit Lions QB and current ESPN analyst.

Madden is one of identical triplets, autistic, a die-hard Philadelphia Eagles fan, and — according to himself — someone with "great artwork, great coloring, great handwriting." His drawings decorated the NFL Live studio all morning.

When Dan asked his son if he could tell the camera something he loves, Madden didn't hesitate. He named every person in his family. His dad broke down on air. The entire NFL Live set joined him. Magic Johnson reposted it. Ric Flair reposted it. Pat McAfee had Dan on the next day to talk about it.

This is what autism parenting looks like when the world finally gets to see it: a kid with his own voice, his own art, his own love language, telling everyone he cares about exactly how much they matter.

Autism isn't silent. We just haven't been listening.

🎥 Dan & Madden Orlovsky on ESPN's NFL Live
💛 World Autism Awareness Day 2026

#AutismDad #DanOrlovsky #MaddenOrlovsky #AutismAwareness #NFL #AutismParent #AutismFamily #WorldAutismDay #AutismAcceptance #Neurodivergent''',
        "badges": [
            ('<span class="meta gold">Reel ready</span>'),
            ('<span class="meta">Carousel ready</span>'),
        ],
    },
]

# ---------------------------------------------------------------------------
# Build per-artist page
# ---------------------------------------------------------------------------
def build_artist(a):
    nav = NAV_HTML.format(
        root="../../../",
        curated_root="../",
        curated_active=' class="active"',
    )

    # Reel section
    if a["reel_status"] == "legacy":
        reel_notice = '''
        <div class="notice-box">
          <strong>⚠ Legacy reel</strong>
          This is the original reel from before the v3 pipeline. The v3 rebuild
          (forced-aligned karaoke captions, per-clip brand overlays, multi-clip
          structure) is pending. Use this version for now.
        </div>'''
    else:
        reel_notice = ""

    # Build carousel slides HTML
    slides_html = []
    total = len(a["carousel"])
    for i, slide in enumerate(a["carousel"], start=1):
        if slide["kind"] == "image":
            thumb = f'<img src="{slide["file"]}" alt="{slide["title"]}">'
        else:
            thumb = f'<video src="{slide["file"]}" muted preload="metadata"></video><div class="play-overlay"></div>'
        ext = slide["file"].rsplit(".", 1)[-1].upper()
        slides_html.append(f'''
        <div class="slide">
          <div class="slide-thumb">{thumb}</div>
          <div class="slide-body">
            <div class="slide-num">SLIDE {i} / {total}</div>
            <div class="slide-title">{slide["title"]}</div>
            <div class="slide-desc">{slide["desc"]}</div>
            <div class="slide-dl"><a href="{slide["file"]}" download>⬇ {ext}</a></div>
          </div>
        </div>''')

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{a["name_full"]} — Curated — Spectrum Unlocked</title>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800;900&family=Playfair+Display:wght@700;900&display=swap" rel="stylesheet">
  <style>{CSS}</style>
</head>
<body>
{nav}
  <div class="header">
    <div class="source-tag">{a["source"]}</div>
    <h1>{a["name_main"]} <span class="em">{a["name_em"]}</span></h1>
    <p>{a["quote"]}</p>
  </div>

  <div class="container">

    <div class="section-card">
      <div class="section-header">
        <div class="section-num">1</div>
        <div class="section-info">
          <h3>REEL</h3>
          <div class="sub">Vertical 1080×1920 — single Instagram Reel</div>
        </div>
      </div>
      <div class="section-content">
        {reel_notice}
        <div class="reel-grid">
          <div class="reel-player">
            <video controls preload="metadata">
              <source src="{a["reel_file"]}" type="video/mp4">
            </video>
          </div>
          <div class="reel-info">
            <p>{a["reel_desc"]}</p>
            <div class="meta-row">
              <span class="meta gold">1080×1920</span>
              <span class="meta">{a["reel_len"]}</span>
              <span class="meta">H.264 high</span>
              <span class="meta">{a["reel_size"]}</span>
            </div>
            <a href="{a["reel_file"]}" download class="btn">⬇ Download Reel (.mp4)</a>
          </div>
        </div>
      </div>
    </div>

    <div class="section-card">
      <div class="section-header">
        <div class="section-num">2</div>
        <div class="section-info">
          <h3>CAROUSEL</h3>
          <div class="sub">{total}-slide Instagram carousel — 1080×1350</div>
        </div>
      </div>
      <div class="section-content">
        <div class="carousel-grid">
{"".join(slides_html)}
        </div>
      </div>
    </div>

    <div class="section-card">
      <div class="section-header">
        <div class="section-num">3</div>
        <div class="section-info">
          <h3>CAPTIONS</h3>
          <div class="sub">Reel + carousel feed copy</div>
        </div>
      </div>
      <div class="section-content">

        <div class="caption-box">
          <span class="label">🎬 REEL CAPTION</span>
          <button class="copy-btn" onclick="copyText(this)">📋 Copy</button>
          <div class="caption-text">{a["reel_caption"]}</div>
        </div>

        <div class="caption-box">
          <span class="label">📱 FEED CAPTION (CAROUSEL)</span>
          <button class="copy-btn" onclick="copyText(this)">📋 Copy</button>
          <div class="caption-text">{a["feed_caption"]}</div>
        </div>

      </div>
    </div>

  </div>

{COPY_SCRIPT}
</body>
</html>
"""

# ---------------------------------------------------------------------------
# Build hub page
# ---------------------------------------------------------------------------
def build_hub():
    nav = NAV_HTML.format(
        root="../../",
        curated_root="",
        curated_active=' class="active"',
    )
    cards = []
    for a in ARTISTS:
        badges = "".join(a["badges"])
        cards.append(f'''
      <a href="{a["slug"]}/index.html" class="artist-card">
        <div class="artist-photo" style="background-image:url('{a["slug"]}/cover-photo.png')"></div>
        <div class="artist-body">
          <div class="artist-source">{a["source"]}</div>
          <div class="artist-name">{a["name_full"]}</div>
          <div class="artist-quote">{a["quote"]}</div>
          <div class="artist-badges">{badges}</div>
        </div>
      </a>''')

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Curated — Spectrum Unlocked</title>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800;900&family=Playfair+Display:wght@700;900&display=swap" rel="stylesheet">
  <style>{CSS}</style>
</head>
<body>
{nav}
  <div class="header">
    <div class="source-tag">SPECTRUM UNLOCKED</div>
    <h1>Curated <span class="em">voices.</span></h1>
    <p>Real moments from real autism parents — curated, branded, and ready to ship as Reels and carousels. Click an artist to view their full package.</p>
  </div>

  <div class="container">
    <div class="artist-grid">
{"".join(cards)}
    </div>
  </div>
</body>
</html>
"""

# ---------------------------------------------------------------------------
# Write all
# ---------------------------------------------------------------------------
hub = BASE / "index.html"
hub.write_text(build_hub(), encoding="utf-8")
print(f"wrote {hub}")

for a in ARTISTS:
    p = BASE / a["slug"] / "index.html"
    p.write_text(build_artist(a), encoding="utf-8")
    print(f"wrote {p}")
