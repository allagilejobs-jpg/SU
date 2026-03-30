const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const whisperData = JSON.parse(fs.readFileSync(path.join(__dirname, 'sensory-hacks-voiceover.json')));

// Anticipation offset - show word slightly before it's spoken
const ANTICIPATE_MS = 120; // milliseconds early

function getSlideForTime(t) {
  if (t < 2.74) return 'cover';
  if (t < 15.68) return 'slide1';
  if (t < 26.7) return 'slide2';
  if (t < 35.26) return 'slide3';
  return 'slide4';
}

const slideContents = {
  cover: `<div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center;padding:0 50px;width:100%;">
      <div style="font-size:180px;font-weight:900;color:#E8B86D;line-height:1;margin-bottom:20px;">4</div>
      <div style="font-family:'Playfair Display',serif;font-size:90px;font-weight:800;line-height:1.1;margin-bottom:30px;"><span style="color:#E8B86D;">Sensory</span> Hacks</div>
      <div style="font-size:36px;opacity:0.8;font-weight:500;margin-bottom:50px;">That Actually Work</div>
      <div style="font-size:80px;">🎧 🕶️ 🌀 🍬</div>
    </div>
    <div style="position:absolute;bottom:100px;left:0;right:0;text-align:center;font-size:28px;opacity:0.6;">@spectrum_unlocked</div>`,
  slide1: `<div style="position:absolute;top:420px;left:0;right:0;text-align:center;padding:0 50px;">
      <div style="font-size:22px;text-transform:uppercase;letter-spacing:5px;opacity:0.7;margin-bottom:18px;">✨ SENSORY HACK ✨</div>
      <div style="font-family:'Playfair Display',serif;font-size:58px;font-weight:800;line-height:1.15;margin-bottom:20px;"><span style="color:#E8B86D;">Noise</span> Buffer</div>
      <div style="font-size:80px;margin-bottom:20px;">🎧</div>
      <div style="font-size:32px;font-weight:700;color:#E8B86D;margin-bottom:30px;">The Emergency Headphones</div>
      <div style="font-size:32px;font-weight:400;line-height:1.6;margin-bottom:30px;">Keep noise-canceling headphones in your bag at ALL times. Even without music, they cut sound by 20-30dB — perfect for sudden sensory overload.</div>
      <div style="font-size:28px;font-style:italic;opacity:0.8;">💡 Practice putting them on at home so it's automatic in public!</div>
    </div>
    <div style="position:absolute;bottom:60px;left:0;right:0;text-align:center;"><div style="font-size:18px;opacity:0.5;letter-spacing:3px;margin-bottom:10px;">SAVE FOR LATER 💾</div><div style="font-size:24px;opacity:0.6;">@spectrum_unlocked</div></div>`,
  slide2: `<div style="position:absolute;top:420px;left:0;right:0;text-align:center;padding:0 50px;">
      <div style="font-size:22px;text-transform:uppercase;letter-spacing:5px;opacity:0.7;margin-bottom:18px;">✨ SENSORY HACK ✨</div>
      <div style="font-family:'Playfair Display',serif;font-size:58px;font-weight:800;line-height:1.15;margin-bottom:20px;"><span style="color:#E8B86D;">Sunglasses</span> Indoors</div>
      <div style="font-size:80px;margin-bottom:20px;">🕶️</div>
      <div style="font-size:32px;font-weight:700;color:#E8B86D;margin-bottom:30px;">Light Sensitivity Solution</div>
      <div style="font-size:32px;font-weight:400;line-height:1.6;margin-bottom:30px;">Who cares what people think? Your child's comfort matters more than strangers' opinions.</div>
      <div style="font-size:28px;font-style:italic;opacity:0.8;">💡 Tinted lenses work even better than dark ones!</div>
    </div>
    <div style="position:absolute;bottom:60px;left:0;right:0;text-align:center;"><div style="font-size:18px;opacity:0.5;letter-spacing:3px;margin-bottom:10px;">SAVE FOR LATER 💾</div><div style="font-size:24px;opacity:0.6;">@spectrum_unlocked</div></div>`,
  slide3: `<div style="position:absolute;top:420px;left:0;right:0;text-align:center;padding:0 50px;">
      <div style="font-size:22px;text-transform:uppercase;letter-spacing:5px;opacity:0.7;margin-bottom:18px;">✨ SENSORY HACK ✨</div>
      <div style="font-family:'Playfair Display',serif;font-size:58px;font-weight:800;line-height:1.15;margin-bottom:20px;"><span style="color:#E8B86D;">Fidget</span> Rotation</div>
      <div style="font-size:80px;margin-bottom:20px;">🌀</div>
      <div style="font-size:32px;font-weight:700;color:#E8B86D;margin-bottom:30px;">Keep Them Effective</div>
      <div style="font-size:32px;font-weight:400;line-height:1.6;margin-bottom:30px;">Rotate fidget toys weekly. The novelty is what keeps them working.</div>
      <div style="font-size:28px;font-style:italic;opacity:0.8;">💡 Keep a "fidget drawer" and swap them out regularly!</div>
    </div>
    <div style="position:absolute;bottom:60px;left:0;right:0;text-align:center;"><div style="font-size:18px;opacity:0.5;letter-spacing:3px;margin-bottom:10px;">SAVE FOR LATER 💾</div><div style="font-size:24px;opacity:0.6;">@spectrum_unlocked</div></div>`,
  slide4: `<div style="position:absolute;top:420px;left:0;right:0;text-align:center;padding:0 50px;">
      <div style="font-size:22px;text-transform:uppercase;letter-spacing:5px;opacity:0.7;margin-bottom:18px;">✨ SENSORY HACK ✨</div>
      <div style="font-family:'Playfair Display',serif;font-size:58px;font-weight:800;line-height:1.15;margin-bottom:20px;"><span style="color:#E8B86D;">Chewing</span> is Calming</div>
      <div style="font-size:80px;margin-bottom:20px;">🍬</div>
      <div style="font-size:32px;font-weight:700;color:#E8B86D;margin-bottom:30px;">Oral Sensory Input</div>
      <div style="font-size:32px;font-weight:400;line-height:1.6;margin-bottom:30px;">Chew necklaces, crunchy snacks, thick smoothies through a straw. Offer them before the meltdown starts.</div>
      <div style="font-size:28px;font-style:italic;opacity:0.8;">💡 Ice chips work great in a pinch!</div>
    </div>
    <div style="position:absolute;bottom:60px;left:0;right:0;text-align:center;"><div style="font-size:18px;opacity:0.5;letter-spacing:3px;margin-bottom:10px;">SAVE FOR LATER 💾</div><div style="font-size:24px;opacity:0.6;">@spectrum_unlocked</div></div>`
};

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
  return `<!DOCTYPE html><html><head><meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800;900&family=Playfair+Display:wght@700;800;900&display=swap" rel="stylesheet">
<style>*{margin:0;padding:0;box-sizing:border-box;}body{width:1080px;height:1920px;font-family:'Poppins',sans-serif;color:white;background:linear-gradient(165deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%);position:relative;overflow:hidden;}.bg-shape{position:absolute;border-radius:50%;}.bg-shape-1{width:500px;height:500px;background:rgba(74,144,164,0.08);top:-150px;right:-150px;}.bg-shape-2{width:500px;height:500px;background:rgba(74,144,164,0.08);bottom:-150px;left:-150px;}.caption-area{position:absolute;bottom:380px;left:40px;right:40px;text-align:center;}.caption-text{font-size:38px;font-weight:600;line-height:1.4;text-shadow:3px 3px 8px rgba(0,0,0,0.9),-2px -2px 4px rgba(0,0,0,0.6);}</style></head>
<body><div class="bg-shape bg-shape-1"></div><div class="bg-shape bg-shape-2"></div>${slideContent}<div class="caption-area"><div class="caption-text">${wordsHTML}</div></div></body></html>`;
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1080, height: 1920 });
  
  fs.mkdirSync(path.join(__dirname, 'synced'), { recursive: true });
  
  // Build a timeline of all words with their absolute start/end times
  const allWords = [];
  for (const seg of whisperData.segments) {
    if (!seg.words || seg.words.length === 0) continue;
    for (const w of seg.words) {
      allWords.push({
        word: w.word.trim(),
        start: w.start,
        end: w.end,
        segStart: seg.start
      });
    }
  }
  
  // Generate frames at 30fps with anticipated timing
  const FPS = 30;
  const FRAME_DURATION = 1 / FPS;
  const TOTAL_DURATION = 51.7; // seconds
  
  const segments = [];
  let currentWordIdx = 0;
  let lastSlide = null;
  let lastWordsInSentence = [];
  let lastHighlightIdx = -1;
  
  for (let frameNum = 0; frameNum < TOTAL_DURATION * FPS; frameNum++) {
    const currentTime = frameNum * FRAME_DURATION;
    const anticipatedTime = currentTime + (ANTICIPATE_MS / 1000);
    
    // Find which word should be highlighted at this anticipated time
    let highlightIdx = -1;
    for (let i = 0; i < allWords.length; i++) {
      if (anticipatedTime >= allWords[i].start && anticipatedTime < allWords[i].end) {
        highlightIdx = i;
        break;
      }
      // If we're past this word, it stays highlighted until next word starts
      if (anticipatedTime >= allWords[i].end && (i === allWords.length - 1 || anticipatedTime < allWords[i + 1].start)) {
        highlightIdx = i;
        break;
      }
    }
    
    // Determine slide
    const slide = getSlideForTime(currentTime);
    
    // Get words in current sentence for caption display
    let sentenceWords = [];
    let sentenceHighlightIdx = -1;
    
    if (highlightIdx >= 0) {
      // Find the sentence this word belongs to
      const wordInfo = allWords[highlightIdx];
      for (const seg of whisperData.segments) {
        if (seg.start <= wordInfo.start && seg.words) {
          const lastWordInSeg = seg.words[seg.words.length - 1];
          if (lastWordInSeg.end >= wordInfo.start) {
            sentenceWords = seg.words;
            // Find highlight index within this sentence
            for (let i = 0; i < seg.words.length; i++) {
              if (seg.words[i].start === wordInfo.start) {
                sentenceHighlightIdx = i;
                break;
              }
            }
            break;
          }
        }
      }
    }
    
    // Check if we need a new frame (slide changed, highlight changed, or first frame)
    const needNewFrame = frameNum === 0 || 
                         slide !== lastSlide || 
                         sentenceHighlightIdx !== lastHighlightIdx ||
                         JSON.stringify(sentenceWords) !== JSON.stringify(lastWordsInSentence);
    
    if (needNewFrame) {
      const wordsHTML = sentenceWords.length > 0 ? generateWordHTML(sentenceWords, sentenceHighlightIdx) : '';
      const html = generateHTML(slideContents[slide], wordsHTML);
      
      const segNum = segments.length;
      const htmlPath = path.join(__dirname, 'synced', `seg_${String(segNum).padStart(3, '0')}.html`);
      const pngPath = path.join(__dirname, 'synced', `seg_${String(segNum).padStart(3, '0')}.png`);
      
      fs.writeFileSync(htmlPath, html);
      await page.goto('file://' + htmlPath);
      await page.waitForTimeout(50);
      await page.screenshot({ path: pngPath });
      
      if (segments.length > 0) {
        // Set duration of previous segment
        segments[segments.length - 1].duration = currentTime - segments[segments.length - 1].startTime;
      }
      
      segments.push({ 
        file: `seg_${String(segNum).padStart(3, '0')}.png`, 
        startTime: currentTime,
        duration: 0 
      });
      
      lastSlide = slide;
      lastHighlightIdx = sentenceHighlightIdx;
      lastWordsInSentence = [...sentenceWords];
      
      if (segNum % 20 === 0) {
        console.log(`Generated segment ${segNum} at ${currentTime.toFixed(2)}s`);
      }
    }
  }
  
  // Set final segment duration
  if (segments.length > 0) {
    segments[segments.length - 1].duration = TOTAL_DURATION - segments[segments.length - 1].startTime;
  }
  
  await browser.close();
  
  // Generate concat file
  let concatFile = '';
  for (const seg of segments) {
    if (seg.duration > 0) {
      concatFile += `file 'synced/${seg.file}'\n`;
      concatFile += `duration ${seg.duration.toFixed(4)}\n`;
    }
  }
  // Add last file again (ffmpeg concat requirement)
  concatFile += `file 'synced/${segments[segments.length - 1].file}'\n`;
  
  fs.writeFileSync(path.join(__dirname, 'concat-synced.txt'), concatFile);
  console.log(`\nDone! Generated ${segments.length} unique frames.`);
}

main();
