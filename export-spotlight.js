const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1920, height: 3000 });
  
  await page.goto('file://' + path.resolve('spotlight-series.html'), { waitUntil: 'networkidle' });
  
  // Wait for content to render
  await page.waitForTimeout(1000);
  
  const posts = [
    { id: 'temple-grandin', type: 'icon' },
    { id: 'holly-robinson-peete', type: 'parent' },
    { id: 'greta-thunberg', type: 'icon' }
  ];
  
  for (const post of posts) {
    // Create the export version
    const data = await page.evaluate((postId) => {
      const icons = [
        { id: 'temple-grandin', name: 'Temple Grandin', title: 'Scientist, Author & Autism Advocate', emoji: '🧬', quote: '"Different, not less."' },
        { id: 'greta-thunberg', name: 'Greta Thunberg', title: 'Climate Activist', emoji: '🌍', quote: '"Being different is a superpower."' }
      ];
      const parents = [
        { id: 'holly-robinson-peete', name: 'Holly Robinson Peete', title: 'Actress & Autism Advocate', child: 'Son RJ', emoji: '💜', quote: '"RJ is my greatest teacher."' }
      ];
      return icons.find(i => i.id === postId) || parents.find(p => p.id === postId);
    }, post.id);
    
    // Create a standalone element for screenshot
    const themeClass = post.type === 'icon' ? 'icon-theme' : 'parent-theme';
    const badge = post.type === 'icon' ? '🌟 Spectrum Spotlight' : '💜 Autism Parent Spotlight';
    
    await page.evaluate(({ data, themeClass, badge }) => {
      const container = document.createElement('div');
      container.id = 'export-standalone';
      container.style.cssText = 'position: fixed; top: 0; left: 0; z-index: 9999;';
      container.innerHTML = `
        <div style="
          width: 1080px;
          height: 1080px;
          background: ${themeClass === 'icon-theme' ? 'linear-gradient(135deg, #4A90A4 0%, #2C5F6E 100%)' : 'linear-gradient(135deg, #9B59B6 0%, #8E44AD 100%)'};
          position: relative;
          font-family: 'Poppins', sans-serif;
          color: white;
        ">
          <span style="
            position: absolute;
            top: 60px;
            left: 60px;
            background: rgba(255,255,255,0.2);
            padding: 20px 40px;
            border-radius: 50px;
            font-size: 28px;
            font-weight: 700;
            letter-spacing: 3px;
            text-transform: uppercase;
          ">${badge}</span>
          <div style="
            position: absolute;
            top: 200px;
            left: 50%;
            transform: translateX(-50%);
          ">
            <div style="
              width: 300px;
              height: 300px;
              border-radius: 50%;
              background: rgba(255,255,255,0.15);
              border: 12px solid rgba(255,255,255,0.4);
              display: flex;
              align-items: center;
              justify-content: center;
              font-size: 120px;
            ">${data.emoji}</div>
          </div>
          <div style="
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(0,0,0,0.4);
            padding: 60px;
            text-align: center;
          ">
            <div style="
              font-family: 'Playfair Display', serif;
              font-size: 72px;
              font-weight: 700;
              margin-bottom: 15px;
            ">${data.name}</div>
            <div style="
              font-size: 28px;
              opacity: 0.8;
              text-transform: uppercase;
              letter-spacing: 4px;
              margin-bottom: 30px;
            ">${data.title}${data.child ? ' • ' + data.child : ''}</div>
            <div style="
              font-size: 36px;
              font-style: italic;
              line-height: 1.5;
              opacity: 0.95;
            ">${data.quote}</div>
          </div>
          <span style="
            position: absolute;
            bottom: 30px;
            right: 40px;
            font-size: 24px;
            opacity: 0.7;
          ">@spectrum_unlocked</span>
        </div>
      `;
      document.body.appendChild(container);
    }, { data, themeClass, badge });
    
    await page.waitForTimeout(200);
    
    const element = await page.$('#export-standalone > div');
    await element.screenshot({ path: `graphics/spotlight-${post.id}.png`, type: 'png' });
    console.log('✓', post.id);
    
    await page.evaluate(() => {
      document.getElementById('export-standalone').remove();
    });
  }
  
  await browser.close();
  console.log('\n✅ Exported 3 spotlight posts!');
})();
