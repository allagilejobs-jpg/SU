const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

async function exportSlides() {
  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: 1080, height: 1350 },
    deviceScaleFactor: 2  // 2x pixel density for crisp rendering
  });
  
  const page = await context.newPage();
  const dir = __dirname;
  const outDir = path.join(dir, 'hq2x');
  
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir);
  
  const slides = [
    'slide-01-cover.html',
    'slide-02-myth1.html', 
    'slide-03-myth2.html',
    'slide-04-myth3.html',
    'slide-05-cta.html'
  ];
  
  for (const slide of slides) {
    const filePath = path.join(dir, slide);
    const outPath = path.join(outDir, slide.replace('.html', '.png'));
    
    await page.goto('file://' + filePath);
    await page.screenshot({ 
      path: outPath,
      type: 'png'
    });
    console.log('✓ Exported:', slide.replace('.html', '.png'));
  }
  
  await browser.close();
  console.log('Done! Files in hq2x/ folder');
}

exportSlides().catch(console.error);
