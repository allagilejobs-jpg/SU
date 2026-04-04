#!/bin/bash
cd "$(dirname "$0")"

echo "🎨 Starting Spectrum Unlocked Editor..."
echo ""

# Start render server in background
node render-server.js &
sleep 1

# Start file server and open browser
echo "Opening browser..."
open "http://localhost:8080/calendar-60day.html"

python3 -m http.server 8080 2>/dev/null

# Cleanup
pkill -f "node render-server.js" 2>/dev/null
