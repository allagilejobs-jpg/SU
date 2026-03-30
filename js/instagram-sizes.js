// Instagram Size Presets 2026
const IG_SIZES = {
  // Feed Posts
  portrait: {
    name: 'Portrait (4:5)',
    width: 1080,
    height: 1350,
    previewWidth: 270,
    previewHeight: 337,
    recommended: true,
    type: 'post'
  },
  tall: {
    name: 'Tall (3:4)',
    width: 1080,
    height: 1440,
    previewWidth: 270,
    previewHeight: 360,
    recommended: true,
    type: 'post'
  },
  square: {
    name: 'Square (1:1)',
    width: 1080,
    height: 1080,
    previewWidth: 270,
    previewHeight: 270,
    type: 'post'
  },
  landscape: {
    name: 'Landscape (1.91:1)',
    width: 1080,
    height: 566,
    previewWidth: 270,
    previewHeight: 141,
    type: 'post'
  },
  // Stories & Reels
  story: {
    name: 'Story/Reel (9:16)',
    width: 1080,
    height: 1920,
    previewWidth: 180,
    previewHeight: 320,
    safeHeight: 1440, // Keep text in this zone
    type: 'story'
  }
};

// Get size preset by key
function getSize(key) {
  return IG_SIZES[key] || IG_SIZES.portrait;
}

// Get scale factor for export (preview to full size)
function getScaleFactor(key) {
  const size = getSize(key);
  return size.width / size.previewWidth;
}

// Generate size selector HTML
function renderSizeSelector(selectedKey = 'portrait', onChange) {
  const container = document.createElement('div');
  container.className = 'size-selector';
  container.innerHTML = `
    <label style="font-size:12px;color:#E8B86D;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;display:block;">
      📐 Image Size
    </label>
    <select id="sizeSelect" style="
      background:#0f3460;
      color:#eee;
      border:1px solid #4A90A4;
      border-radius:8px;
      padding:10px 15px;
      font-family:Poppins,sans-serif;
      font-size:14px;
      width:100%;
      cursor:pointer;
    ">
      <optgroup label="Feed Posts">
        <option value="portrait" ${selectedKey === 'portrait' ? 'selected' : ''}>Portrait — 1080×1350 (4:5) ⭐</option>
        <option value="tall" ${selectedKey === 'tall' ? 'selected' : ''}>Tall — 1080×1440 (3:4) ⭐</option>
        <option value="square" ${selectedKey === 'square' ? 'selected' : ''}>Square — 1080×1080 (1:1)</option>
        <option value="landscape" ${selectedKey === 'landscape' ? 'selected' : ''}>Landscape — 1080×566 (1.91:1)</option>
      </optgroup>
      <optgroup label="Stories & Reels">
        <option value="story" ${selectedKey === 'story' ? 'selected' : ''}>Story/Reel — 1080×1920 (9:16)</option>
      </optgroup>
    </select>
    <p style="font-size:11px;color:#888;margin-top:8px;">
      ⭐ Portrait & Tall get best engagement
    </p>
  `;
  
  if (onChange) {
    container.querySelector('select').addEventListener('change', (e) => onChange(e.target.value));
  }
  
  return container;
}

// Apply size to element
function applySize(element, sizeKey) {
  const size = getSize(sizeKey);
  element.style.width = size.previewWidth + 'px';
  element.style.height = size.previewHeight + 'px';
}

// Export with correct size
async function exportWithSize(element, sizeKey, filename) {
  const size = getSize(sizeKey);
  const scale = size.width / element.offsetWidth;
  
  const canvas = await html2canvas(element, {
    scale: scale,
    useCORS: true,
    allowTaint: true,
    backgroundColor: null,
    width: element.offsetWidth,
    height: element.offsetHeight
  });
  
  const link = document.createElement('a');
  link.download = filename || `spectrum-unlocked-${sizeKey}.png`;
  link.href = canvas.toDataURL('image/png');
  link.click();
  
  return canvas;
}

// Export to window for use in HTML files
if (typeof window !== 'undefined') {
  window.IG_SIZES = IG_SIZES;
  window.getSize = getSize;
  window.getScaleFactor = getScaleFactor;
  window.renderSizeSelector = renderSizeSelector;
  window.applySize = applySize;
  window.exportWithSize = exportWithSize;
}
