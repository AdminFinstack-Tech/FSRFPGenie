#!/usr/bin/env node

/**
 * Finstack 2025 Logo Generator
 * Generates PNG logo from SVG definition
 * 
 * Usage: node generate-logo.js [size]
 * Default size: 512x512
 */

const fs = require('fs');
const path = require('path');

// SVG Template for Finstack 2025 Logo
const generateSVG = (size = 512) => {
  const scale = size / 48; // Base viewBox is 48x48
  
  return `<?xml version="1.0" encoding="UTF-8"?>
<svg width="${size}" height="${size}" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Gradient: Teal to Purple -->
    <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#38B2AC;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#805AD5;stop-opacity:1" />
    </linearGradient>
    
    <!-- Glow effect -->
    <filter id="glow">
      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  
  <!-- Background (transparent) -->
  <rect width="48" height="48" fill="none"/>
  
  <!-- Base layers (stack motif) - Bottom layer -->
  <rect 
    x="12" y="34" 
    width="24" height="3" 
    rx="1.5" 
    fill="url(#logoGradient)" 
    opacity="0.8"
  />
  
  <!-- Base layers (stack motif) - Middle layer -->
  <rect 
    x="14" y="30" 
    width="20" height="3" 
    rx="1.5" 
    fill="url(#logoGradient)" 
    opacity="0.9"
  />
  
  <!-- Lamp body - Triangle shade -->
  <path 
    d="M 24 8 L 28 20 L 20 20 Z" 
    fill="url(#logoGradient)"
  />
  
  <!-- Lamp body - Post/stem -->
  <rect 
    x="22" y="20" 
    width="4" height="8" 
    rx="1" 
    fill="url(#logoGradient)"
  />
  
  <!-- Light glow at top -->
  <circle 
    cx="24" cy="8" 
    r="4" 
    fill="#FFFFFF" 
    opacity="0.4"
    filter="url(#glow)"
  />
  
  <!-- Grid pattern lines -->
  <line 
    x1="18" y1="32" 
    x2="30" y2="32" 
    stroke="#FFFFFF" 
    stroke-width="0.5" 
    opacity="0.4"
  />
  <line 
    x1="16" y1="36" 
    x2="32" y2="36" 
    stroke="#FFFFFF" 
    stroke-width="0.5" 
    opacity="0.4"
  />
</svg>`;
};

// Generate multiple sizes
const sizes = [
  { size: 48, name: 'logo-48.svg' },
  { size: 64, name: 'logo-64.svg' },
  { size: 128, name: 'logo-128.svg' },
  { size: 256, name: 'logo-256.svg' },
  { size: 512, name: 'logo-512.svg' }
];

const outputDir = path.join(__dirname, '../public');

// Ensure output directory exists
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

console.log('🎨 Finstack 2025 Logo Generator\n');
console.log('Generating SVG logos...\n');

// Generate SVG files
sizes.forEach(({ size, name }) => {
  const svg = generateSVG(size);
  const outputPath = path.join(outputDir, name);
  fs.writeFileSync(outputPath, svg);
  console.log(`✅ Generated: ${name} (${size}x${size})`);
});

// Generate main logo.svg (512x512)
const mainSvg = generateSVG(512);
const mainSvgPath = path.join(outputDir, 'logo.svg');
fs.writeFileSync(mainSvgPath, mainSvg);
console.log(`✅ Generated: logo.svg (512x512) [Main Logo]`);

console.log('\n📝 Instructions for PNG conversion:');
console.log('To convert SVG to PNG, you can use one of these methods:\n');
console.log('1. Online converter: https://cloudconvert.com/svg-to-png');
console.log('2. ImageMagick: convert logo.svg -resize 512x512 logo.png');
console.log('3. Inkscape CLI: inkscape logo.svg --export-png=logo.png -w 512 -h 512');
console.log('4. Chrome: Open logo.svg, take screenshot, save as PNG');
console.log('\n✨ All SVG files saved to:', outputDir);
console.log('\n🚀 Ready to use! Replace logo.png with your converted PNG file.');

module.exports = { generateSVG };
