"""Generate vertical reel slides (1080x1920) for the 3 personal post reels."""
import os

REELS = [
    {
        "folder": "post-02-parking-lot-reel",
        "slides": [
            ("hook",      3.0, "label", "A True Story",       "The day my son was diagnosed", "with autism"),
            ("scene",     4.0, "scene", None,                 "I drove to a grocery store I never go to.", None),
            ("sit",       4.0, "scene", None,                 "And I sat in the parking lot for 20 minutes.", None),
            ("nothing",   5.0, "list",  "I didn't cry.",      "I didn't call anyone.", "I just sat there."),
            ("kid",       5.0, "scene", None,                 "Eventually I drove home.", "He ran to the door. Same smile. Same kid."),
            ("reframe",   6.0, "quote", None,                 "Nothing had changed about him.", "Everything had changed about how I understood him."),
            ("cta",       5.0, "cta",   "If you're there now",  "You don't have to have a plan.", "You just have to get home."),
        ],
    },
    {
        "folder": "post-08-target-meltdown-reel",
        "slides": [
            ("hook",      3.0, "label", "A True Story",       "Aisle 7. Target.",            "4:47pm on a Tuesday."),
            ("scene",     4.0, "scene", None,                 "My son was on the floor.",     "Not a tantrum. A meltdown."),
            ("why",       5.0, "scene", None,                 "His nervous system hit a wall.", "Lights, beeping, intercom, strangers."),
            ("with",      5.0, "scene", None,                 "I got on the floor with him.", "Didn't talk. Didn't pick him up."),
            ("judge",     5.0, "scene", None,                 "A woman walked past.",         "She shook her head. I felt it."),
            ("kindness",  5.0, "scene", None,                 "Then another woman caught my eye.", "She said five quiet words..."),
            ("words",     5.0, "quote", None,                 '"Hang in there, dad."',        None),
            ("lesson",    5.0, "cta",   "Five words",         "No advice. No judgment.",      "Just acknowledgment. It meant everything."),
        ],
    },
    {
        "folder": "post-10-one-year-later-reel",
        "slides": [
            ("hook",      3.0, "label", "One Year Later",     "My son was diagnosed",         "with autism at age 3."),
            ("intro",     3.5, "scene", None,                 "Here's what I learned.",       None),
            ("lesson1",   5.0, "list",  "Lesson 1",           "The diagnosis didn't change him.", "It changed how I understood him."),
            ("lesson2",   5.0, "list",  "Lesson 2",           "The systems aren't built for us.", "Every step requires advocacy."),
            ("lesson3",   5.0, "list",  "Lesson 3",           "Other parents are the best resource.", "Not the internet. Find them."),
            ("lesson4",   5.0, "list",  "Lesson 4",           "Self-care isn't optional.",    "I burned out at month 4."),
            ("lesson5",   6.0, "list",  "Lesson 5",           "Autism is not a tragedy.",     "It's a different way of being human."),
            ("cta",       5.0, "cta",   "Spectrum Unlocked",  "Built for the parent at 3am.", "Link in bio. Everything is free."),
        ],
    },
]

# Slide templates
HEAD = '''<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800;900&family=Playfair+Display:wght@700;800;900&display=swap" rel="stylesheet">
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      width: 1080px; height: 1920px;
      font-family: 'Poppins', sans-serif; color: white;
      background: linear-gradient(165deg, #0a0a15 0%, #16213e 40%, #0f3460 100%);
      display: flex; flex-direction: column; align-items: center; justify-content: center;
      text-align: center; padding: 100px 70px;
      position: relative; overflow: hidden;
    }}
    body::before {{ content: ''; position: absolute; top: -150px; right: -150px; width: 400px; height: 400px; background: #E8B86D; border-radius: 50%; opacity: 0.07; }}
    body::after {{ content: ''; position: absolute; bottom: -100px; left: -100px; width: 350px; height: 350px; background: #4A90A4; border-radius: 50%; opacity: 0.07; }}
    .label {{ font-size: 24px; font-weight: 700; color: #4A90A4; text-transform: uppercase; letter-spacing: 4px; margin-bottom: 50px; position: relative; z-index: 1; }}
    .main-text {{ font-family: 'Playfair Display', serif; font-size: 80px; font-weight: 800; line-height: 1.15; max-width: 950px; position: relative; z-index: 1; }}
    .main-text .em {{ color: #E8B86D; font-style: italic; }}
    .sub-text {{ font-family: 'Playfair Display', serif; font-size: 56px; font-weight: 700; font-style: italic; line-height: 1.3; max-width: 950px; opacity: 0.9; margin-top: 35px; position: relative; z-index: 1; }}
    .quote-mark {{ font-family: 'Playfair Display', serif; font-size: 200px; color: #E8B86D; opacity: 0.4; line-height: 0.6; margin-bottom: 20px; position: relative; z-index: 1; }}
    .footer {{ position: absolute; bottom: 60px; }}
    .handle {{ font-size: 24px; opacity: 0.5; font-weight: 600; }}
  </style>
</head>
<body>
'''

