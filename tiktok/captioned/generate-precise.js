const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// Load Whisper timestamps
const whisperData = JSON.parse(fs.readFileSync(path.join(__dirname, 'sensory-hacks-voiceover.json')));

// Extract all words with timestamps
const allWords = [];
whisperData.segments.forEach(seg => {
  if (seg.words) {
    seg.words.forEach(w => {
      allWords.push({
        word: w.word.trim(),
        start: w.start,
        end: w.end
      });
    });
  }
});

console.log(`Loaded ${allWords.length} words with timestamps`);

// Map words to slides based on timestamp
function getSlideForTime(t) {
  if (t < 2.74) return 'cover';
  if (t < 15.68) return 'slide1';
  if (t < 26.7) return 'slide2';
  if (t < 35.26) return 'slide3';
  return 'slide4';
}

const slideContents = {
  cover: `<div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-60%);text-align:center;padding:0 50px;">
      <div style="font-size:180px;font-weight:900;color:#E8B86D;line-height:1;margin-bottom:20px;">4</div>
      <div style="font-family:'Playfair Display',serif;font-size:90px;font-weight:800;line-height:1.1;margin-bottom:40px;"><span style="color:#E8B86D;">Sensory</span> Hacks</div>
      <div style="font-size:36px;opacity:0.8;font-weight:500;margin-bottom:60px;">That Actually Work</div>
      <div style="font-size:80px;margin-bottom:40px;">🎧 🕶️ 🌀 🍬</div>
    </div>
    <div style="position:absolute;bottom:100px;left:0;right:0;text-align:center;font-size:28px;opacity:0.6;">@spectrum_unlocked</div>`,
  slide1: `<div style="position:absolute;top:200px;left:0;right:0;text-align:center;padding:0 60px;">
      <div style="font-size:26px;text-transform:uppercase;letter-spacing:6px;opacity:0.7;margin-bottom:25px;">✨ SENSORY HACK ✨</div>
      <div style="font-family:'Playfair Display',serif;font-size:72px;font-weight:800;line-height:1.15;margin-bottom:40px;"><span style="color:#E8B86D;">Noise</span> Buffer</div>
      <div style="font-size:100px;margin-bottom:40px;">🎧</div>
      <div style="font-size:38px;font-weight:700;color:#E8B86D;margin-bottom:25px;">The Emergency Headphones</div>
    </div>
    <div style="position:absolute;bottom:80px;left:0;right:0;text-align:center;"><div style="font-size:20px;opacity:0.5;letter-spacing:3px;margin-bottom:12px;">SAVE FOR LATER 💾</div><div style="font-size:26px;opacity:0.6;">@spectrum_unlocked</div></div>`,
  slide2: `<div style="position:absolute;top:200px;left:0;right:0;text-align:center;padding:0 60px;">
      <div style="font-size:26px;text-transform:uppercase;letter-spacing:6px;opacity:0.7;margin-bottom:25px;">✨ SENSORY HACK ✨</div>
      <div style="font-family:'Playfair Display',serif;font-size:72px;font-weight:800;line-height:1.15;margin-bottom:40px;"><span style="color:#E8B86D;">Sunglasses</span> Indoors</div>
      <div style="font-size:100px;margin-bottom:40px;">🕶️</div>
      <div style="font-size:38px;font-weight:700;color:#E8B86D;margin-bottom:25px;">Light Sensitivity Solution</div>
    </div>
    <div style="position:absolute;bottom:80px;left:0;right:0;text-align:center;"><div style="font-size:20px;opacity:0.5;letter-spacing:3px;margin-bottom:12px;">SAVE FOR LATER 💾</div><div style="font-size:26px;opacity:0.6;">@spectrum_unlocked</div></div>`,
  slide3: `<div style="position:absolute;top:200px;left:0;right:0;text-align:center;padding:0 60px;">
      <div style="font-size:26px;text-transform:uppercase;letter-spacing:6px;opacity:0.7;margin-bottom:25px;">✨ SENSORY HACK ✨</div>
      <div style="font-family:'Playfair Display',serif;font-size:72px;font-weight:800;line-height:1.15;margin-bottom:40px;"><span style="color:#E8B86D;">Fidget</span> Rotation</div>
      <div style="font-size:100px;margin-bottom:40px;">🌀</div>
      <div style="font-size:38px;font-weight:700;color:#E8B86D;margin-bottom:25px;">Keep Them Effective</div>
    </div>
    <div style="position:absolute;bottom:80px;left:0;right:0;text-align:center;"><div style="font-size:20px;opacity:0.5;letter-spacing:3px;margin-bottom:12px;">SAVE FOR LATER 💾</div><div style="font-size:26px;opacity:0.6;">@spectrum_unlocked</div></div>`,
  slide4: `<div style="position:absolute;top:200px;left:0;right:0;text-align:center;padding:0 60px;">
      <div style="font-size:26px;text-transform:uppercase;letter-spacing:6px;opacity:0.7;margin-bottom:25px;">✨ SENSORY HACK ✨</div>
      <div style="font-family:'Playfair Display',serif;font-size:72px;font-weight:800;line-height:1.15;margin-bottom:40px;"><span style="color:#E8B86D;">Chewing</span> is Calming</div>
      <div style="font-size:100px;margin-bottom:40px;">🍬</div>
      <div style="font-size:38px;font-weight:700;color:#E8B86D;margin-bottom:25px;">Oral Sensory Input</div>
    </div>
    <div style="position:absolute;bottom:80px;left:0;right:0;text-align:center;"><div style="font-size:20px;opacity:0.5;letter-spacing:3px;margin-bottom:12px;">SAVE FOR LATER 💾</div><div style="font-size:26px;opacity:0.6;">@spectrum_unlocked</div></div>`
};

