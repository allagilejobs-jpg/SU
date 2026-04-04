#!/usr/bin/env node
/**
 * Local render server for Spectrum Unlocked HTML Editor
 * 
 * Run: node render-server.js
 * Then use the HTML editor at http://localhost:8080/html-editor.html
 * 
 * The editor will call this server to render PNGs.
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const PORT = 3456;
const BASE_DIR = __dirname;

const server = http.createServer(async (req, res) => {
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }
  
  if (req.method === 'POST' && req.url === '/render') {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', async () => {
      try {
        const { html, outputPath } = JSON.parse(body);
        
        if (!html || !outputPath) {
          throw new Error('Missing html or outputPath');
        }
        
        // Write HTML to temp file
        const tempHtml = path.join(BASE_DIR, '.temp-render.html');
        fs.writeFileSync(tempHtml, html);
        
        // Full output path
        const fullOutputPath = path.join(BASE_DIR, outputPath);
        
        // Detect size from HTML (look for body width/height)
        let width = 1080;
        let height = 1350;
        const sizeMatch = html.match(/body\s*\{[^}]*width:\s*(\d+)px;\s*height:\s*(\d+)px/);
        if (sizeMatch) {
          width = parseInt(sizeMatch[1]);
          height = parseInt(sizeMatch[2]);
        }
        
        // Render with Playwright at detected size
        console.log(`Rendering: ${outputPath} (${width}x${height})`);
        execSync(`/opt/homebrew/bin/npx playwright screenshot --viewport-size=${width},${height} "${tempHtml}" "${fullOutputPath}"`, {
          cwd: BASE_DIR,
          stdio: 'inherit'
        });
        
        // Clean up temp file
        fs.unlinkSync(tempHtml);
        
        console.log(`✅ Saved: ${outputPath}`);
        
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ success: true, path: outputPath }));
        
      } catch (err) {
        console.error('Render error:', err.message);
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: err.message }));
      }
    });
    return;
  }
  
  if (req.method === 'POST' && req.url === '/save') {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', async () => {
      try {
        const { html, filePath } = JSON.parse(body);
        
        if (!html || !filePath) {
          throw new Error('Missing html or filePath');
        }
        
        // Full file path
        const fullPath = path.join(BASE_DIR, filePath);
        
        // Save HTML
        fs.writeFileSync(fullPath, html);
        console.log(`✅ Saved HTML: ${filePath}`);
        
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ success: true, path: filePath }));
        
      } catch (err) {
        console.error('Save error:', err.message);
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: err.message }));
      }
    });
    return;
  }
  
  res.writeHead(404);
  res.end('Not found');
});

server.listen(PORT, () => {
  console.log(`
🎨 Spectrum Unlocked Render Server
===================================
Server running at http://localhost:${PORT}

Endpoints:
  POST /render  - Render HTML to PNG
  POST /save    - Save HTML file

Usage:
  1. Keep this server running
  2. Open html-editor.html in browser
  3. Edit content and click "Render PNG"
  4. PNG will be saved automatically

Press Ctrl+C to stop.
`);
});
