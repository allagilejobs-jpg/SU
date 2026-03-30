const puppeteer = require('puppeteer');
const path = require('path');

(async () => {
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  await page.setViewport({ width: 1080, height: 1920 });

  const templates = [
    'tiktok-01-headphones',
    'tiktok-02-sunglasses', 
    'tiktok-03-fidgets',
    'tiktok-04-chewy'
  ];

  for (const name of templates) {
    const htmlPath = path.join(__dirname, `${name}.html`);
    await page.goto(`file://${htmlPath}`, { waitUntil: 'networkidle0' });
    await page.screenshot({ path: `${name}.png`, type: 'png' });
    console.log(`Created: ${name}.png`);
  }

  await browser.close();
  console.log('All screenshots captured!');
})();
