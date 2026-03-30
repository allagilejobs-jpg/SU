const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// Base styles for all slides
const baseStyles = `
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { 
    width: 1080px; height: 1920px; 
    font-family: 'Poppins', sans-serif; color: white;
    background: linear-gradient(165deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    position: relative; overflow: hidden;
  }
  .bg-shape { position: absolute; border-radius: 50%; }
  .bg-shape-1 { width: 500px; height: 500px; background: rgba(74, 144, 164, 0.08); top: -150px; right: -150px; }
  .bg-shape-2 { width: 500px; height: 500px; background: rgba(74, 144, 164, 0.08); bottom: -150px; left: -150px; }
  .caption-bar {
    position: absolute; bottom: 200px; left: 40px; right: 40px;
    background: rgba(0,0,0,0.75); padding: 24px 30px;
    text-align: center; border-radius: 12px;
  }
  .caption-text {
    font-size: 36px; font-weight: 600; line-height: 1.5;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
  }
`;

// Slide content templates
const slideContents = {
  cover: `
    <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center;padding:0 50px;">
      <div style="font-size:180px;font-weight:900;color:#E8B86D;line-height:1;margin-bottom:20px;">4</div>
      <div style="font-family:'Playfair Display',serif;font-size:90px;font-weight:800;line-height:1.1;margin-bottom:40px;"><span style="color:#E8B86D;">Sensory</span> Hacks</div>
      <div style="font-size:36px;opacity:0.8;font-weight:500;margin-bottom:60px;">That Actually Work</div>
      <div style="font-size:80px;margin-bottom:40px;">🎧 🕶️ 🌀 🍬</div>
    </div>
    <div style="position:absolute;bottom:100px;left:0;right:0;text-align:center;font-size:28px;opacity:0.6;">@spectrum_unlocked</div>
  `,
  slide1: `
    <div style="position:absolute;top:280px;left:0;right:0;text-align:center;padding:0 60px;">
      <div style="font-size:26px;text-transform:uppercase;letter-spacing:6px;opacity:0.7;margin-bottom:25px;">✨ SENSORY HACK ✨</div>
      <div style="font-family:'Playfair Display',serif;font-size:72px;font-weight:800;line-height:1.15;margin-bottom:40px;"><span style="color:#E8B86D;">Noise</span> Buffer</div>
      <div style="font-size:100px;margin-bottom:40px;">🎧</div>
      <div style="font-size:38px;font-weight:700;color:#E8B86D;margin-bottom:25px;">The Emergency Headphones</div>
      <div style="font-size:30px;line-height:1.55;opacity:0.9;max-width:920px;margin:0 auto 30px auto;">Keep noise-canceling headphones in your bag at ALL times. Even without music, they cut sound by 20-30dB — perfect for sudden sensory overload.</div>
      <div style="font-size:26px;opacity:0.65;font-style:italic;">💡 Practice putting them on at home so it's automatic in public!</div>
    </div>
    <div style="position:absolute;bottom:80px;left:0;right:0;text-align:center;"><div style="font-size:20px;opacity:0.5;letter-spacing:3px;margin-bottom:12px;">SAVE FOR LATER 💾</div><div style="font-size:26px;opacity:0.6;">@spectrum_unlocked</div></div>
  `,
  slide2: `
    <div style="position:absolute;top:280px;left:0;right:0;text-align:center;padding:0 60px;">
      <div style="font-size:26px;text-transform:uppercase;letter-spacing:6px;opacity:0.7;margin-bottom:25px;">✨ SENSORY HACK ✨</div>
      <div style="font-family:'Playfair Display',serif;font-size:72px;font-weight:800;line-height:1.15;margin-bottom:40px;"><span style="color:#E8B86D;">Sunglasses</span> Indoors</div>
      <div style="font-size:100px;margin-bottom:40px;">🕶️</div>
      <div style="font-size:38px;font-weight:700;color:#E8B86D;margin-bottom:25px;">Light Sensitivity Solution</div>
      <div style="font-size:30px;line-height:1.55;opacity:0.9;max-width:920px;margin:0 auto 30px auto;">Fluorescent lights in stores and schools can be overwhelming. Let your child wear sunglasses indoors — who cares what people think?</div>
      <div style="font-size:26px;opacity:0.65;font-style:italic;">💡 Your child's comfort > strangers' opinions. Every time.</div>
    </div>
    <div style="position:absolute;bottom:80px;left:0;right:0;text-align:center;"><div style="font-size:20px;opacity:0.5;letter-spacing:3px;margin-bottom:12px;">SAVE FOR LATER 💾</div><div style="font-size:26px;opacity:0.6;">@spectrum_unlocked</div></div>
  `,
  slide3: `
    <div style="position:absolute;top:280px;left:0;right:0;text-align:center;padding:0 60px;">
      <div style="font-size:26px;text-transform:uppercase;letter-spacing:6px;opacity:0.7;margin-bottom:25px;">✨ SENSORY HACK ✨</div>
      <div style="font-family:'Playfair Display',serif;font-size:72px;font-weight:800;line-height:1.15;margin-bottom:40px;"><span style="color:#E8B86D;">Fidget</span> Rotation</div>
      <div style="font-size:100px;margin-bottom:40px;">🌀</div>
      <div style="font-size:38px;font-weight:700;color:#E8B86D;margin-bottom:25px;">Keep Them Effective</div>
      <div style="font-size:30px;line-height:1.55;opacity:0.9;max-width:920px;margin:0 auto 30px auto;">Keep 3-4 different fidgets and rotate them weekly. Kids get bored — the novelty is what keeps them working.</div>
      <div style="font-size:26px;opacity:0.65;font-style:italic;">💡 Silent fidgets work best for school!</div>
    </div>
    <div style="position:absolute;bottom:80px;left:0;right:0;text-align:center;"><div style="font-size:20px;opacity:0.5;letter-spacing:3px;margin-bottom:12px;">SAVE FOR LATER 💾</div><div style="font-size:26px;opacity:0.6;">@spectrum_unlocked</div></div>
  `,
  slide4: `
    <div style="position:absolute;top:280px;left:0;right:0;text-align:center;padding:0 60px;">
      <div style="font-size:26px;text-transform:uppercase;letter-spacing:6px;opacity:0.7;margin-bottom:25px;">✨ SENSORY HACK ✨</div>
      <div style="font-family:'Playfair Display',serif;font-size:72px;font-weight:800;line-height:1.15;margin-bottom:40px;"><span style="color:#E8B86D;">Chewing</span> is Calming</div>
      <div style="font-size:100px;margin-bottom:40px;">🍬</div>
      <div style="font-size:38px;font-weight:700;color:#E8B86D;margin-bottom:25px;">Oral Sensory Input</div>
      <div style="font-size:30px;line-height:1.55;opacity:0.9;max-width:920px;margin:0 auto 30px auto;">Chewing is calming! Silicone chew necklaces, crunchy snacks, or thick smoothies through a straw all provide regulating oral input.</div>
      <div style="font-size:26px;opacity:0.65;font-style:italic;">💡 Offer them BEFORE the meltdown starts!</div>
    </div>
    <div style="position:absolute;bottom:80px;left:0;right:0;text-align:center;"><div style="font-size:20px;opacity:0.5;letter-spacing:3px;margin-bottom:12px;">SAVE FOR LATER 💾</div><div style="font-size:26px;opacity:0.6;">@spectrum_unlocked</div></div>
  `
};

