#!/usr/bin/env python3
"""Add Pinterest sections to 30-day calendar - FIXED version"""

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
            # Handle day-01, day-02, etc. but NOT day-01-tiktok-myths-reel
            match = re.match(r'day-(\d+)-[^-]', folder.name)
            if match:
                day_num = int(match.group(1))
                captions = folder / 'captions.md'
                if captions.exists() and day_num not in mapping:
                    mapping[day_num] = captions
    
    return mapping

def generate_pinterest_html(day_num, data):
    """Generate HTML for Pinterest caption section"""
    return f'''
      <div class="pinterest-caption">
        <h4>📌 Pinterest</h4>
        <div class="pinterest-field">
          <span class="field-label">Title:</span>
          <span class="field-value" id="pin-title-{day_num}">{data['title']}</span>
          <button class="copy-btn small" onclick="copyField('pin-title-{day_num}')">📋</button>
        </div>
        <div class="pinterest-field">
          <span class="field-label">Description:</span>
          <span class="field-value" id="pin-desc-{day_num}">{data['description']}</span>
          <button class="copy-btn small" onclick="copyField('pin-desc-{day_num}')">📋</button>
        </div>
        <div class="pinterest-field">
          <span class="field-label">Board:</span>
          <span class="field-value">{data['board']}</span>
        </div>
      </div>'''

def main():
    calendar_path = Path('/Users/aramide/clawd/SU/calendar-30day.html')
    content = calendar_path.read_text()
    
    day_mapping = get_day_folder_mapping()
    
    # Add CSS if not present
    pinterest_css = '''
    .pinterest-caption {
      margin-top: 15px;
      padding: 15px;
      background: rgba(230, 60, 60, 0.1);
      border: 1px solid rgba(230, 60, 60, 0.3);
      border-radius: 10px;
    }
    .pinterest-caption h4 {
      color: #E63C3C;
      margin-bottom: 12px;
      font-size: 14px;
    }
    .pinterest-field {
      display: flex;
      flex-wrap: wrap;
      align-items: flex-start;
      gap: 8px;
      margin-bottom: 10px;
    }
    .pinterest-field:last-child { margin-bottom: 0; }
    .field-label {
      color: #E8B86D;
      font-weight: 600;
      font-size: 12px;
      min-width: 80px;
    }
    .field-value {
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
      color: white;
      cursor: pointer;
    }
    .copy-btn.small:hover { background: rgba(74, 144, 164, 0.5); }
'''
    
    if '.pinterest-caption {' not in content:
        content = content.replace('</style>', pinterest_css + '\n  </style>')
        print("✓ Added Pinterest CSS")
    
    # Add copyField function
    copy_fn = '''
  function copyField(elementId) {
    const text = document.getElementById(elementId).textContent.trim();
    navigator.clipboard.writeText(text).then(() => {
      showToast('✓ Copied!');
    });
  }
'''
    if 'function copyField' not in content:
        content = content.replace('function copyCaption', copy_fn + '\n  function copyCaption')
        print("✓ Added copyField function")
    
    # Insert Pinterest sections for each day
    # Find each create-links div and insert Pinterest section BEFORE it
    for day_num in sorted(day_mapping.keys()):
        if day_num > 30:
            continue
            
        data = extract_pinterest_data(day_mapping[day_num])
        if not data or not data['title']:
            continue
        
        pinterest_html = generate_pinterest_html(day_num, data)
        
        # Find the create-links for this specific day
        # Pattern: <div class="create-links">..day=N..
        # We need to match the specific day
        
        # First, try exact day link pattern
        patterns = [
            rf'(<div class="create-links">\s*<a href="create\.html\?day={day_num}")',
            rf'(<div class="create-links"><a href="create\.html\?day={day_num}")',
        ]
        
        inserted = False
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                # Insert Pinterest section before create-links
                old_text = match.group(1)
                new_text = pinterest_html + '\n      ' + old_text
                content = content.replace(old_text, new_text, 1)
                print(f"✓ Added Pinterest for Day {day_num}")
                inserted = True
                break
        
        if not inserted:
            print(f"⚠ Could not find create-links for Day {day_num}")
    
    calendar_path.write_text(content)
    print("\nDone!")

if __name__ == '__main__':
    main()
