#!/usr/bin/env python3
"""Add Pinterest data to 60-day calendar modal"""

import re
from pathlib import Path

def extract_pinterest_data(captions_path):
    """Extract Pinterest title, description, and board from captions.md"""
    try:
        content = captions_path.read_text()
        
        title_match = re.search(r'\*\*Title:\*\* (.+)', content)
        desc_match = re.search(r'\*\*Description:\*\* (.+)', content)
        board_match = re.search(r'\*\*Board:\*\* (.+)', content)
        
        return {
            'title': title_match.group(1).replace('"', '\\"') if title_match else '',
            'description': desc_match.group(1).replace('"', '\\"') if desc_match else '',
            'board': board_match.group(1).replace('"', '\\"') if board_match else ''
        }
    except:
        return None

def get_day_folder_mapping():
    """Map day numbers to folder names"""
    content_dir = Path('/Users/aramide/clawd/SU/content')
    mapping = {}
    
    for folder in content_dir.iterdir():
        if folder.is_dir() and folder.name.startswith('day-'):
            match = re.match(r'day-(\d+)', folder.name)
            if match:
                day_num = int(match.group(1))
                captions = folder / 'captions.md'
                if captions.exists():
                    mapping[day_num] = captions
    
    return mapping

def main():
    calendar_path = Path('/Users/aramide/clawd/SU/calendar-60day.html')
    content = calendar_path.read_text()
    
    day_mapping = get_day_folder_mapping()
    
    # Add Pinterest fields to dayData entries
    for day_num in range(1, 61):
        if day_num in day_mapping:
            data = extract_pinterest_data(day_mapping[day_num])
            if data and data['title']:
                # Find the dayData entry and add Pinterest fields
                # Look for the tiktokCaption line for this day and add after it
                pattern = rf'(\s+{day_num}: \{{[^}}]+tiktokCaption: "[^"]*")\s*\}}'
                
                replacement = rf'\1,\n        pinterestTitle: "{data["title"]}",\n        pinterestDesc: "{data["description"]}",\n        pinterestBoard: "{data["board"]}"\n      }}'
                
                if f'pinterestTitle' not in content or f'{day_num}: {{' not in content.split('pinterestTitle')[0][-200:]:
                    new_content = re.sub(pattern, replacement, content)
                    if new_content != content:
                        content = new_content
                        print(f"✓ Added Pinterest data for Day {day_num}")
    
    # Add Pinterest section to modal HTML
    pinterest_modal_section = '''
          <!-- Pinterest Section -->
          <div class="modal-section pinterest-section">
            <h3>📌 Pinterest</h3>
            <div class="pinterest-fields">
              <div class="pinterest-field">
                <label>Title:</label>
                <span id="modal-pinterest-title"></span>
                <button class="copy-btn small" onclick="copyText('modal-pinterest-title')">📋</button>
              </div>
              <div class="pinterest-field">
                <label>Description:</label>
                <span id="modal-pinterest-desc"></span>
                <button class="copy-btn small" onclick="copyText('modal-pinterest-desc')">📋</button>
              </div>
              <div class="pinterest-field">
                <label>Board:</label>
                <span id="modal-pinterest-board"></span>
              </div>
            </div>
          </div>'''
    
    # Insert Pinterest section after TikTok section in modal
    if 'modal-pinterest-title' not in content:
        content = content.replace(
            '</div>\n          </div>\n\n          <div class="modal-actions">',
            f'</div>\n          </div>\n{pinterest_modal_section}\n\n          <div class="modal-actions">'
        )
        print("✓ Added Pinterest modal section")
    
    # Add CSS for Pinterest section
    pinterest_css = '''
    .pinterest-section {
      background: rgba(230, 60, 60, 0.1);
      border: 1px solid rgba(230, 60, 60, 0.3);
    }
    .pinterest-section h3 {
      color: #E63C3C !important;
    }
    .pinterest-fields {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .pinterest-field {
      display: flex;
      flex-wrap: wrap;
      align-items: flex-start;
      gap: 8px;
    }
    .pinterest-field label {
      color: #E8B86D;
      font-weight: 600;
      font-size: 12px;
      min-width: 80px;
    }
    .pinterest-field span {
      flex: 1;
      font-size: 13px;
      color: #ccc;
      line-height: 1.4;
    }
    .copy-btn.small {
      padding: 4px 8px;
      font-size: 11px;
      background: rgba(74, 144, 164, 0.3);
      border: none;
      border-radius: 4px;
      cursor: pointer;
      color: white;
    }
    .copy-btn.small:hover {
      background: rgba(74, 144, 164, 0.5);
    }
'''
    
    if '.pinterest-section {' not in content:
        content = content.replace('.modal-actions {', pinterest_css + '\n    .modal-actions {')
        print("✓ Added Pinterest CSS")
    
    # Add JavaScript to populate Pinterest fields
    pinterest_js = '''
      // Pinterest fields
      if (data.pinterestTitle) {
        document.getElementById('modal-pinterest-title').textContent = data.pinterestTitle;
        document.getElementById('modal-pinterest-desc').textContent = data.pinterestDesc;
        document.getElementById('modal-pinterest-board').textContent = data.pinterestBoard;
        document.querySelector('.pinterest-section').style.display = 'block';
      } else {
        document.querySelector('.pinterest-section').style.display = 'none';
      }
'''
    
    if 'modal-pinterest-title' not in content.split('function openDay')[1][:2000]:
        content = content.replace(
            "document.getElementById('modal-captions-link').href = `content/${data.folder}/captions.md`;",
            f"document.getElementById('modal-captions-link').href = `content/${{data.folder}}/captions.md`;\n{pinterest_js}"
        )
        print("✓ Added Pinterest JS")
    
    # Add copyText function if not present
    copy_text_fn = '''
    function copyText(elementId) {
      const text = document.getElementById(elementId).textContent.trim();
      navigator.clipboard.writeText(text).then(() => {
        showToast('✓ Copied!');
      });
    }
'''
    
    if 'function copyText' not in content:
        content = content.replace('function showToast', copy_text_fn + '\n    function showToast')
        print("✓ Added copyText function")
    
    calendar_path.write_text(content)
    print("\nDone! 60-day calendar updated with Pinterest sections.")

if __name__ == '__main__':
    main()
