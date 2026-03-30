const puppeteer = require('puppeteer');
const path = require('path');

(async () => {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  
  await page.goto('file://' + path.resolve('story-templates.html'), { waitUntil: 'networkidle0' });
  
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
    await page.evaluate((id) => {
      const el = document.getElementById(id);
      el.style.transform = 'none';
      el.style.marginBottom = '0';
    }, t.id);
    
    const element = await page.$('#' + t.id);
    await element.screenshot({ path: 'graphics/' + t.name, type: 'png' });
    console.log('✓', t.name);
  }
  
  await browser.close();
  console.log('\n✅ All 8 story templates exported!');
})();
