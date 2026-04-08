import { chromium } from 'playwright';
const BASE = 'C:/Users/Solomon/Desktop/SU/content/curated';
const targets = [
  {
    html: `${BASE}/holly-peete/cover-slide.html`,
    out:  `${BASE}/holly-peete/cover-slide-v3.png`,
  },
  {
    html: `${BASE}/ot-genasis/cover-slide.html`,
    out:  `${BASE}/ot-genasis/cover-slide-v3.png`,
  },
];

const browser = await chromium.launch();
for (const t of targets) {
  const ctx = await browser.newContext({
    viewport: { width: 1080, height: 1350 },
    deviceScaleFactor: 1,
  });
  const page = await ctx.newPage();
  await page.goto('file:///' + t.html);
  await page.waitForLoadState('networkidle');
  await page.screenshot({ path: t.out, clip: { x: 0, y: 0, width: 1080, height: 1350 } });
  console.log('rendered ->', t.out);
  await ctx.close();
}
await browser.close();
