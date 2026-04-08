import { chromium } from 'playwright';

const BASE = 'C:/Users/Solomon/Desktop/SU/content/curated';
const targets = [
  { html: `${BASE}/holly-peete/brand-overlay-v2.html`, out: `${BASE}/holly-peete/brand-overlay-v2.png` },
  { html: `${BASE}/ot-genasis/brand-overlay-v2.html`,  out: `${BASE}/ot-genasis/brand-overlay-v2.png`  },
  { html: `${BASE}/faith-evans/brand-overlay-v2.html`, out: `${BASE}/faith-evans/brand-overlay-v2.png` },
];

const browser = await chromium.launch();
for (const t of targets) {
  const ctx = await browser.newContext({
    viewport: { width: 1080, height: 1920 },
    deviceScaleFactor: 1,
  });
  const page = await ctx.newPage();
  await page.goto('file:///' + t.html);
  await page.waitForLoadState('networkidle');
  // Wait briefly for fonts
  await page.waitForTimeout(800);
  await page.screenshot({
    path: t.out,
    omitBackground: true,
    clip: { x: 0, y: 0, width: 1080, height: 1920 },
  });
  console.log('rendered ->', t.out);
  await ctx.close();
}
await browser.close();
