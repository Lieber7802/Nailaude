import test from 'node:test'
import assert from 'node:assert/strict'

import { getArtifactCardPresentation } from '../src/utils/artifactCard.ts'

const baseArtifact = {
  id: 'artifact-1',
  messageId: 'message-1',
  previousVersionId: null,
  previewUrl: null,
  createdAt: '2026-06-04T00:00:00Z',
  version: 1,
  files: [],
  diffData: null,
}

test('code artifact cards summarize generated files without inline preview requirements', () => {
  const presentation = getArtifactCardPresentation({
    ...baseArtifact,
    type: 'code',
    title: 'src/App.tsx',
    files: [{ name: 'src/App.tsx', language: 'tsx', content: 'export function App() {\n  return null\n}' }],
  })

  assert.deepEqual(presentation, {
    actionLabel: '在右侧查看',
    detail: 'TSX · 3 行 · 39 B',
    kind: 'code',
    statusLabel: '新创建的文件',
    title: 'src/App.tsx',
  })
})

test('diff artifact cards summarize file changes for right-side inspection', () => {
  const presentation = getArtifactCardPresentation({
    ...baseArtifact,
    type: 'diff',
    title: 'src/App.tsx changes',
    diffData: {
      file: 'src/App.tsx',
      additions: 8,
      deletions: 2,
      oldContent: '',
      newContent: '',
      hunks: [],
    },
  })

  assert.equal(presentation.kind, 'diff')
  assert.equal(presentation.statusLabel, '文件更改')
  assert.equal(presentation.detail, '+8 / -2 · src/App.tsx')
})
