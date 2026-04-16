#!/usr/bin/env python3
"""Fix Pinterest titles that incorrectly show 'Character count:'"""

import re
from pathlib import Path

def get_pinterest_data(folder_path):
    """Extract Pinterest data from captions.md"""
    captions = folder_path / 'captions.md'
    if not captions.exists():
        return None
    
    content = captions.read_text()
    
    title_match = re.search(r'\*\*Title:\*\* (.+)', content)
    desc_match = re.search(r'\*\*Description:\*\* (.+)', content)
    board_match = re.search(r'\*\*Board:\*\* (.+)', content)
    
    if not title_match:
        return None
        
    return {
        'title': title_match.group(1).replace('"', '\\"'),
        'desc': desc_match.group(1).replace('"', '\\"') if desc_match else '',
        'board': board_match.group(1).replace('"', '\\"') if board_match else 'Autism Parenting Tips'
    }

def main():
    calendar_path = Path('/Users/aramide/clawd/SU/calendar-60day.html')
    content = calendar_path.read_text()
    content_dir = Path('/Users/aramide/clawd/SU/content')
    
    # Find all occurrences of "Character count:" title
    pattern = r'pinterestTitle: "Character count:"'
    
    # For each day, find its folder and get correct Pinterest data
    fixes = []
    
    # Days that need fixing (based on grep results)
    problem_days = [2, 10, 14, 17, 21, 24, 31, 35, 45, 52, 59]
    
    for day in problem_days:
        # Find the folder for this day
        for folder in content_dir.iterdir():
            if folder.is_dir() and folder.name.startswith(f'day-{day:02d}-') or folder.name.startswith(f'day-{day}-'):
                if 'reel' not in folder.name:
                    data = get_pinterest_data(folder)
                    if data:
                        fixes.append((day, folder.name, data))
                        break
    
    # Apply fixes
    for day, folder_name, data in fixes:
        # Find the dayData entry for this day and replace Pinterest fields
        # Pattern: look for the day entry and replace pinterestTitle: "Character count:"
        old_pattern = rf'({day}: \{{[^}}]+)pinterestTitle: "Character count:"'
        new_text = rf'\1pinterestTitle: "{data["title"]}"'
        
        new_content = re.sub(old_pattern, new_text, content, flags=re.DOTALL)
        if new_content != content:
            print(f"✓ Fixed Day {day}: {data['title'][:50]}...")
            content = new_content
    
    calendar_path.write_text(content)
    print(f"\nDone! Fixed Pinterest titles.")

if __name__ == '__main__':
    main()
