import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { test } from 'node:test'

const css = await readFile(new URL('../src/index.css', import.meta.url), 'utf8')

test('frontend CSS exposes Claude-inspired design tokens', () => {
  assert.match(css, /--parchment:\s*#f5f4ed/i)
  assert.match(css, /--ivory:\s*#faf9f5/i)
  assert.match(css, /--terracotta:\s*#c96442/i)
  assert.match(css, /--near-black:\s*#141413/i)
  assert.match(css, /--font-serif:\s*Georgia/i)
  assert.match(css, /--ring-warm:\s*#d1cfc5/i)
})

test('frontend CSS favors warm paper surfaces over gradient-heavy chrome', () => {
  const gradientCount = (css.match(/linear-gradient|radial-gradient/g) || []).length
  assert.ok(gradientCount <= 3, `expected at most 3 gradients, found ${gradientCount}`)
  assert.match(css, /body\s*{[^}]*background:\s*var\(--bg\)/s)
})
