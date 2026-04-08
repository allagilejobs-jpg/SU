import { chromium } from 'playwright';

const BASE = 'C:/Users/Solomon/Desktop/SU/content/curated';
const artists = ['holly-peete', 'ot-genasis', 'faith-evans'];
const designs = ['a1-magazine', 'a2-minimalist', 'a3-split'];

const browser = await chromium.launch();
for (const artist of artists) {
  for (const d of designs) {
    const html = `${BASE}/${artist}/cover-options/${d}.html`;
    const out  = `${BASE}/${artist}/cover-options/${d}.png`;
    const ctx = await browser.newContext({
      viewport: { width: 1080, height: 1920 },
      deviceScaleFactor: 1,
    });
    const page = await ctx.newPage();
    await page.goto('file:///' + html);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(800);
    await page.screenshot({
      path: out,
      clip: { x: 0, y: 0, width: 1080, height: 1920 },
    });
    console.log('rendered ->', out);
    await ctx.close();
  }
}
await browser.close();
