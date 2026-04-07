"""Generator for FJ personal posts. Run from this folder."""
import os, json

POSTS = [
    {
        "id": 1,
        "slug": "counting",
        "title": "The Counting",
        "template": "quote",
        "graphic_text": "He counts to 100 before breakfast.\nEvery morning. In the same order.\nIn the same rhythm.\nAnd I've stopped trying to interrupt it.",
        "caption": "FJ counts to 100 every morning before he'll eat breakfast. Same cadence. Same volume. Same spot on the kitchen floor.\n\nFor a while, I tried to redirect him. \"FJ, your eggs are ready.\" \"FJ, come sit down.\" He'd start over from 1 every time I interrupted.\n\nOne morning I just let him finish. 97, 98, 99, 100. He looked up, walked to the table, and ate.\n\nThat was the day I stopped seeing his routines as problems to solve and started seeing them as things that help him prepare for the world. He wasn't ignoring me. He was getting ready.\n\nIf your child has a routine that drives you crazy, try sitting with it for a week instead of fighting it. You might find out it's doing something important that you can't see.",
        "hashtags": "#AutismParent #AutismAcceptance #NeurodivergentKids #AutismLife",
        "reel_caption": "He counts to 100 before breakfast.\nI stopped fighting it. Here's what happened.\n#autismparent #autism #neurodivergentkids",
    },
    {
        "id": 2,
        "slug": "parking-lot",
        "title": "The Parking Lot",
        "template": "quote",
        "graphic_text": "I sat in the parking lot\nfor 20 minutes after\nthe evaluation.\n\nI didn't cry.\nI didn't call anyone.\nI just sat there.",
        "caption": "The day FJ was diagnosed, I drove to the parking lot of a grocery store I never go to and sat there.\n\nI didn't cry. I wasn't ready for that yet. I wasn't angry. I wasn't relieved. I was just still. Like my brain needed to buffer before it could process what I'd just heard.\n\nI looked at my phone. I almost Googled \"autism prognosis.\" I put it down. I almost called my mom. I put the phone down again.\n\nEventually I drove home. FJ was with his grandma. He ran to the door when I walked in, same as always. Same smile. Same kid.\n\nNothing had changed about him. Everything had changed about how I understood him.\n\nIf you're in that parking lot right now - metaphorically or literally - you don't have to do anything. You don't have to have a plan. You just have to get home.",
        "hashtags": "#AutismDiagnosis #AutismParent #YouAreNotAlone #AutismAcceptance",
        "reel_caption": "If you're in that parking lot right now...\nYou don't have to have a plan. You just have to get home.\n#autismdiagnosis #autismparent #youarenotalone",
    },
    {
        "id": 3,
        "slug": "birthday-party",
        "title": "The Birthday Party",
        "template": "content_box",
        "header": "The Birthday Party We Left After 12 Minutes",
        "graphic_text": "He covered his ears\nthe moment we walked in.\n\nI knew.\nBut I tried anyway.",
        "caption": "We got invited to a birthday party last month. I spent 30 minutes prepping FJ. Visual schedule. Social story. Noise-canceling headphones in the bag.\n\nWe walked in. Music was loud. Kids were screaming. Balloons were popping. FJ covered his ears immediately. I picked him up. \"Let's try for a few minutes.\"\n\nHe lasted 12 minutes. Most of it on my lap with his face in my chest. When another kid popped a balloon 3 feet from us, we were done.\n\nOn the drive home I felt the guilt hit. Why did I even try? Why can't he just enjoy a party? Why am I upset about something he doesn't even care about?\n\nThen I checked the rearview mirror. He was calm. Humming to himself. Looking out the window. He wasn't upset. I was.\n\nThe party wasn't a failure. My expectation was the failure. He told me exactly what he needed - less noise, less chaos, more space. I just wasn't listening at first.\n\nWe'll try again. Shorter. Quieter. On his terms.",
        "hashtags": "#SensoryOverload #AutismParent #AutismLife #SensoryProcessing",
        "reel_caption": "12 minutes. That's how long we lasted.\nThe party wasn't the failure. My expectations were.\n#autismparent #sensoryoverload #autismlife",
    },
    {
        "id": 4,
        "slug": "3am-google",
        "title": "The 3am Google Search",
        "template": "quote",
        "graphic_text": "At 3am I had 47 tabs open.\n\nHalf contradicted each other.\nA third were trying to sell me something.",
        "caption": "Three weeks after FJ's diagnosis, I was up at 3am with my phone under the covers so I wouldn't wake anyone.\n\n47 tabs open. ABA therapy pros and cons. Early intervention success rates. \"Will my autistic child ever talk?\" \"Autism prognosis level 2.\" Reddit threads. Medical studies I didn't understand. A $400 course promising breakthroughs.\n\nI felt worse with every tab I opened.\n\nHere's what I know now that I didn't know at 3am: the internet at midnight is not your friend. You can't tell the difference between good information and garbage when you're exhausted and terrified. And the algorithm feeds you more of whatever makes you anxious because anxious people keep clicking.\n\nI built spectrumunlocked.com so the next parent at 3am lands somewhere calm instead of somewhere that profits off their fear.\n\nIf you're reading this at 3am - close the tabs. Your child is the same person they'll be tomorrow morning. The research will wait. Go to sleep.",
        "hashtags": "#AutismDiagnosis #AutismParent #NewlyDiagnosed #AutismAcceptance",
        "reel_caption": "47 tabs open at 3am.\nThe internet at midnight is not your friend.\n#autismparent #autismdiagnosis #newlydiagnosed",
    },
    {
        "id": 5,
        "slug": "five-foods",
        "title": "The Five Foods",
        "template": "content_box",
        "header": "FJ's Entire Menu",
        "graphic_text": "Chicken nuggets.\nPlain pasta.\nGoldfish crackers.\nApplesauce.\nBanana.\n\nThat's it.\nThat's the whole list.",
        "caption": "FJ eats 5 foods. Not 5 categories. Five specific foods prepared in a specific way.\n\nChicken nuggets - one brand only. Plain pasta - no sauce, not even butter. Goldfish crackers - original flavor, don't even think about the pizza ones. Applesauce - one specific pouch brand. Banana - only if it has zero brown spots.\n\nFor months I tried to expand his diet. \"Just try one bite.\" He gagged. \"It tastes the same!\" It didn't to him. \"He'll eat when he's hungry enough.\" He didn't.\n\nThen his OT explained something that changed my perspective: for many autistic kids, food isn't just taste. It's texture, temperature, color, smell, and how it feels in their mouth all at once. A \"new food\" isn't just unfamiliar. It's a full sensory event that his nervous system treats as a threat.\n\nWe stopped the food battles. We keep his safe foods available. We put new foods on the table without pressure. Sometimes he touches them. Twice he licked something new. That's progress measured in months, not meals.\n\nIf your child eats 3 foods or 5 foods or 10 foods, they're eating. That's enough right now.",
        "hashtags": "#AutismPickyEating #AutismParent #SensoryProcessing #AutismLife",
        "reel_caption": "5 foods. That's FJ's entire menu.\nIf your kid eats anything, they're eating. That's enough.\n#autismparent #autismpickyeating #sensoryprocessing",
    },
    {
        "id": 6,
        "slug": "explanation",
        "title": "The Explanation",
        "template": "quote",
        "graphic_text": "My mom asked why he\ndoesn't look at her\nwhen she talks to him.\n\nI explained it for the third time.",
        "caption": "My mom loves FJ. She adores him. And she asks the same question every visit.\n\n\"Why won't he look at me?\"\n\nThe first time, I explained: eye contact is physically uncomfortable for many autistic people. He's not being rude. He's actually listening better when he's not forced to look at you.\n\nThe second time, I explained it again with more patience.\n\nThe third time, I was tired. And I said something I probably shouldn't have: \"Mom, if someone shined a flashlight in your eyes and said 'now concentrate,' could you? That's what eye contact feels like for him.\"\n\nShe hasn't asked again. And she's started talking to him while he plays instead of trying to get him to look up first. He responds more now.\n\nSometimes the people who love your child the most are the ones who need the most education. That's not because they don't care. It's because they grew up in a world that defined connection differently.\n\nBe patient with them. But also be clear.",
        "hashtags": "#AutismFamily #AutismParent #AutismAcceptance #AutismAwareness",
        "reel_caption": "\"Why won't he look at me?\"\nHere's what I told her the third time she asked.\n#autismfamily #autismparent #autismacceptance",
    },
    {
        "id": 7,
        "slug": "small-win",
        "title": "The Small Win",
        "template": "quote",
        "graphic_text": "He pointed at the dog today.\n\nJust pointed.\n\nAnd I almost cried\nin the middle of the sidewalk.",
        "caption": "If you don't live this life, you won't understand why I almost cried on a sidewalk because a 4-year-old pointed at a dog.\n\nPointing is a milestone most parents never think about. Their kid points at 9 months. At 12 months. At everything. It just happens.\n\nFJ didn't point. Not at 12 months. Not at 18. Not at 2. Not at 3. We worked on it in speech therapy for months. Hand-over-hand. Modeling. Pointing at everything ourselves until we looked ridiculous.\n\nToday, walking down the street, a dog passed us. FJ stopped. Extended his finger. Pointed. Looked at me. Looked back at the dog.\n\nThat's joint attention. That's him saying \"Dad, do you see what I see? Isn't that cool?\" That's connection.\n\nThe milestones that matter in our house aren't on any chart. They're the ones we fought for. And when they come, they hit differently because we know exactly what it took to get here.\n\nCelebrate the small wins. They're not small.",
        "hashtags": "#AutismParent #AutismWins #AutismAcceptance #CelebrateDifferences",
        "reel_caption": "He pointed at a dog. Just pointed.\nIf you know, you know. The small wins aren't small.\n#autismparent #autismwins #celebratedifferences",
    },
    {
        "id": 8,
        "slug": "target-meltdown",
        "title": "The Meltdown at Target",
        "template": "content_box",
        "header": "Aisle 7, Target, 4:47pm",
        "graphic_text": "He was on the floor.\nEveryone was staring.\n\nOne woman shook her head.\nAnother one said\n\"hang in there, dad.\"",
        "caption": "Aisle 7. Target. 4:47pm on a Tuesday.\n\nFJ was on the floor. Not screaming for a toy. Not throwing a tantrum because I said no. His nervous system hit a wall. The lights, the beeping registers, the intercom, the strangers - it all stacked up and his brain said \"done.\"\n\nI got on the floor with him. Didn't talk. Didn't pick him up. Just sat there.\n\nA woman walked past and shook her head. I saw it. I felt it. I used to let that destroy me.\n\nThen another woman, a few aisles over, caught my eye and said quietly: \"Hang in there, dad.\"\n\nFive words. No advice. No judgment. Just acknowledgment.\n\nI think about her a lot. I never got her name. But she taught me something: you don't need to fix it for someone. You just need to let them know you see them.\n\nIf you see a parent on the floor of Target with a screaming child, you have two choices. One costs you nothing and means everything.",
        "hashtags": "#AutismMeltdown #AutismParent #SensoryOverload #AutismAcceptance",
        "reel_caption": "Aisle 7. Target. 4:47pm.\nFive words from a stranger changed everything.\n#autismparent #autismmeltdown #sensoryoverload",
    },
    {
        "id": 9,
        "slug": "things-he-teaches",
        "title": "The Things He Teaches Me",
        "template": "quote",
        "graphic_text": "My 4-year-old\nis teaching me things\nno one else could.",
        "caption": "Things FJ has taught me this year:\n\nThat you can love something by lining it up perfectly instead of playing with it the way the box says you should.\n\nThat the world is louder than I ever realized, and the people who navigate it with sensitive nervous systems are braver than anyone gives them credit for.\n\nThat \"I love you\" doesn't always sound like words. Sometimes it sounds like counting to 100. Sometimes it looks like bringing me the same book for the 30th time because sharing it with me is his version of connection.\n\nThat progress isn't a straight line. Last week he used a new word. This week he stopped using it. Next month it might come back. That's not regression. That's how development actually works when you stop comparing it to a chart.\n\nThat I was measuring his life against a template that was never designed for him. And the life he's building - his way, on his timeline - is worth more than any version I imagined before I knew him.\n\nHe doesn't need to be more like other kids. I needed to be more like his dad.",
        "hashtags": "#AutismParent #AutismAcceptance #CelebrateDifferences #NeurodivergentKids",
        "reel_caption": "Things my 4-year-old has taught me this year.\nHe doesn't need to be more like other kids. I needed to be more like his dad.\n#autismparent #autismacceptance",
    },
    {
        "id": 10,
        "slug": "one-year-later",
        "title": "One Year Later",
        "template": "quote",
        "graphic_text": "One year since the diagnosis.\n\nHere's what I've learned.",
        "caption": "One year ago, FJ was diagnosed with autism at age 3. Here's what I've learned since then.\n\nThe diagnosis didn't change my son. It changed my understanding of him. Every confusing behavior suddenly had an explanation. The counting, the rigidity, the meltdowns - they weren't defiance. They were communication.\n\nThe systems aren't built for us. Insurance fights, therapy waitlists, IEP meetings where you're outnumbered - every step requires advocacy. Nobody hands you a roadmap. You build it yourself.\n\nOther parents are the best resource. Not the internet. Not the doctors. The parents who are 6 months ahead of you and willing to share what they learned. Find them. They'll save you months of confusion.\n\nSelf-care isn't optional. I burned out at month 4. Stopped sleeping. Stopped calling friends. Started resenting the therapy schedule. I had to learn that I can't pour from an empty cup, and that taking care of myself is part of taking care of him.\n\nAnd the biggest lesson: autism is not a tragedy. It's a different way of being human. My son is funny, brilliant, determined, and sees the world in ways I never would have noticed without him. The life I imagined for him before the diagnosis was smaller than the one he's actually living.\n\nThis is Spectrum Unlocked. I built it because I couldn't find what I needed. Everything on the site is free. If one parent finds it and feels less alone, that's enough.\n\nLink in bio.",
        "hashtags": "#AutismParent #AutismAcceptance #AutismDiagnosis #AutismJourney",
        "reel_caption": "One year since FJ's diagnosis.\n5 things I wish I knew that first day.\n#autismparent #autismdiagnosis #autismjourney",
    },
]

