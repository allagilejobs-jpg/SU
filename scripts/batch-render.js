#!/usr/bin/env node
/**
 * Batch Playwright renderer.
 * Reuses one browser instance across all files — orders of magnitude faster
 * than spawning npx-per-file.
 *
 * Usage:
 *   node scripts/batch-render.js                        # render every .html that has a sibling .png
 *   node scripts/batch-render.js path/to/file.html ...  # render specific files
 *   node scripts/batch-render.js --manifest scripts/migration-manifest.txt
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const REPO_ROOT = path.resolve(__dirname, '..');

function detectSize(html) {
  const match = html.match(/body\s*\{[^}]*?width:\s*(\d+)px;\s*height:\s*(\d+)px/);
  if (match) return { width: parseInt(match[1], 10), height: parseInt(match[2], 10) };
  return { width: 1080, height: 1350 };
}

function fileUrl(p) {
  const resolved = path.resolve(p);
  // Windows: file:///C:/... with forward slashes.
  return 'file:///' + resolved.replace(/\\/g, '/');
}

async function main() {
  const args = process.argv.slice(2);
  let manifestPath = null;
  const explicitFiles = [];

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--manifest') {
      manifestPath = args[++i];
    } else {
      explicitFiles.push(args[i]);
    }
  }

  let targets = [];
  if (manifestPath) {
    const lines = fs.readFileSync(manifestPath, 'utf-8').split(/\r?\n/).filter(Boolean);
    targets = lines.map(line => path.join(REPO_ROOT, line));
  } else if (explicitFiles.length > 0) {
    targets = explicitFiles.map(f => path.resolve(f));
  } else {
    console.error('No targets. Pass files or --manifest <path>.');
    process.exit(1);
  }

  console.log(`Rendering ${targets.length} HTML file(s)…`);

  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  let ok = 0, failed = 0;
  const start = Date.now();

  for (let i = 0; i < targets.length; i++) {
    const htmlPath = targets[i];
    if (!fs.existsSync(htmlPath)) {
      console.warn(`  [skip] missing: ${htmlPath}`);
      failed++;
      continue;
    }

    try {
      const html = fs.readFileSync(htmlPath, 'utf-8');
      const { width, height } = detectSize(html);

      await page.setViewportSize({ width, height });
      await page.goto(fileUrl(htmlPath), { waitUntil: 'networkidle', timeout: 30000 });
      // Slight settle for web fonts.
      await page.waitForTimeout(150);

      const pngPath = htmlPath.replace(/\.html$/i, '.png');
      await page.screenshot({ path: pngPath, fullPage: false, clip: { x: 0, y: 0, width, height } });

      ok++;
      if ((i + 1) % 25 === 0 || i === targets.length - 1) {
        const elapsed = ((Date.now() - start) / 1000).toFixed(1);
        const rate = ((i + 1) / parseFloat(elapsed)).toFixed(2);
        console.log(`  [${i + 1}/${targets.length}] ${ok} ok / ${failed} failed · ${elapsed}s · ${rate}/s`);
      }
    } catch (err) {
      failed++;
      console.warn(`  [fail] ${path.relative(REPO_ROOT, htmlPath)} — ${err.message}`);
    }
  }

  await browser.close();

  const total = ((Date.now() - start) / 1000).toFixed(1);
  console.log(`\nDone. ${ok} rendered, ${failed} failed. ${total}s total.`);
  process.exit(failed > 0 && ok === 0 ? 1 : 0);
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
