#!/usr/bin/env python3
"""Improve Pinterest descriptions by extracting real value from content."""

import os
import re
from pathlib import Path

# Custom descriptions for key posts (topic keyword -> better description)
DESCRIPTIONS = {
    'myths': "5 autism myths that need to die. These harmful misconceptions hurt autistic people every day. Learn the truth and share it.",
    'acceptance': "Acceptance means embracing autism as part of identity, not something to fix. Learn why acceptance matters more than awareness.",
    'glass child': "Siblings of special needs kids often become invisible. Here's how to support the 'glass child' in your family without guilt.",
    'sensory': "Simple sensory hacks that actually work for autistic kids. No expensive equipment needed. Save for those overwhelming moments.",
    'late diagnosis': "Got diagnosed as an adult? You're not alone. Here's what late diagnosis feels like and why it's never too late to understand yourself.",
    'burnout': "Autism parent burnout is real. Learn the warning signs and recovery strategies before you hit the wall. You can't pour from an empty cup.",
    'april': "April is Autism Acceptance Month. Here's how to celebrate and advocate all month long. Save this calendar of awareness days.",
    'waad': "World Autism Awareness Day is April 2nd. Here's how to celebrate autistic people, not pity them. Light it up gold, not blue.",
    'aba': "ABA therapy: what parents need to know. The good, the bad, and how to find ethical providers. An honest guide.",
    'visual': "Visual supports help autistic kids thrive. From schedules to social stories, here are tools that actually work. Free printables inside!",
    'meltdown': "Meltdowns aren't tantrums. Learn the difference and exactly what to do (and what NOT to do) to help your child. Must-save guide.",
    'feeding': "Autism and picky eating: it's not just being difficult. Understand the sensory reasons and strategies that actually help expand foods.",
    'sleep': "Autism and sleep struggles go hand in hand. Here are evidence-based strategies to help your whole family rest better.",
    'girls': "Autism looks different in girls. Here's why they're missed and what to look for. Share this, it might change a life.",
    'community': "Finding your autism parent tribe. Where to connect with people who truly get it without judgment. You're not alone.",
    'potty': "Potty training an autistic child takes longer, and that's okay. Here's a sensory-friendly approach with zero pressure.",
    'audhd': "ADHD + Autism together (AuDHD) is more common than you think. Here's what this combo looks like and why it's so exhausting.",
    'aac': "AAC devices give non-speaking kids a voice. Here's what parents need to know about communication alternatives. Game-changing info.",
    'accommodations': "Accommodations aren't giving kids an unfair advantage. They level the playing field. Save this list for your next school meeting.",
    'anxiety': "Anxiety and autism often come together. Here's how to recognize it and support your child without making it worse.",
    'respite': "You need a break. Yes, you. Here's how to get respite care without guilt. Your well-being matters too.",
    'teens': "Parenting autistic teens brings new challenges. Puberty, independence, social pressure. Here's how to navigate it together.",
    'nature': "Nature therapy for autistic kids. Why outdoor time is especially powerful and how to make it work. Free, effective, accessible.",
    'friendships': "Helping autistic kids build real friendships. Scripts, strategies, and how to support without taking over.",
    'siblings': "Supporting siblings of autistic children. They need attention too. Here's how to make sure no one becomes invisible.",
    'transition': "Transitioning from school to adulthood with autism. Start planning early. Here's what you need to know at every age.",
    'summer': "Summer break with an autistic child. Routines change, but prep helps. Here's how to make it work for everyone.",
    'therapy ot': "Occupational therapy for autism: what it actually does and how to tell if it's working. Parent's guide to OT.",
    'speech': "Speech therapy for autism isn't just about talking. Here's what SLPs actually work on and questions to ask your provider.",
    'insurance': "Getting insurance to cover autism therapy. Tips, scripts, and strategies from parents who've been there. Don't give up.",
    'marriage': "Autism parenting tests marriages. Here's how to stay connected when all your energy goes to your kids.",
    'self-care': "Self-care for autism parents isn't selfish. It's survival. Quick resets you can do in 5 minutes or less.",
    'camps': "Summer camps for autistic kids. What to look for, questions to ask, and red flags to avoid. Start planning now.",
    'travel': "Traveling with an autistic child. Airport hacks, hotel tips, and how to prep for the unexpected. Yes, you can do this.",
    'independence': "Building independence in autistic kids. Age-appropriate skills and how to teach them without overwhelming anyone.",
    'sensory deep': "Deep dive into sensory processing. Understand seeking vs avoiding, and how to create a sensory-friendly environment.",
    'executive function': "Executive function and autism. Why simple tasks feel impossible and strategies that actually help. Save this.",
    'technology': "Technology and autism. How to use screens as tools, not just pacifiers. Apps, settings, and balance tips.",
    'employment': "Employment for autistic adults. Finding jobs that fit, disclosure decisions, and workplace accommodations that help.",
    'self-advocacy': "Teaching autistic kids to self-advocate. Scripts, practice, and building confidence to speak up for their needs.",
    'mental health': "Mental health and autism. Recognizing depression and anxiety when communication is different. Signs to watch for.",
    'joy': "Autistic joy is real and beautiful. Celebrating special interests, stims, and the unique ways autistic people experience happiness.",
}

def get_better_description(topic, hook, default):
    """Get an improved description based on topic keywords."""
    topic_lower = topic.lower()
    
    for keyword, desc in DESCRIPTIONS.items():
        if keyword in topic_lower:
            return desc
    
    # If we have a good hook, use it as part of description
    if hook and len(hook) > 10:
        return f"{hook.rstrip('.')}. Save this guide for tips that actually work."
    
    return default

def process_file(filepath):
    """Improve the Pinterest description in a captions file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Skip if no Pinterest section
    if '## 📌 Pinterest' not in content:
        return False
    
    # Extract current values
    topic_match = re.search(r'\*\*Topic\*\*\s*\n\*\*(.+?)\*\*', content)
    topic = topic_match.group(1) if topic_match else ''
    
    hook_match = re.search(r'### Hook\s*\n["\']?(.+?)["\']?\s*\n', content)
    hook = hook_match.group(1).strip('"\'') if hook_match else ''
    
    desc_match = re.search(r'\*\*Description:\*\* (.+?)\n', content)
    if not desc_match:
        return False
    
    current_desc = desc_match.group(1)
    
    # Only update generic descriptions
    if 'Save this guide for practical tips' not in current_desc:
        return False
    
    new_desc = get_better_description(topic, hook, current_desc)
    
    if new_desc == current_desc:
        return False
    
    new_content = content.replace(
        f'**Description:** {current_desc}',
        f'**Description:** {new_desc}'
    )
    
    with open(filepath, 'w') as f:
        f.write(new_content)
    
    return True

def main():
    content_dir = Path('/Users/aramide/clawd/SU/content')
    updated = 0
    
    for caption_file in sorted(content_dir.rglob('captions.md')):
        if process_file(caption_file):
            print(f"✓ Improved: {caption_file.parent.name}")
            updated += 1
    
    print(f"\nDone! Improved {updated} descriptions")

if __name__ == '__main__':
    main()