QUOTE_HTML = '''<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&family=Playfair+Display:wght@700;800;900&display=swap" rel="stylesheet">
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      width: 1080px; height: 1350px;
      font-family: 'Poppins', sans-serif; color: white;
      background: linear-gradient(165deg, #1a1a2e 0%, #16213e 40%, #0f3460 100%);
      display: flex; flex-direction: column; align-items: center; justify-content: center;
      text-align: center; padding: 90px 80px;
      position: relative; overflow: hidden;
    }}
    .bg-shape {{ position: absolute; border-radius: 50%; opacity: 0.07; }}
    .bg-shape-1 {{ width: 550px; height: 550px; background: #E8B86D; top: -180px; right: -180px; }}
    .bg-shape-2 {{ width: 400px; height: 400px; background: #4A90A4; bottom: -130px; left: -130px; }}
    .quote-mark {{
      font-family: 'Playfair Display', serif;
      font-size: 200px;
      color: #E8B86D;
      opacity: 0.4;
      line-height: 0.8;
      margin-bottom: 10px;
      position: relative; z-index: 1;
    }}
    .quote-text {{
      font-family: 'Playfair Display', serif;
      font-size: 56px;
      font-weight: 700;
      font-style: italic;
      line-height: 1.35;
      max-width: 920px;
      position: relative; z-index: 1;
      white-space: pre-line;
    }}
    .divider {{
      width: 100px; height: 3px;
      background: #E8B86D;
      margin: 50px auto 30px;
      opacity: 0.6;
      position: relative; z-index: 1;
    }}
    .attribution {{
      font-size: 22px;
      color: #4A90A4;
      font-weight: 600;
      letter-spacing: 2px;
      text-transform: uppercase;
      position: relative; z-index: 1;
    }}
    .footer {{ position: absolute; bottom: 40px; }}
    .handle {{ font-size: 22px; opacity: 0.55; font-weight: 600; }}
  </style>
</head>
<body>
  <div class="bg-shape bg-shape-1"></div>
  <div class="bg-shape bg-shape-2"></div>

  <div class="quote-mark">"</div>
  <div class="quote-text">{TEXT}</div>

  <div class="divider"></div>
  <div class="attribution">— FJ's Dad</div>

  <div class="footer"><div class="handle">@spectrum_unlocked</div></div>
</body>
</html>
'''

