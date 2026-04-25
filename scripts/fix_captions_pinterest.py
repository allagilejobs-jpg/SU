#!/usr/bin/env python3
"""Fix captions.md files with 'Character count:' Pinterest titles"""

import re
from pathlib import Path

def fix_caption_file(filepath):
    """Fix a single captions.md file"""
    content = filepath.read_text()
    
    if 'Title:** Character count:' not in content:
        return False
    
    # Extract topic from the file
    topic_match = re.search(r'\*\*Topic\*\*\s*\n\*\*(.+?)\*\*', content)
    if not topic_match:
        # Try alternate format
        topic_match = re.search(r'### Topic\s*\n\*\*(.+?)\*\*', content)
    if not topic_match:
        # Try getting title from first heading
        topic_match = re.search(r'^# (.+)', content, re.MULTILINE)
    
    if not topic_match:
        print(f"  ⚠ Could not find topic in {filepath.parent.name}")
        return False
    
    topic = topic_match.group(1).strip()
    
    # Extract hook if available for description
    hook_match = re.search(r'### Hook\s*\n["\']?(.+?)["\']?\s*\n', content)
    hook = hook_match.group(1).strip('"\'') if hook_match else ''
    
    # Generate proper title (clean up topic)
    title = topic
    
    # Generate description from hook or topic
    if hook:
        desc = f"{hook.rstrip('.')}. Save this guide for tips that actually work."
    else:
        desc = f"{topic}. Save this guide for practical tips for autism families."
    
    # Replace the bad title
    content = re.sub(
        r'\*\*Title:\*\* Character count:.*',
        f'**Title:** {title}',
        content
    )
    
    # Check if description also needs fixing
    if 'Description:** Save this guide for practical tips' in content and hook:
        content = re.sub(
            r'\*\*Description:\*\* Save this guide for practical tips.*',
            f'**Description:** {desc}',
            content
        )
    
    filepath.write_text(content)
    print(f"  ✓ Fixed: {filepath.parent.name} → {title[:40]}...")
    return True

def main():
    content_dir = Path('/Users/aramide/clawd/SU/content')
    fixed = 0
    
    for caption_file in content_dir.rglob('captions.md'):
        if fix_caption_file(caption_file):
            fixed += 1
    
    print(f"\nDone! Fixed {fixed} files.")

if __name__ == '__main__':
    main()
