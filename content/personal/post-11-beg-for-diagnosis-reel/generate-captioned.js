const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const DIR = __dirname;
const VIDEO = '/tmp/insta_post.mp4';

// Captions with timestamps [start, end, text]
const captions = [
  [0, 4.5, "What was it like for you,\nfor those who may be experiencing that now,"],
  [4.5, 7.5, "discovering that your child\nwas autistic?"],
  [7.5, 13.5, "By the time he was diagnosed,\nI was already aware something was wrong."],
  [13.5, 21, "So it was me begging for a written\ndiagnosis to access early intervention."],
  [21, 24.5, "I had to beg for a written diagnosis."],
  [24.5, 31.5, "Because by the time he was two,\nI'm like, my son should be talking."],
  [31.5, 35, "I had three other kids before him."],
  [35, 41.5, "And his doctor was like,\njust wait it out. Every kid is different."],
  [41.5, 45, "But I still felt\nsomething wasn't right."],
  [45, 53.5, "So I started on my own putting him\nin speech therapy."],
  [53.5, 60.5, "Speech therapy,\noccupational therapy."],
  [60.5, 66.8, "And to access early intervention,\nI needed a diagnosis before he was three."]
];

// Brand + headline overlay HTML
const brandOverlayHTML = `<!DOCTYPE html>
<html>
<head>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600;700;800;900&display=swap" rel="stylesheet">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { width: 720px; height: 900px; background: #00ff00; font-family: 'Poppins', sans-serif; }
.brand { position: absolute; top: 30px; left: 30px; }
.brand-main { font-size: 22px; font-weight: 900; color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.8); }
.brand-sub { font-size: 16px; font-weight: 700; color: #4A90A4; text-shadow: 2px 2px 4px rgba(0,0,0,0.8); background: rgba(0,0,0,0.3); padding: 2px 6px; display: inline-block; }
.headline-box { position: absolute; top: 260px; left: 50%; transform: translateX(-50%); background: rgba(255,255,255,0.95); padding: 15px 25px; border-radius: 6px; max-width: 650px; text-align: center; }
.headline { font-size: 22px; font-weight: 800; color: #1a1a2e; line-height: 1.3; }
.arrow { position: absolute; bottom: 30px; right: 30px; width: 60px; height: 30px; border: 2px solid rgba(255,255,255,0.6); border-radius: 15px; display: flex; align-items: center; justify-content: center; }
.arrow::after { content: '→'; color: rgba(255,255,255,0.6); font-size: 18px; }
</style>
</head>
<body>
<div class="brand"><div class="brand-main">SPECTRUM</div><div class="brand-sub">UNLOCKED</div></div>
<div class="headline-box"><div class="headline">Parent Opens Up About Having to<br>BEG for an Autism Diagnosis</div></div>
<div class="arrow"></div>
</body>
</html>`;

// Caption overlay HTML generator
function captionHTML(text) {
  return `<!DOCTYPE html>
<html>
<head>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600;700&display=swap" rel="stylesheet">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { width: 720px; height: 900px; background: #00ff00; font-family: 'Poppins', sans-serif; }
.caption { position: absolute; bottom: 80px; left: 50%; transform: translateX(-50%); max-width: 660px; text-align: center; font-size: 26px; font-weight: 600; color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.9), -1px -1px 2px rgba(0,0,0,0.5); line-height: 1.4; }
</style>
</head>
<body>
<div class="caption">${text.replace(/\n/g, '<br>')}</div>
</body>
</html>`;
}

async function main() {
  console.log('Generating brand overlay...');
  fs.writeFileSync(path.join(DIR, 'brand.html'), brandOverlayHTML);
  execSync(`cd /Users/aramide/clawd/SU && npx playwright screenshot --viewport-size=720,900 "${DIR}/brand.html" "${DIR}/brand.png"`, { stdio: 'inherit' });
  
  console.log('Generating caption overlays...');
  for (let i = 0; i < captions.length; i++) {
    const [start, end, text] = captions[i];
    const num = String(i).padStart(2, '0');
    fs.writeFileSync(path.join(DIR, `cap-${num}.html`), captionHTML(text));
    execSync(`cd /Users/aramide/clawd/SU && npx playwright screenshot --viewport-size=720,900 "${DIR}/cap-${num}.html" "${DIR}/cap-${num}.png"`, { stdio: 'pipe' });
    console.log(`  Caption ${num}: ${text.split('\\n')[0].substring(0, 40)}...`);
  }
  
  console.log('Building ffmpeg filter...');
  
  // Build complex filter for all captions
  let filterParts = [];
  let inputs = `-i "${VIDEO}" -i "${DIR}/brand.png"`;
  
  // Add all caption images as inputs
  for (let i = 0; i < captions.length; i++) {
    inputs += ` -i "${DIR}/cap-${String(i).padStart(2, '0')}.png"`;
  }
  
  // Start with brand overlay (with colorkey)
  filterParts.push(`[1:v]colorkey=0x00ff00:0.3:0.2[brand]`);
  filterParts.push(`[0:v][brand]overlay=0:0[v0]`);
  
  // Add each caption with enable timing
  for (let i = 0; i < captions.length; i++) {
    const [start, end] = captions[i];
    const inputIdx = i + 2;
    const prevLabel = i === 0 ? 'v0' : `v${i}`;
    const nextLabel = `v${i + 1}`;
    filterParts.push(`[${inputIdx}:v]colorkey=0x00ff00:0.3:0.2[cap${i}]`);
    filterParts.push(`[${prevLabel}][cap${i}]overlay=0:0:enable='between(t,${start},${end})'[${nextLabel}]`);
  }
  
  const lastLabel = `v${captions.length}`;
  const filterComplex = filterParts.join(';');
  
  const cmd = `ffmpeg -y ${inputs} -filter_complex "${filterComplex}" -map "[${lastLabel}]" -map 0:a -c:v libx264 -preset fast -crf 22 -c:a aac -b:a 192k -movflags +faststart "${DIR}/FINAL-captioned.mp4"`;
  
  console.log('Rendering video...');
  console.log(cmd.substring(0, 200) + '...');
  
  try {
    execSync(cmd, { stdio: 'inherit', timeout: 300000 });
    console.log('Done! Output: FINAL-captioned.mp4');
  } catch (e) {
    console.error('ffmpeg failed:', e.message);
  }
}

main();
