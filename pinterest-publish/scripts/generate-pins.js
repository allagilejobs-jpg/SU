#!/usr/bin/env node
// Pinterest pin generator (batch 2 - pins 26-65 redesign)
// Reads pins.json, emits HTML files into content/pinterest/, then renders PNGs via Playwright.

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const ROOT = path.resolve(__dirname, '../..');
const OUT_DIR = path.join(ROOT, 'content/pinterest');
const CONFIG_PATH = path.join(__dirname, 'pins.json');
const CSV_PATH = path.join(ROOT, 'pinterest-publish/bulk-upload-batch2.csv');
const SITE_BASE = 'https://www.spectrumunlocked.com';
const IMAGE_BASE = 'https://allagilejobs-jpg.github.io/SU/content/pinterest';

const BOARDS = {
  'Autism Diagnosis & Getting Started': /diagnosis|first-48|grief|diagnosed-now|first-week|newly|tiktok-myths|world-autism-day/i,
  'IEP Tips & School Advocacy': /iep|504|school|accommodations|teacher|advocacy|legal|rights|first-iep/i,
  'Sensory Activities & Regulation': /sensory|nature|calm|regulation|meltdown(?!-tantrum)/i,
  'Visual Schedules & Daily Routines': /visual|schedule|routine|aac|communication|gestalt-language|early-intervention/i,
  'Autism Resources for Parents': /apps|toolkit|resources|aac-beginners|therap|workplace|sleep|picky|feeding|waitlist|burnout|self-care|finding-village|encouragement|public-meltdown/i,
  'Autism Parenting Real Talk': /marriage|sibling|joy|emotions|functioning|grief|what-to-say|explain-family|acceptance|autistic-joy|tantrum/i,
};

function boardFor(file) {
  for (const [board, re] of Object.entries(BOARDS)) {
    if (re.test(file)) return board;
  }
  return 'Autism Resources for Parents'; // fallback
}

function fullTitle(p) {
  if (p.csvTitle) return p.csvTitle;
  if (p.template === 'C') {
    // Use the "pre" line as title (it's the headline framing the stat).
    // Strip trailing punctuation and any leading "The".
    const base = (p.pre || '').replace(/[:.?!]$/, '').replace(/^The\s+/i, '').trim();
    return base.charAt(0).toUpperCase() + base.slice(1);
  }
  const parts = [p.titlePre, p.titleHighlight, p.titlePost].filter(Boolean);
  return parts.join(' ').replace(/\s+/g, ' ').trim();
}