// Caption segments with timing and which slide they appear on
const segments = [
  { id: '01', slide: 'cover', caption: 'Sensory hacks that actually work.' },
  { id: '02', slide: 'slide1', caption: 'Number one.' },
  { id: '03', slide: 'slide1', caption: 'Keep noise-canceling headphones<br>in your bag at all times.' },
  { id: '04', slide: 'slide1', caption: 'Even without music, they cut<br>overwhelming sounds by 30%.' },
  { id: '05', slide: 'slide1', caption: 'Game changer for grocery stores.' },
  { id: '06', slide: 'slide2', caption: 'Number two.' },
  { id: '07', slide: 'slide2', caption: 'Let your kid wear sunglasses indoors.' },
  { id: '08', slide: 'slide2', caption: 'Fluorescent lights are brutal<br>for sensory-sensitive kids.' },
  { id: '09', slide: 'slide2', caption: 'Who cares what people think?' },
  { id: '10', slide: 'slide3', caption: 'Number three.' },
  { id: '11', slide: 'slide3', caption: 'Rotate fidgets weekly.' },
  { id: '12', slide: 'slide3', caption: 'Kids get bored. The novelty<br>is what keeps them working.' },
  { id: '13', slide: 'slide4', caption: 'Number four.' },
  { id: '14', slide: 'slide4', caption: 'Chewing is calming.' },
  { id: '15', slide: 'slide4', caption: 'Chew necklaces, crunchy snacks,<br>thick smoothies through a straw.' },
  { id: '16', slide: 'slide4', caption: 'Offer them before the meltdown starts.' },
  { id: '17', slide: 'slide4', caption: 'Save this for later.' },
  { id: '18', slide: 'slide4', caption: 'Follow for more autism parenting tips.' }
];

function generateHTML(slideContent, caption) {
  return `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800;900&family=Playfair+Display:wght@700;800;900&display=swap" rel="stylesheet">
  <style>${baseStyles}</style>
</head>
<body>
  <div class="bg-shape bg-shape-1"></div>
  <div class="bg-shape bg-shape-2"></div>
  ${slideContent}
  <div class="caption-bar">
    <div class="caption-text">${caption}</div>
  </div>
</body>
</html>`;
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1080, height: 1920 });
  
  for (const seg of segments) {
    const html = generateHTML(slideContents[seg.slide], seg.caption);
    const htmlPath = path.join(__dirname, `seg_${seg.id}.html`);
    fs.writeFileSync(htmlPath, html);
    
    await page.goto('file://' + htmlPath);
    await page.waitForTimeout(500); // Wait for fonts
    await page.screenshot({ path: path.join(__dirname, `seg_${seg.id}.png`) });
    console.log(`Generated seg_${seg.id}.png`);
  }
  
  await browser.close();
  console.log('Done!');
}

main();
