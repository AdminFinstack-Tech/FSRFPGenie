#!/usr/bin/env node

/**
 * Create SVG wrapper for the original logo PNG
 * This creates a proper SVG that embeds the PNG as a base64 data URL
 */

const fs = require('fs');
const path = require('path');

const publicDir = path.join(__dirname, 'public');
const pngPath = path.join(publicDir, 'logo-old-backup.png');
const svgPath = path.join(publicDir, 'logo-original.svg');

// Read PNG and convert to base64
const pngBuffer = fs.readFileSync(pngPath);
const base64Data = pngBuffer.toString('base64');
const dataUrl = `data:image/png;base64,${base64Data}`;

// Create SVG wrapper
const svgContent = `<?xml version="1.0" encoding="UTF-8"?>
<svg width="1024" height="1024" viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <title>FS RFP Genie Logo</title>
  <desc>Original logo for FS RFP Genie application</desc>
  <image 
    width="1024" 
    height="1024" 
    xlink:href="${dataUrl}"
    preserveAspectRatio="xMidYMid meet"
  />
</svg>`;

// Write SVG file
fs.writeFileSync(svgPath, svgContent);

console.log('✅ SVG created successfully!');
console.log(`📁 Location: ${svgPath}`);
console.log(`📊 Size: ${(fs.statSync(svgPath).size / 1024 / 1024).toFixed(2)} MB`);
console.log('\n🎨 The SVG embeds the original PNG as a base64 data URL');
console.log('✨ This provides the best of both worlds: SVG scalability + PNG quality');
