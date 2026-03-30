const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  // Set viewport large enough
  await page.setViewportSize({ width: 1920, height: 3000 });
  
  await page.goto('file://' + path.resolve('story-templates.html'), { waitUntil: 'networkidle' });
  
  const templates = [
    { id: 'story-tip', name: 'story-quick-tip.png' },
    { id: 'story-poll', name: 'story-poll.png' },
    { id: 'story-newpost', name: 'story-new-post.png' },
    { id: 'story-quote', name: 'story-quote.png' },
    { id: 'story-thisorthat', name: 'story-this-or-that.png' },
    { id: 'story-bts', name: 'story-behind-scenes.png' },
    { id: 'story-reminder', name: 'story-reminder.png' },
    { id: 'story-link', name: 'story-link.png' }
  ];
  
  for (const t of templates) {
    // Reset transform and position for proper screenshot
    await page.evaluate((id) => {
      const el = document.getElementById(id);
      // Reset all transforms and positioning
      el.style.transform = 'none';
      el.style.marginBottom = '0';
      el.style.position = 'fixed';
      el.style.top = '0';
      el.style.left = '0';
      el.style.zIndex = '9999';
    }, t.id);
    
    // Wait a bit for render
    await page.waitForTimeout(100);
    
    const element = await page.$('#' + t.id);
    await element.screenshot({ path: 'graphics/' + t.name, type: 'png' });
    
    // Reset position
    await page.evaluate((id) => {
      const el = document.getElementById(id);
      el.style.position = '';
      el.style.top = '';
      el.style.left = '';
      el.style.zIndex = '';
      el.style.transform = 'scale(0.25)';
      el.style.marginBottom = '-1440px';
    }, t.id);
    
    console.log('✓', t.name);
  }
  
  await browser.close();
  console.log('\n✅ All 8 story templates exported!');
})();
