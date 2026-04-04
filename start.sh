#!/bin/bash
# Start Spectrum Unlocked Editor
# Just double-click this file or run: ./start.sh

cd "$(dirname "$0")"

echo "🎨 Starting Spectrum Unlocked..."

# Start render server in background
node render-server.js &
SERVER_PID=$!

# Wait for server to start
sleep 1

# Open calendar in browser
open "http://localhost:8080/calendar-60day.html"

# Start simple HTTP server for local files
echo "📂 Serving files at http://localhost:8080"
echo "🌐 Calendar opened in browser"
echo ""
echo "Press Ctrl+C to stop when done."
echo ""

# Use Python's simple HTTP server (built into macOS)
python3 -m http.server 8080 2>/dev/null || python -m SimpleHTTPServer 8080

# Cleanup when stopped
kill $SERVER_PID 2>/dev/null
echo "Stopped."
