import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

const BASE = 'C:/Users/Solomon/Desktop/SU/content/curated';
const artists = ['holly-peete', 'ot-genasis', 'faith-evans'];

const browser = await chromium.launch();
for (const artist of artists) {
  const dir = `${BASE}/${artist}/carousel-v2`;
  if (!fs.existsSync(dir)) continue;
  const files = fs.readdirSync(dir).filter(f => f.endsWith('.html'));
  for (const f of files) {
    const html = `${dir}/${f}`;
    const out  = `${dir}/${f.replace(/\.html$/, '.png')}`;
    const ctx = await browser.newContext({
      viewport: { width: 1080, height: 1350 },
      deviceScaleFactor: 1,
    });
    const page = await ctx.newPage();
    await page.goto('file:///' + html);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(800);
    await page.screenshot({
      path: out,
      clip: { x: 0, y: 0, width: 1080, height: 1350 },
    });
    console.log('rendered ->', out);
    await ctx.close();
  }
}
await browser.close();
