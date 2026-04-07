const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const DIR = __dirname;
const VIDEO = '/tmp/insta_post.mp4';

// Create the branded frame (background with logo, headline - video goes in center)
const frameHTML = `<!DOCTYPE html>
<html>
<head>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600;700;800;900&display=swap" rel="stylesheet">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { 
  width: 1080px; 
  height: 1350px; 
  background: linear-gradient(165deg, #0a0a15 0%, #16213e 40%, #0f3460 100%);
  font-family: 'Poppins', sans-serif; 
  position: relative;
}
.brand { position: absolute; top: 40px; left: 50px; }
.brand-main { font-size: 28px; font-weight: 900; color: white; letter-spacing: 1px; }
.brand-sub { font-size: 20px; font-weight: 700; color: #4A90A4; letter-spacing: 1px; }
.headline { 
  position: absolute; 
  top: 130px; 
  left: 50%; 
  transform: translateX(-50%); 
  font-size: 26px; 
  font-weight: 700; 
  color: white; 
  text-align: center;
  max-width: 900px;
  line-height: 1.4;
}
.headline .name { color: #E8B86D; }
/* Video area is 800x1000 centered, starting at y=220 */
.video-placeholder {
  position: absolute;
  top: 220px;
  left: 140px;
  width: 800px;
  height: 1000px;
  background: #00ff00;
  border-radius: 12px;
}
.footer {
  position: absolute;
  bottom: 40px;
  left: 50%;
  transform: translateX(-50%);
  text-align: center;
}
.handle { font-size: 22px; font-weight: 700; color: #4A90A4; }
.website { font-size: 16px; color: rgba(255,255,255,0.6); margin-top: 5px; }
</style>
</head>
<body>
<div class="brand">
  <div class="brand-main">SPECTRUM</div>
  <div class="brand-sub">UNLOCKED</div>
</div>
<div class="headline"><span class="name">Parent</span> Opens Up About Having to BEG for an Autism Diagnosis</div>
<div class="video-placeholder"></div>
<div class="footer">
  <div class="handle">@spectrum_unlocked</div>
  <div class="website">spectrumunlocked.com</div>
</div>
</body>
</html>`;

async function main() {
  console.log('Creating branded frame...');
  fs.writeFileSync(path.join(DIR, 'frame.html'), frameHTML);
  execSync(`cd /Users/aramide/clawd/SU && npx playwright screenshot --viewport-size=1080,1350 "${DIR}/frame.html" "${DIR}/frame.png"`, { stdio: 'inherit' });
  
  console.log('Compositing video into frame...');
  // Scale video to fit in the 800x1000 green area, then overlay frame with colorkey
  // Video is 720x900, scale to fit 800x1000 (keeping aspect ratio = 800x1000)
  const cmd = `ffmpeg -y -i "${VIDEO}" -i "${DIR}/frame.png" \\
    -filter_complex "[0:v]scale=800:1000:force_original_aspect_ratio=decrease,pad=800:1000:(ow-iw)/2:(oh-ih)/2:color=#1a1a2e[vid];[1:v]colorkey=0x00ff00:0.3:0.2[frame];[vid]pad=1080:1350:140:220:color=#16213e[canvas];[canvas][frame]overlay=0:0" \\
    -c:v libx264 -preset fast -crf 22 -c:a aac -b:a 192k \\
    -movflags +faststart \\
    "${DIR}/FINAL-framed-video.mp4"`;
  
  console.log('Running ffmpeg...');
  try {
    execSync(cmd, { stdio: 'inherit', timeout: 300000 });
    console.log('Done! Output: FINAL-framed-video.mp4');
  } catch(e) {
    console.error('Error:', e.message);
  }
}

main();
