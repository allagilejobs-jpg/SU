#!/bin/bash
# Render HTML to PNG using Playwright
# Usage: ./render.sh content/day-01-tiktok-myths/slide-01-cover.html

if [ -z "$1" ]; then
  echo "Usage: ./render.sh <html-file>"
  echo "Example: ./render.sh content/day-01-tiktok-myths/slide-01-cover.html"
  exit 1
fi

HTML_FILE="$1"
PNG_FILE="${HTML_FILE%.html}.png"

if [ ! -f "$HTML_FILE" ]; then
  echo "Error: File not found: $HTML_FILE"
  exit 1
fi

echo "Rendering: $HTML_FILE"
echo "Output: $PNG_FILE"

npx playwright screenshot --viewport-size=1080,1350 "$HTML_FILE" "$PNG_FILE"

if [ $? -eq 0 ]; then
  echo "✅ Done! PNG saved to: $PNG_FILE"
else
  echo "❌ Error rendering PNG"
  exit 1
fi
