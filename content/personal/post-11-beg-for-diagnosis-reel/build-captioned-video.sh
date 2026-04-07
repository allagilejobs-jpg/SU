#!/bin/bash
# Build captioned video for Post 11

DIR="/Users/aramide/clawd/SU/content/personal/post-11-beg-for-diagnosis-reel"
VIDEO="/tmp/insta_post.mp4"
OUTPUT="$DIR/FINAL-captioned.mp4"

# Caption segments with timestamps (start, end, text)
CAPTIONS=(
  "0:4.5:What was it like for you, for those who may be experiencing that now,"
  "4.5:7.5:discovering that your child was autistic?"
  "7.5:13.5:By the time he was diagnosed, I was already aware something was wrong."
  "13.5:21:So it was me begging for a written diagnosis to access early intervention."
  "21:24.5:I had to beg for a written diagnosis."
  "24.5:31.5:Because by the time he was two, I'm like, my son should be talking."
  "31.5:35:I had three other kids before him."
  "35:41.5:And his doctor was like, just wait it out. Every kid is different."
  "41.5:45:But I still felt something wasn't right."
  "45:53.5:So I started on my own putting him in speech therapy and things I would look up."
  "53.5:60.5:Speech therapy, occupational therapy."
  "60.5:66.8:And to access early intervention, I needed a diagnosis before he was three."
)

echo "Building caption overlays..."

# Create caption images
for i in "${!CAPTIONS[@]}"; do
  IFS=':' read -r start end text <<< "${CAPTIONS[$i]}"
  num=$(printf "%02d" $i)
  
  cat > "$DIR/caption-$num.html" << EOF
<!DOCTYPE html>
<html>
<head>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600;700&display=swap" rel="stylesheet">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  width: 720px; height: 900px;
  background: #00ff00;
  font-family: 'Poppins', sans-serif;
}
.caption {
  position: absolute;
  bottom: 120px;
  left: 50%;
  transform: translateX(-50%);
  max-width: 650px;
  text-align: center;
  font-size: 26px;
  font-weight: 600;
  color: white;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.9), -1px -1px 2px rgba(0,0,0,0.5);
  line-height: 1.4;
}
</style>
</head>
<body>
<div class="caption">$text</div>
</body>
</html>
EOF
  
  cd /Users/aramide/clawd/SU
  npx playwright screenshot --viewport-size=720,900 "$DIR/caption-$num.html" "$DIR/caption-$num.png" 2>/dev/null
  echo "Created caption $num: $text"
done

echo "Done creating captions. Now combining with ffmpeg..."
