#!/usr/bin/env python3
"""Add Pinterest caption tabs to calendar-30day.html"""

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
            'title': title_match.group(1) if title_match else '',
            'description': desc_match.group(1) if desc_match else '',
            'board': board_match.group(1) if board_match else ''
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

def generate_pinterest_section(day_num, data):
    """Generate HTML for Pinterest caption section"""
    if not data:
        return ''
    
    return f'''
      <div class="pinterest-section" id="pinterest-d{day_num}">
        <h4>📌 Pinterest</h4>
        <div class="pinterest-field">
          <label>Title:</label>
          <span class="pinterest-title">{data['title']}</span>
          <button class="copy-btn small" onclick="copyText(this.previousElementSibling)">📋</button>
        </div>
        <div class="pinterest-field">
          <label>Description:</label>
          <span class="pinterest-desc">{data['description']}</span>
          <button class="copy-btn small" onclick="copyText(this.previousElementSibling)">📋</button>
        </div>
        <div class="pinterest-field">
          <label>Board:</label>
          <span class="pinterest-board">{data['board']}</span>
        </div>
      </div>'''

def main():
    calendar_path = Path('/Users/aramide/clawd/SU/calendar-30day.html')
    content = calendar_path.read_text()
    
    # Get day folder mapping
    day_mapping = get_day_folder_mapping()
    
    # Add CSS for Pinterest sections
    pinterest_css = '''
    .pinterest-section {
      margin-top: 15px;
      padding: 15px;
      background: rgba(230, 60, 60, 0.1);
      border: 1px solid rgba(230, 60, 60, 0.3);
      border-radius: 10px;
    }
    .pinterest-section h4 {
      color: #E63C3C;
      margin-bottom: 12px;
      font-size: 14px;
    }
    .pinterest-field {
      margin-bottom: 10px;
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
    }
'''
    
    # Insert CSS before </style>
    if pinterest_css not in content:
        content = content.replace('</style>', pinterest_css + '\n  </style>')
    
    # Add copyText function if not present
    copy_text_js = '''
  function copyText(element) {
    navigator.clipboard.writeText(element.textContent.trim()).then(() => {
      showToast('✓ Copied!');
    });
  }
'''
    if 'function copyText' not in content:
        content = content.replace('function copyCaption', copy_text_js + '\n  function copyCaption')
    
    # Add Pinterest sections after each caption-box
    for day_num in range(1, 31):
        if day_num in day_mapping:
            data = extract_pinterest_data(day_mapping[day_num])
            if data and data['title']:
                pinterest_html = generate_pinterest_section(day_num, data)
                
                # Find the create-links div for this day and insert Pinterest section before it
                pattern = rf'(<div class="create-links">[\s\S]*?day={day_num}[\s\S]*?</div>)'
                match = re.search(pattern, content)
                
                if match and f'id="pinterest-d{day_num}"' not in content:
                    # Insert after caption-box, before create-links
                    old_text = match.group(1)
                    new_text = pinterest_html + '\n      ' + old_text
                    content = content.replace(old_text, new_text, 1)
                    print(f"✓ Added Pinterest section for Day {day_num}")
    
    calendar_path.write_text(content)
    print("\nDone! Calendar updated with Pinterest sections.")

if __name__ == '__main__':
    main()
