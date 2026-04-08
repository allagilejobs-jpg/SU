import { chromium } from 'playwright';

const BASE = 'C:/Users/Solomon/Desktop/SU/content/curated';
const targets = [
  { html: `${BASE}/holly-peete/ending-slide.html`, out: `${BASE}/holly-peete/ending-slide.png` },
  { html: `${BASE}/ot-genasis/ending-slide.html`,  out: `${BASE}/ot-genasis/ending-slide.png`  },
  { html: `${BASE}/faith-evans/ending-slide.html`, out: `${BASE}/faith-evans/ending-slide.png` },
  { html: `${BASE}/dan-orlovsky-madden/ending-slide.html`, out: `${BASE}/dan-orlovsky-madden/ending-slide.png` },
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
  await page.waitForTimeout(800);
  await page.screenshot({ path: t.out, clip: { x: 0, y: 0, width: 1080, height: 1920 } });
  console.log('rendered ->', t.out);
  await ctx.close();
}
await browser.close();
