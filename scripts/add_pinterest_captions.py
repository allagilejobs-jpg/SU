#!/usr/bin/env python3
"""Add Pinterest sections to all captions.md files that don't have them."""

import os
import re
from pathlib import Path

# Board mapping based on content topics
BOARD_MAP = {
    'iep': 'IEP & School Advocacy',
    'school': 'IEP & School Advocacy',
    'education': 'IEP & School Advocacy',
    'meltdown': 'Meltdown Support',
    'sensory': 'Sensory Support & Hacks',
    'sleep': 'Autism & Sleep',
    'feeding': 'Feeding & Food Tips',
    'potty': 'Potty Training Tips',
    'communication': 'Communication & AAC',
    'aac': 'Communication & AAC',
    'masking': 'Understanding Autism',
    'burnout': 'Self-Care for Parents',
    'selfcare': 'Self-Care for Parents',
    'diagnosis': 'Newly Diagnosed',
    'myth': 'Autism Myths Debunked',
    'aba': 'Therapy Options',
    'therapy': 'Therapy Options',
    'girl': 'Autism in Girls',
    'women': 'Autism in Girls',
    'adult': 'Adult Autism',
    'late': 'Late Diagnosis',
    'audhd': 'ADHD & Autism',
    'adhd': 'ADHD & Autism',
    'visual': 'Visual Supports',
    'routine': 'Routines & Schedules',
    'sibling': 'Sibling Support',
    'glass': 'Sibling Support',
    'acceptance': 'Autism Acceptance',
    'awareness': 'Autism Acceptance',
    'community': 'Autism Community',
    'joy': 'Autistic Joy',
    'summer': 'Seasonal Tips',
    'holiday': 'Seasonal Tips',
}

def get_board(topic_lower):
    """Determine the best board based on topic keywords."""
    for keyword, board in BOARD_MAP.items():
        if keyword in topic_lower:
            return board
    return 'Autism Parenting Tips'

def extract_info(content):
    """Extract topic and hook from captions content."""
    topic_match = re.search(r'\*\*(.+?)\*\*', content)
    topic = topic_match.group(1) if topic_match else ''
    
    hook_match = re.search(r'### Hook\s*\n["\']?(.+?)["\']?\s*\n', content)
    hook = hook_match.group(1).strip('"\'') if hook_match else ''
    
    return topic, hook

def generate_pinterest_section(topic, hook, content):
    """Generate Pinterest title, description, and board."""
    topic_lower = topic.lower()
    
    # Generate title (under 100 chars, front-load value)
    title = topic
    if len(title) > 95:
        title = title[:92] + '...'
    
    # Generate description from hook + value prop (220-250 chars target)
    if hook:
        desc_start = hook.rstrip('.') + '. '
    else:
        desc_start = ''
    
    # Extract key value from Instagram caption
    ig_match = re.search(r'## 📸 Instagram Caption\s*\n\n(.+?)(?=\n\n---|\n\n#)', content, re.DOTALL)
    if ig_match:
        ig_text = ig_match.group(1)
        # Get first meaningful line
        lines = [l.strip() for l in ig_text.split('\n') if l.strip() and not l.startswith('#')]
        value_line = lines[1] if len(lines) > 1 else lines[0] if lines else ''
        value_line = re.sub(r'[✓✗❌✅🎧💬📚🤝💙💾📋⬇️]', '', value_line).strip()
    else:
        value_line = ''
    
    description = f"{desc_start}Save this guide for practical tips that actually work for autism families."
    
    # Keep under 250 chars
    if len(description) > 250:
        description = description[:247] + '...'
    
    board = get_board(topic_lower)
    
    return f"""---

## 📌 Pinterest

**Title:** {title}

**Description:** {description}

**Board:** Autism Parenting Tips / {board}

---"""

def process_file(filepath):
    """Add Pinterest section to a captions file if it doesn't have one."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Skip if already has Pinterest section
    if '## 📌 Pinterest' in content:
        return False
    
    topic, hook = extract_info(content)
    if not topic:
        print(f"  Skipping {filepath} - no topic found")
        return False
    
    pinterest_section = generate_pinterest_section(topic, hook, content)
    
    # Insert before Content Notes or at end
    if '## Content Notes' in content:
        new_content = content.replace('## Content Notes', f'{pinterest_section}\n\n## Content Notes')
    elif '## Files' in content:
        new_content = content.replace('## Files', f'{pinterest_section}\n\n## Files')
    elif '## Notes' in content:
        new_content = content.replace('## Notes', f'{pinterest_section}\n\n## Notes')
    else:
        new_content = content + '\n\n' + pinterest_section
    
    with open(filepath, 'w') as f:
        f.write(new_content)
    
    return True

def main():
    content_dir = Path('/Users/aramide/clawd/SU/content')
    updated = 0
    skipped = 0
    
    for caption_file in sorted(content_dir.rglob('captions.md')):
        print(f"Processing {caption_file.parent.name}...")
        if process_file(caption_file):
            updated += 1
            print(f"  ✓ Added Pinterest section")
        else:
            skipped += 1
    
    print(f"\nDone! Updated: {updated}, Skipped: {skipped}")

if __name__ == '__main__':
    main()
