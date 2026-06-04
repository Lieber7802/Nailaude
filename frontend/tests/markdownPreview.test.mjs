import test from 'node:test'
import assert from 'node:assert/strict'

import {
  getArtifactPreviewMode,
  isMarkdownFile,
  parseInlineMarkdown,
  parseMarkdownBlocks,
} from '../src/utils/markdownPreview.ts'

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

test('parses tilde fenced code blocks used by chat replies', () => {
  const blocks = parseMarkdownBlocks('~~~tsx\nconst value = <App />\n~~~')

  assert.deepEqual(blocks, [{ type: 'code', language: 'tsx', code: 'const value = <App />' }])
})

test('parses indented code blocks used by plain markdown replies', () => {
  const blocks = parseMarkdownBlocks('Here is code:\n\n    const value = 1\n    console.log(value)')

  assert.deepEqual(blocks, [
    { type: 'paragraph', text: 'Here is code:' },
    { type: 'code', language: 'text', code: 'const value = 1\nconsole.log(value)' },
  ])
})

test('parses chat replies with markdown headings, ordered lists, and paragraphs', () => {
  const blocks = parseMarkdownBlocks('## Done\n\n1. Created `App.tsx`\n2. Added **preview** button\n\nReady for review.')

  assert.deepEqual(blocks, [
    { type: 'heading', level: 2, text: 'Done' },
    { type: 'list', ordered: true, items: ['Created `App.tsx`', 'Added **preview** button'] },
    { type: 'paragraph', text: 'Ready for review.' },
  ])
})

test('parses nested strong inline code without preserving literal backticks', () => {
  assert.deepEqual(parseInlineMarkdown('**`index.html`** — 预览入口'), [
    { type: 'strong', children: [{ type: 'code', text: 'index.html' }] },
    { type: 'text', text: ' — 预览入口' },
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