CONTENT_BOX_HTML = '''<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&family=Playfair+Display:wght@700;800;900&display=swap" rel="stylesheet">
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      width: 1080px; height: 1350px;
      font-family: 'Poppins', sans-serif; color: white;
      background: linear-gradient(165deg, #1a1a2e 0%, #16213e 40%, #0f3460 100%);
      display: flex; flex-direction: column; align-items: center; justify-content: center;
      text-align: center; padding: 70px;
      position: relative; overflow: hidden;
    }}
    .bg-shape {{ position: absolute; border-radius: 50%; opacity: 0.07; }}
    .bg-shape-1 {{ width: 550px; height: 550px; background: #E8B86D; top: -180px; right: -180px; }}
    .bg-shape-2 {{ width: 400px; height: 400px; background: #4A90A4; bottom: -130px; left: -130px; }}
    .container {{
      background: rgba(255,255,255,0.04);
      border: 2px solid rgba(232, 184, 109, 0.3);
      border-radius: 24px;
      padding: 60px 70px;
      max-width: 920px;
      position: relative; z-index: 1;
      backdrop-filter: blur(10px);
    }}
    .header {{
      background: linear-gradient(135deg, #E8B86D 0%, #d4a85d 100%);
      color: #1a1a2e;
      padding: 18px 35px;
      border-radius: 12px;
      font-family: 'Playfair Display', serif;
      font-size: 38px;
      font-weight: 800;
      margin-bottom: 50px;
      display: inline-block;
      line-height: 1.2;
    }}
    .body-text {{
      font-family: 'Playfair Display', serif;
      font-size: 48px;
      font-weight: 700;
      font-style: italic;
      line-height: 1.4;
      white-space: pre-line;
    }}
    .footer {{ position: absolute; bottom: 40px; }}
    .handle {{ font-size: 22px; opacity: 0.55; font-weight: 600; }}
  </style>
</head>
<body>
  <div class="bg-shape bg-shape-1"></div>
  <div class="bg-shape bg-shape-2"></div>

  <div class="container">
    <div class="header">{HEADER}</div>
    <div class="body-text">{TEXT}</div>
  </div>

  <div class="footer"><div class="handle">@spectrum_unlocked</div></div>
</body>
</html>
'''