function csvField(s) {
  if (s == null) return '';
  const v = String(s).replace(/"/g, '""');
  return /[",\n]/.test(v) ? `"${v}"` : v;
}

function endPunct(s) {
  if (!s) return '';
  return /[.!?]$/.test(s.trim()) ? s.trim() : s.trim() + '.';
}

function buildDescription(p) {
  // Pinterest descriptions: 250-500 char sweet spot. Lead with subtitle/headline, then payoff.
  if (p.template === 'A') {
    const items = (p.rows || []).slice(0, 3).map(r => r.title).join(', ');
    const tipPart = p.tip ? ` ${endPunct(p.tip.title)}` : '';
    return `${endPunct(p.subtitle)} Inside: ${items}.${tipPart} Save & share.`.trim();
  }
  if (p.template === 'B') {
    const items = (p.truthItems || []).map(t => t.label).join(', ');
    return `${endPunct(p.mythSub)} ${endPunct(p.truthHeadline)} Inside: ${items}. Save & share to bust this myth.`.trim();
  }
  if (p.template === 'C') {
    const items = (p.actions || []).slice(0, 3).map(a => a.title).join(', ');
    const tipPart = p.tip ? ` ${endPunct(p.tip.title)}` : '';
    return `${p.statValue} ${p.statUnit} — ${endPunct(p.statLabel)} What to do now: ${items}.${tipPart}`.trim();
  }
  return p.subtitle || '';
}

function destLink(p) {
  // Match existing batch-1 dedup pattern: UTM-tagged homepage links per pin slug.
  // Pinterest rejects duplicate destination URLs, so each pin gets a unique campaign tag.
  const slug = p.file.replace(/^pin-\d+-/, '').replace(/^blog-/, '');
  return `${SITE_BASE}/?utm_source=pinterest&utm_campaign=${slug}`;
}

const config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf-8'));

// ---------- Template A: Bold List ----------
function templateA(p) {
  const rows = (p.rows || []).map((r, i) => `
    <div class="row">
      <div class="num">${i + 1}</div>
      <div class="row-text">${r.title}
        <small>${r.sub}</small>
      </div>
    </div>`).join('');
  const tip = p.tip ? `
    <div class="tip-card">
      <div class="tip-emoji">${p.tip.icon || '!'}</div>
      <div class="tip-text">${p.tip.title}
        <small>${p.tip.sub}</small>
      </div>
    </div>` : '';
  return `<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800;900&family=Caveat:wght@600&display=swap" rel="stylesheet">
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { width:1000px; height:1500px; font-family:'Poppins',sans-serif; background:#FFF4E8; color:#2a004a; display:flex; flex-direction:column; position:relative; overflow:hidden; }
.blob { position:absolute; width:320px; height:320px; border-radius:50%; background:#FDB03E; top:-120px; right:-120px; opacity:0.55; }
.blob.b2 { width:220px; height:220px; background:#18A8F1; top:auto; bottom:380px; right:-80px; opacity:0.18; }
.hero { background:#CC78CB; color:white; padding:70px 60px 60px; position:relative; z-index:2; }
.kicker { display:inline-block; background:#FDB03E; color:#2a004a; padding:10px 22px; border-radius:999px; font-size:18px; font-weight:800; text-transform:uppercase; letter-spacing:2px; margin-bottom:28px; }
.title { font-size:96px; font-weight:900; line-height:0.98; letter-spacing:-2px; margin-bottom:18px; }
.title em { font-style:normal; background:#18A8F1; color:white; padding:0 14px; display:inline-block; transform:rotate(-1.5deg); box-decoration-break:clone; }
.subtitle { font-size:26px; font-weight:500; opacity:0.95; max-width:600px; line-height:1.3; }
.content { flex:1; padding:50px 60px 30px; display:flex; flex-direction:column; gap:18px; position:relative; z-index:2; }
.row { display:flex; align-items:center; gap:24px; background:white; border-radius:22px; padding:24px 30px; box-shadow:0 6px 0 rgba(82,0,140,0.12); }
.num { flex-shrink:0; width:74px; height:74px; border-radius:50%; background:#18A8F1; color:white; font-size:42px; font-weight:900; display:flex; align-items:center; justify-content:center; line-height:1; }
.row:nth-child(2) .num { background:#CC78CB; }
.row:nth-child(3) .num { background:#FDB03E; color:#2a004a; }
.row:nth-child(4) .num { background:#52008C; }
.row:nth-child(5) .num { background:#18A8F1; }
.row-text { font-size:25px; font-weight:700; line-height:1.25; color:#2a004a; }
.row-text small { display:block; font-size:18px; font-weight:500; color:#6b5a7a; margin-top:4px; }
.tip-card { margin:8px 0 0; background:#2a004a; color:white; border-radius:22px; padding:26px 30px; display:flex; align-items:center; gap:22px; border:4px solid #FDB03E; }
.tip-card .tip-emoji { flex-shrink:0; width:64px; height:64px; border-radius:50%; background:#FDB03E; color:#2a004a; font-size:32px; font-weight:900; display:flex; align-items:center; justify-content:center; transform:rotate(-6deg); }
.tip-card .tip-text { font-size:21px; font-weight:700; line-height:1.3; }
.tip-card .tip-text small { display:block; font-size:16px; font-weight:500; opacity:0.85; margin-top:4px; }
.save-band { background:#2a004a; color:white; padding:26px 60px; display:flex; align-items:center; justify-content:space-between; position:relative; z-index:2; }
.save-cta { font-size:22px; font-weight:800; }
.save-cta .pin-emoji { display:inline-block; background:#CC78CB; width:36px; height:36px; border-radius:50%; text-align:center; line-height:36px; margin-right:10px; font-size:18px; }
.brand { font-family:'Caveat',cursive; font-size:30px; color:#FDB03E; font-weight:700; }
</style></head>
<body>
<div class="blob"></div><div class="blob b2"></div>
<div class="hero">
  <span class="kicker">${p.kicker}</span>
  <h1 class="title">${p.titlePre} <em>${p.titleHighlight}</em>${p.titlePost ? '<br>' + p.titlePost : ''}</h1>
  <p class="subtitle">${p.subtitle}</p>
</div>
<div class="content">${rows}${tip}</div>
<div class="save-band">
  <div class="save-cta"><span class="pin-emoji">📌</span>${p.saveCta}</div>
  <div class="brand">spectrumunlocked.com</div>
</div>
</body></html>`;
}

// ---------- Template B: Comparison ----------
function templateB(p) {
  const truthItems = (p.truthItems || []).map(t => `
    <div class="truth-item">
      <div class="ico">${t.icon}</div>
      <div class="lbl">${t.label}<small>${t.sub}</small></div>
    </div>`).join('');
  const quote = p.quote ? `
    <div class="truth-quote">"${p.quote.text}"
      <span class="who">— ${p.quote.who}</span>
    </div>` : '';
  return `<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800;900&family=Caveat:wght@600&display=swap" rel="stylesheet">
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { width:1000px; height:1500px; font-family:'Poppins',sans-serif; background:#FFF4E8; display:flex; flex-direction:column; position:relative; overflow:hidden; }
.title-strip { background:#18A8F1; color:white; padding:54px 60px 60px; text-align:center; position:relative; }
.kicker { display:inline-block; background:#FDB03E; color:#2a004a; padding:8px 22px; border-radius:999px; font-size:16px; font-weight:800; text-transform:uppercase; letter-spacing:2px; margin-bottom:18px; }
.title { font-size:84px; font-weight:900; line-height:0.96; letter-spacing:-2px; }
.title .feel { background:#CC78CB; padding:0 16px; display:inline-block; transform:rotate(-2deg); }
.compare { flex:1; display:flex; flex-direction:column; }
.block { padding:44px 60px; position:relative; }
.block.myth { background:#FFE4E1; border-bottom:6px dashed #CC78CB; }
.block.truth { background:#CC78CB; color:white; flex:1; }
.block-label { display:inline-block; font-size:22px; font-weight:900; text-transform:uppercase; letter-spacing:3px; padding:8px 20px; border-radius:8px; margin-bottom:22px; }
.myth .block-label { background:#2a004a; color:white; }
.truth .block-label { background:#FDB03E; color:#2a004a; }
.block-text { font-size:42px; font-weight:800; line-height:1.1; letter-spacing:-1px; }
.myth .block-text { color:#6b5a7a; text-decoration:line-through; text-decoration-color:#CC78CB; text-decoration-thickness:4px; }
.block-sub { font-size:22px; font-weight:500; line-height:1.35; margin-top:22px; }
.myth .block-sub { color:#2a004a; opacity:0.8; }
.vs-stamp { position:absolute; left:50%; transform:translateX(-50%) rotate(-8deg); bottom:-42px; width:86px; height:86px; border-radius:50%; background:#FDB03E; color:#2a004a; font-size:26px; font-weight:900; display:flex; align-items:center; justify-content:center; z-index:3; box-shadow:0 6px 0 rgba(82,0,140,0.4); border:4px solid white; }
.truth-list { display:flex; flex-direction:column; gap:12px; margin-top:26px; }
.truth-item { display:flex; align-items:center; gap:16px; background:rgba(255,255,255,0.18); border-radius:14px; padding:14px 18px; }
.truth-item .ico { flex-shrink:0; width:40px; height:40px; border-radius:10px; background:#FDB03E; color:#2a004a; font-size:20px; font-weight:900; display:flex; align-items:center; justify-content:center; transform:rotate(-4deg); }
.truth-item .lbl { font-size:19px; font-weight:700; line-height:1.25; }
.truth-item .lbl small { display:block; font-size:14px; font-weight:500; opacity:0.85; margin-top:2px; }
.truth-quote { margin-top:24px; background:#2a004a; color:white; border-radius:18px; padding:22px 26px; font-size:21px; font-weight:700; line-height:1.3; border-left:8px solid #FDB03E; font-style:italic; }
.truth-quote .who { display:block; font-style:normal; font-size:15px; font-weight:500; opacity:0.8; margin-top:8px; }
.save-band { background:#2a004a; color:white; padding:24px 60px; display:flex; align-items:center; justify-content:space-between; }
.save-cta { font-size:22px; font-weight:800; }
.save-cta .pin-emoji { display:inline-block; background:#CC78CB; width:36px; height:36px; border-radius:50%; text-align:center; line-height:36px; margin-right:10px; font-size:18px; }
.brand { font-family:'Caveat',cursive; font-size:30px; color:#FDB03E; font-weight:700; }
</style></head>
<body>
<div class="title-strip">
  <span class="kicker">${p.kicker}</span>
  <h1 class="title">${p.titlePre} <span class="feel">${p.titleHighlight}</span>${p.titlePost ? '<br>' + p.titlePost : ''}</h1>
</div>
<div class="compare">
  <div class="block myth">
    <span class="block-label">✕ ${p.mythLabel || 'The Myth'}</span>
    <div class="block-text">"${p.mythText}"</div>
    <div class="block-sub">${p.mythSub}</div>
    <div class="vs-stamp">VS</div>
  </div>
  <div class="block truth">
    <span class="block-label">✓ ${p.truthLabel || 'The Truth'}</span>
    <div class="block-text">${p.truthHeadline}</div>
    <div class="truth-list">${truthItems}</div>
    ${quote}
  </div>
</div>
<div class="save-band">
  <div class="save-cta"><span class="pin-emoji">📌</span>${p.saveCta}</div>
  <div class="brand">spectrumunlocked.com</div>
</div>
</body></html>`;
}

// ---------- Template C: Stat Hero ----------
function templateC(p) {
  const actions = (p.actions || []).map((a, i) => `
    <div class="action">
      <div class="action-bullet">${i + 1}</div>
      <div class="action-text">${a.title}
        <small>${a.sub}</small>
      </div>
    </div>`).join('');
  const tip = p.tip ? `
    <div class="tip-band">
      <div class="tip-icon">${p.tip.icon || '💡'}</div>
      <div class="tip-text">${p.tip.title}
        <small>${p.tip.sub}</small>
      </div>
    </div>` : '';
  return `<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800;900&family=Caveat:wght@600&display=swap" rel="stylesheet">
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { width:1000px; height:1500px; font-family:'Poppins',sans-serif; background:#CC78CB; color:white; display:flex; flex-direction:column; position:relative; overflow:hidden; }
.dots { position:absolute; top:0; left:0; right:0; bottom:0; background-image:radial-gradient(circle, rgba(255,255,255,0.18) 2px, transparent 2px); background-size:36px 36px; pointer-events:none; opacity:0.45; }
.top { padding:60px 60px 30px; position:relative; z-index:2; text-align:center; }
.kicker { display:inline-block; background:#FDB03E; color:#2a004a; padding:10px 22px; border-radius:999px; font-size:18px; font-weight:800; text-transform:uppercase; letter-spacing:2px; margin-bottom:24px; }
.pre { font-size:28px; font-weight:700; letter-spacing:1px; margin-bottom:8px; opacity:0.95; }
.stat-wrap { background:white; color:#2a004a; margin:14px 60px 0; border-radius:28px; padding:46px 30px 32px; text-align:center; position:relative; z-index:2; box-shadow:0 12px 0 rgba(82,0,140,0.4); }
.stat { font-size:${p.statSize || 220}px; font-weight:900; line-height:0.85; letter-spacing:-8px; background:linear-gradient(180deg,#18A8F1 0%,#52008C 100%); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }
.stat-unit { font-size:38px; font-weight:800; color:#CC78CB; letter-spacing:1px; margin-top:-4px; }
.stat-label { font-size:24px; font-weight:600; color:#2a004a; margin-top:16px; line-height:1.25; }
.actions { padding:32px 60px 8px; display:flex; flex-direction:column; gap:14px; position:relative; z-index:2; }
.actions-title { font-size:30px; font-weight:900; letter-spacing:1px; text-align:center; margin-bottom:4px; }
.action { display:flex; align-items:center; gap:18px; background:rgba(255,255,255,0.95); color:#2a004a; border-radius:18px; padding:18px 24px; }
.action-bullet { flex-shrink:0; width:50px; height:50px; border-radius:12px; background:#FDB03E; color:#2a004a; font-weight:900; font-size:26px; display:flex; align-items:center; justify-content:center; transform:rotate(-4deg); }
.action:nth-child(3) .action-bullet { background:#18A8F1; color:white; transform:rotate(3deg); }
.action:nth-child(4) .action-bullet { background:#52008C; color:white; transform:rotate(-2deg); }
.action:nth-child(5) .action-bullet { background:#CC78CB; color:white; transform:rotate(4deg); }
.action-text { font-size:21px; font-weight:700; line-height:1.25; }
.action-text small { display:block; font-size:15px; font-weight:500; color:#6b5a7a; margin-top:2px; }
.tip-band { margin:14px 60px 24px; background:#2a004a; border-radius:22px; padding:22px 26px; display:flex; align-items:center; gap:20px; border:4px solid #FDB03E; position:relative; z-index:2; }
.tip-band .tip-icon { flex-shrink:0; width:60px; height:60px; border-radius:50%; background:#FDB03E; color:#2a004a; font-size:28px; font-weight:900; display:flex; align-items:center; justify-content:center; transform:rotate(-5deg); }
.tip-band .tip-text { color:white; font-size:20px; font-weight:700; line-height:1.3; }
.tip-band .tip-text small { display:block; font-size:15px; font-weight:500; opacity:0.85; margin-top:3px; }
.spacer { flex:1; }
.save-band { background:#2a004a; color:white; padding:24px 60px; display:flex; align-items:center; justify-content:space-between; position:relative; z-index:2; }
.save-cta { font-size:22px; font-weight:800; }
.save-cta .pin-emoji { display:inline-block; background:#CC78CB; width:36px; height:36px; border-radius:50%; text-align:center; line-height:36px; margin-right:10px; font-size:18px; }
.brand { font-family:'Caveat',cursive; font-size:30px; color:#FDB03E; font-weight:700; }
</style></head>
<body>
<div class="dots"></div>
<div class="top">
  <span class="kicker">${p.kicker}</span>
  <div class="pre">${p.pre}</div>
</div>
<div class="stat-wrap">
  <div class="stat">${p.statValue}</div>
  <div class="stat-unit">${p.statUnit}</div>
  <div class="stat-label">${p.statLabel}</div>
</div>
<div class="actions">
  <div class="actions-title">${p.actionsTitle}</div>
  ${actions}
</div>
${tip}
<div class="spacer"></div>
<div class="save-band">
  <div class="save-cta"><span class="pin-emoji">📌</span>${p.saveCta}</div>
  <div class="brand">spectrumunlocked.com</div>
</div>
</body></html>`;
}

const templates = { A: templateA, B: templateB, C: templateC };

// Generate HTML files
let count = 0;
for (const pin of config.pins) {
  const fn = templates[pin.template];
  if (!fn) {
    console.error(`Unknown template "${pin.template}" for ${pin.file}`);
    continue;
  }
  const html = fn(pin);
  const outPath = path.join(OUT_DIR, pin.file + '.html');
  fs.writeFileSync(outPath, html);
  console.log(`✓ HTML: ${pin.file}.html (${pin.template})`);
  count++;
}
console.log(`\nGenerated ${count} HTML files. Now rendering PNGs...\n`);

// Render PNGs in series
let rendered = 0;
for (const pin of config.pins) {
  const htmlPath = path.join(OUT_DIR, pin.file + '.html');
  const pngPath = path.join(OUT_DIR, pin.file + '.png');
  try {
    execSync(`npx playwright screenshot --viewport-size=1000,1500 "${htmlPath}" "${pngPath}"`, {
      stdio: 'pipe',
      cwd: ROOT,
    });
    rendered++;
    console.log(`✓ PNG (${rendered}/${count}): ${pin.file}.png`);
  } catch (e) {
    console.error(`✗ Render failed for ${pin.file}: ${e.message}`);
  }
}
console.log(`\nDone. ${rendered}/${count} PNGs rendered.`);

// ---------- Build CSV ----------
const csvHeader = 'Title,Media URL,Pinterest board,Thumbnail,Description,Link,Publish date,Keywords';
const csvLines = [csvHeader];
for (const pin of config.pins) {
  const row = [
    fullTitle(pin),
    `${IMAGE_BASE}/${pin.file}.png`,
    boardFor(pin.file),
    '',
    buildDescription(pin),
    destLink(pin),
    '',
    '',
  ].map(csvField).join(',');
  csvLines.push(row);
}
fs.writeFileSync(CSV_PATH, csvLines.join('\n') + '\n');
console.log(`\n✓ CSV: ${CSV_PATH} (${config.pins.length} rows)`);

// ---------- Update PINTEREST-POSTS.md ----------
const POSTS_MD = path.join(OUT_DIR, 'PINTEREST-POSTS.md');
const existing = fs.readFileSync(POSTS_MD, 'utf-8');
// Drop everything from "## Quick Reference" onward, then rebuild for full set.
const head = existing.split('\n## Quick Reference')[0];
const lines = [head.trimEnd(), '', '---', ''];

for (const pin of config.pins) {
  const num = parseInt(pin.file.match(/^pin-(\d+)/)[1], 10);
  if (num <= 25) continue; // only document the new batch
  lines.push(`## ${num}. ${fullTitle(pin)}`);
  lines.push(`**File:** \`${pin.file}.png\` · **Template:** ${pin.template} · **Board:** ${boardFor(pin.file)}`);
  lines.push('');
  lines.push(`**Description:** ${buildDescription(pin)}`);
  lines.push('');
  lines.push(`**Link:** \`${destLink(pin)}\``);
  lines.push('');
  lines.push('---');
  lines.push('');
}

lines.push('## Quick Reference - Batch 2 (pins 26-65)');
lines.push('');
lines.push('| # | Title | Template | Board |');
lines.push('|---|-------|----------|-------|');
for (const pin of config.pins) {
  const num = parseInt(pin.file.match(/^pin-(\d+)/)[1], 10);
  if (num <= 25) continue;
  lines.push(`| ${num} | ${fullTitle(pin)} | ${pin.template} | ${boardFor(pin.file)} |`);
}
lines.push('');
lines.push(`*Batch 2 generated: ${new Date().toISOString().slice(0,10)}*`);
lines.push(`*Total: ${config.pins.length} Pinterest-ready graphics at 1000×1500*`);
lines.push('');

fs.writeFileSync(POSTS_MD, lines.join('\n'));
console.log(`✓ Docs: ${POSTS_MD}`);
