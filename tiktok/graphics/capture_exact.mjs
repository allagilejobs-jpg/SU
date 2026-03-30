import puppeteer from 'puppeteer';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

(async () => {
  const browser = await puppeteer.launch({ 
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const page = await browser.newPage();
  
  // Set viewport to exact TikTok size - no deviceScaleFactor to avoid 2x
  await page.setViewport({ 
    width: 1080, 
    height: 1920,
    deviceScaleFactor: 1 
  });

  const templates = [
    'tiktok-01-headphones',
    'tiktok-02-sunglasses', 
    'tiktok-03-fidgets',
    'tiktok-04-chewy'
  ];

  for (const name of templates) {
    const htmlPath = path.join(__dirname, `${name}.html`);
    await page.goto(`file://${htmlPath}`, { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 500)); // Wait for fonts
    await page.screenshot({ 
      path: `${name}-hd.png`, 
      type: 'png',
      clip: { x: 0, y: 0, width: 1080, height: 1920 }
    });
    console.log(`Created: ${name}-hd.png`);
  }

  await browser.close();
  console.log('All screenshots captured at 1080x1920!');
})();
