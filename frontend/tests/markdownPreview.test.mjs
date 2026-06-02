import test from 'node:test'
import assert from 'node:assert/strict'

import { getArtifactPreviewMode, isMarkdownFile, parseMarkdownBlocks } from '../src/utils/markdownPreview.ts'

test('recognizes generated code review markdown files', () => {
  assert.equal(isMarkdownFile({ name: 'index.html.code-review.md', language: 'markdown' }), true)
  assert.equal(isMarkdownFile({ name: 'notes.MARKDOWN', language: 'text' }), true)
  assert.equal(isMarkdownFile({ name: 'index.html', language: 'html' }), false)
})

test('selects markdown preview mode without requiring previewUrl', () => {
  const artifact = {
    files: [{ name: 'index.html.code-review.md', language: 'markdown', content: '# Review' }],
    previewUrl: null,
  }

  assert.equal(getArtifactPreviewMode(artifact), 'markdown')
})

test('parses markdown headings, lists, and fenced code for rendered preview', () => {
  const blocks = parseMarkdownBlocks('# Title\n\n- item\n\n```js\nconst value = 1\n```')

  assert.deepEqual(blocks, [
    { type: 'heading', level: 1, text: 'Title' },
    { type: 'list', ordered: false, items: ['item'] },
    { type: 'code', language: 'js', code: 'const value = 1' },
  ])
})

test('parses github-style markdown tables', () => {
  const blocks = parseMarkdownBlocks(
    '| 严重度 | 数量 | 关键事项 |\n|---|---:|---|\n| 🔴 High | 1 | XSS 漏洞 |\n| 🟢 Low | 7 | label 缺失 |'
  )

  assert.deepEqual(blocks, [
    {
      type: 'table',
      headers: ['严重度', '数量', '关键事项'],
      alignments: ['left', 'right', 'left'],
      rows: [
        ['🔴 High', '1', 'XSS 漏洞'],
        ['🟢 Low', '7', 'label 缺失'],
      ],
    },
  ])
})