CAPTIONS_TEMPLATE = '''# Personal Post {ID}: {TITLE}

**Template:** {TEMPLATE}
**Format:** Single image post (1080x1350)

---

## 📱 FEED CAPTION (Instagram Post)

{CAPTION}

{HASHTAGS}

---

## 🎬 REEL CAPTION (if posted as Reel)

{REEL_CAPTION}

---

## 🎨 Graphic Text

{GRAPHIC_TEXT}
'''

# Generate all posts
for post in POSTS:
    folder = f"post-{post['id']:02d}-{post['slug']}"
    os.makedirs(folder, exist_ok=True)

    # Generate slide HTML
    if post['template'] == 'quote':
        # Escape \n in graphic_text for HTML rendering
        text_html = post['graphic_text'].replace('"', '&quot;')
        html = QUOTE_HTML.format(TEXT=text_html)
    else:  # content_box
        text_html = post['graphic_text'].replace('"', '&quot;')
        header_html = post['header'].replace('"', '&quot;')
        html = CONTENT_BOX_HTML.format(HEADER=header_html, TEXT=text_html)

    with open(f"{folder}/slide-01.html", 'w', encoding='utf-8') as f:
        f.write(html)

    # Generate captions.md
    captions = CAPTIONS_TEMPLATE.format(
        ID=post['id'],
        TITLE=post['title'],
        TEMPLATE='Quote' if post['template'] == 'quote' else 'Content Box',
        CAPTION=post['caption'],
        HASHTAGS=post['hashtags'],
        REEL_CAPTION=post['reel_caption'],
        GRAPHIC_TEXT=post['graphic_text']
    )
    with open(f"{folder}/captions.md", 'w', encoding='utf-8') as f:
        f.write(captions)

    print(f"Generated: {folder}")

# Save data for personal.html page
with open('posts.json', 'w', encoding='utf-8') as f:
    json.dump(POSTS, f, indent=2)

print(f"\nDone. {len(POSTS)} posts generated.")