FOOT = '''
  <div class="footer"><div class="handle">@spectrum_unlocked</div></div>
</body>
</html>
'''

def make_slide(slide_type, label, line1, line2):
    parts = [HEAD]
    if label:
        parts.append(f'  <div class="label">{label}</div>\n')

    if slide_type == "label":
        parts.append(f'  <div class="main-text">{line1}<br>{line2}</div>\n')
    elif slide_type == "scene":
        if line2:
            parts.append(f'  <div class="main-text">{line1}</div>\n')
            parts.append(f'  <div class="sub-text">{line2}</div>\n')
        else:
            parts.append(f'  <div class="main-text">{line1}</div>\n')
    elif slide_type == "list":
        # Three short lines stacked
        if line2 and not label:
            parts.append(f'  <div class="main-text"><span class="em">{line1}</span><br>{line2}</div>\n')
        else:
            parts.append(f'  <div class="main-text">{line1}</div>\n')
            if line2:
                parts.append(f'  <div class="sub-text">{line2}</div>\n')
    elif slide_type == "quote":
        parts.append(f'  <div class="quote-mark">"</div>\n')
        parts.append(f'  <div class="main-text" style="font-style:italic;">{line1}</div>\n')
        if line2:
            parts.append(f'  <div class="sub-text">{line2}</div>\n')
    elif slide_type == "cta":
        parts.append(f'  <div class="main-text"><span class="em">{line1}</span></div>\n')
        if line2:
            parts.append(f'  <div class="sub-text">{line2}</div>\n')

    parts.append(FOOT)
    return ''.join(parts)


# For "label" slides, the label arg is in line1 of the tuple, line2 has the actual text
def write_slides():
    for reel in REELS:
        folder = reel["folder"]
        for i, (name, dur, stype, label_or_main, line1, line2) in enumerate(reel["slides"], 1):
            num = f"{i:02d}"
            # Restructure based on slide type
            if stype == "label":
                # label_or_main is the label, line1+line2 are the main text
                html = make_slide("label", label_or_main, line1, line2)
            elif stype == "list" and label_or_main:
                # label_or_main is the label, line1+line2 are content
                html = make_slide("scene", label_or_main, line1, line2)
            elif stype == "cta":
                html = make_slide("cta", None, label_or_main, line1 if line2 else None)
                # Restructure: label_or_main is the eyebrow, line1 main, line2 sub
                parts = [HEAD]
                parts.append(f'  <div class="label">{label_or_main}</div>\n')
                parts.append(f'  <div class="main-text"><span class="em">{line1}</span></div>\n')
                if line2:
                    parts.append(f'  <div class="sub-text">{line2}</div>\n')
                parts.append(FOOT)
                html = ''.join(parts)
            elif stype == "quote":
                parts = [HEAD]
                parts.append(f'  <div class="quote-mark">"</div>\n')
                parts.append(f'  <div class="main-text" style="font-style:italic;">{line1}</div>\n')
                if line2:
                    parts.append(f'  <div class="sub-text">{line2}</div>\n')
                parts.append(FOOT)
                html = ''.join(parts)
            else:  # scene
                parts = [HEAD]
                parts.append(f'  <div class="main-text">{line1}</div>\n')
                if line2:
                    parts.append(f'  <div class="sub-text">{line2}</div>\n')
                parts.append(FOOT)
                html = ''.join(parts)

            filepath = f"{folder}/slide-{num}-{name}.html"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"  {filepath}")
        print(f"Done: {folder}\n")

write_slides()