// Group words into sentences (by segment)
const sentences = whisperData.segments.map(seg => ({
  words: seg.words || [],
  slide: getSlideForTime(seg.start)
}));

function generateWordHTML(words, highlightIndex) {
  return words.map((w, i) => {
    const word = w.word.trim();
    if (i === highlightIndex) {
      return `<span style="color:#E8B86D;font-weight:800;transform:scale(1.15);display:inline-block;text-shadow:0 0 30px rgba(232,184,109,0.7),0 0 60px rgba(232,184,109,0.4);">${word}</span>`;
    } else if (i < highlightIndex) {
      return `<span style="color:white;">${word}</span>`;
    } else {
      return `<span style="color:rgba(255,255,255,0.35);">${word}</span>`;
    }
  }).join(' ');
}

function generateHTML(slideContent, wordsHTML) {
  return `<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800;900&family=Playfair+Display:wght@700;800;900&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{width:1080px;height:1920px;font-family:'Poppins',sans-serif;color:white;background:linear-gradient(165deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%);position:relative;overflow:hidden;}
.bg-shape{position:absolute;border-radius:50%;}
.bg-shape-1{width:500px;height:500px;background:rgba(74,144,164,0.08);top:-150px;right:-150px;}
.bg-shape-2{width:500px;height:500px;background:rgba(74,144,164,0.08);bottom:-150px;left:-150px;}
.caption-area{position:absolute;bottom:300px;left:60px;right:60px;text-align:center;}
.caption-text{font-size:46px;font-weight:600;line-height:1.6;text-shadow:3px 3px 8px rgba(0,0,0,0.9),-2px -2px 4px rgba(0,0,0,0.6);}
</style></head>
<body>
<div class="bg-shape bg-shape-1"></div>
<div class="bg-shape bg-shape-2"></div>
${slideContent}
<div class="caption-area"><div class="caption-text">${wordsHTML}</div></div>
</body></html>`;
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1080, height: 1920 });
  
  fs.mkdirSync(path.join(__dirname, 'precise'), { recursive: true });
  
  const segments = [];
  let segNum = 0;
  
  for (const sentence of sentences) {
    if (!sentence.words || sentence.words.length === 0) continue;
    
    for (let wordIdx = 0; wordIdx < sentence.words.length; wordIdx++) {
      const w = sentence.words[wordIdx];
      const duration = w.end - w.start;
      
      const wordsHTML = generateWordHTML(sentence.words, wordIdx);
      const html = generateHTML(slideContents[sentence.slide], wordsHTML);
      
      const htmlPath = path.join(__dirname, 'precise', `seg_${String(segNum).padStart(3, '0')}.html`);
      const pngPath = path.join(__dirname, 'precise', `seg_${String(segNum).padStart(3, '0')}.png`);
      
      fs.writeFileSync(htmlPath, html);
      await page.goto('file://' + htmlPath);
      await page.waitForTimeout(150);
      await page.screenshot({ path: pngPath });
      
      segments.push({ file: `seg_${String(segNum).padStart(3, '0')}.png`, duration: duration });
      console.log(`seg_${segNum}: "${w.word.trim()}" @ ${w.start.toFixed(2)}s (${duration.toFixed(2)}s)`);
      segNum++;
    }
  }
  
  await browser.close();
  
  // Generate ffmpeg concat file
  let concatFile = '';
  segments.forEach(seg => {
    concatFile += `file 'precise/${seg.file}'\n`;
    concatFile += `duration ${seg.duration.toFixed(4)}\n`;
  });
  concatFile += `file 'precise/${segments[segments.length-1].file}'\n`;
  
  fs.writeFileSync(path.join(__dirname, 'concat-precise.txt'), concatFile);
  console.log(`\nDone! Generated ${segNum} segments with precise timing.`);
}

main();
