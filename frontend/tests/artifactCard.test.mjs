import test from 'node:test'
import assert from 'node:assert/strict'

import {
  getArtifactCardPresentation,
  getChangeArtifacts,
  getOrderedMessageArtifacts,
  getOutputArtifacts,
} from '../src/utils/artifactCard.ts'

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
  assert.equal(presentation.detail, '+8 / -2 · src/App.tsx')
})

test('chat artifact cards show new files before changed files', () => {
  const created = {
    ...baseArtifact,
    id: 'created',
    type: 'code',
    title: 'src/App.tsx',
    files: [{ name: 'src/App.tsx', language: 'tsx', content: 'export function App() {}' }],
  }
  const webpage = {
    ...baseArtifact,
    id: 'webpage',
    type: 'webpage',
    title: 'index.html',
    previewUrl: '/preview/conv/index.html',
  }
  const changed = {
    ...baseArtifact,
    id: 'changed',
    type: 'diff',
    title: 'src/App.tsx changes',
    diffData: {
      file: 'src/App.tsx',
      additions: 2,
      deletions: 1,
      hunks: [],
    },
  }

  assert.deepEqual(
    getOrderedMessageArtifacts([changed, webpage, created]).map((artifact) => artifact.id),
    ['created', 'webpage', 'changed']
  )
})

test('right preview outputs exclude diffs while changes list only includes diff files', () => {
  const created = { ...baseArtifact, id: 'created', type: 'code', title: 'src/App.tsx' }
  const changed = {
    ...baseArtifact,
    id: 'changed',
    type: 'diff',
    title: 'src/App.tsx changes',
    diffData: {
      file: 'src/App.tsx',
      additions: 2,
      deletions: 1,
      hunks: [],
    },
  }

  assert.deepEqual(getOutputArtifacts([created, changed]).map((artifact) => artifact.id), ['created'])
  assert.deepEqual(getChangeArtifacts([created, changed]).map((artifact) => artifact.id), ['changed'])
})
