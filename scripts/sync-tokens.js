#!/usr/bin/env node
/**
 * sync-tokens.js
 *
 * Reads frontend/tokens.json (Tokens Studio format) and regenerates
 * the color + animation sections of frontend/tailwind.config.js.
 *
 * Usage:
 *   node scripts/sync-tokens.js
 *
 * Run this after exporting tokens from Figma via the Tokens Studio plugin
 * (Sync → GitHub or export to local file, point it at frontend/tokens.json).
 */

import { readFileSync, writeFileSync } from 'fs'
import { resolve, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const root = resolve(__dirname, '..')
const tokensPath = resolve(root, 'frontend/tokens.json')
const tailwindPath = resolve(root, 'frontend/tailwind.config.js')

const tokens = JSON.parse(readFileSync(tokensPath, 'utf8'))
const global = tokens.global

// ── Helpers ──────────────────────────────────────────────────────────────────

function colorScale(scale) {
  return Object.fromEntries(
    Object.entries(scale).map(([k, v]) => [k, v.value])
  )
}

// ── Extract values ────────────────────────────────────────────────────────────

const colors = {
  'cornell-red': global.color.cornell['700'].value,
  cornell: colorScale(global.color.cornell),
  slate: colorScale(global.color.slate),
}

const borderRadius = Object.fromEntries(
  Object.entries(global.borderRadius).map(([k, v]) => [k, `${v.value}px`])
)

const fontFamily = {
  sans: [global.typography.fontFamily.sans.value],
}

const animation = {
  'fade-in': `fadeIn ${global.animation.fadeIn.duration.value} ${global.animation.fadeIn.easing.value}`,
  'slide-up': `slideUp ${global.animation.slideUp.duration.value} ${global.animation.slideUp.easing.value}`,
}

const keyframes = {
  fadeIn: {
    '0%': { opacity: '0' },
    '100%': { opacity: '1' },
  },
  slideUp: {
    '0%': { opacity: '0', transform: `translateY(${global.animation.slideUp.translateY.value})` },
    '100%': { opacity: '1', transform: 'translateY(0)' },
  },
}

// ── Write tailwind.config.js ──────────────────────────────────────────────────

const config = `/** @type {import('tailwindcss').Config} */
// AUTO-GENERATED — edit frontend/tokens.json, then run: node scripts/sync-tokens.js
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: ${JSON.stringify(fontFamily, null, 6).replace(/"/g, "'")},
      colors: ${JSON.stringify(colors, null, 6).replace(/"#/g, "'#").replace(/",/g, "',").replace(/"}/g, "'}").replace(/": "/g, "': '")},
      borderRadius: ${JSON.stringify(borderRadius, null, 6).replace(/"/g, "'")},
      animation: ${JSON.stringify(animation, null, 6).replace(/"/g, "'")},
      keyframes: ${JSON.stringify(keyframes, null, 6).replace(/"/g, "'")},
    },
  },
  plugins: [],
}
`

writeFileSync(tailwindPath, config, 'utf8')
console.log('✓ tailwind.config.js updated from tokens.json')
