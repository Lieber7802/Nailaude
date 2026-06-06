import test from 'node:test'
import assert from 'node:assert/strict'

import {
  MESSAGE_ARTIFACT_COLLAPSE_LIMIT,
  getArtifactCardPresentation,
  getChangeArtifacts,
  getOrderedMessageArtifacts,
  getOutputArtifacts,
  getVisibleMessageArtifacts,
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
    ['webpage', 'created', 'changed']
  )
})

test('chat artifact cards prioritize previewable html and readme artifacts', () => {
  const source = {
    ...baseArtifact,
    id: 'source',
    type: 'code',
    title: 'src/App.tsx',
    files: [{ name: 'src/App.tsx', language: 'tsx', content: 'export function App() {}' }],
  }
  const readme = {
    ...baseArtifact,
    id: 'readme',
    type: 'code',
    title: 'README.md',
    files: [{ name: 'README.md', language: 'markdown', content: '# Project' }],
  }
  const html = {
    ...baseArtifact,
    id: 'html',
    type: 'code',
    title: 'public/index.html',
    files: [{ name: 'public/index.html', language: 'html', content: '<main>Hello</main>' }],
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
    getOrderedMessageArtifacts([source, changed, readme, webpage, html]).map((artifact) => artifact.id),
    ['webpage', 'html', 'readme', 'source', 'changed']
  )
})

test('chat artifact ordering keeps same-priority files in arrival order', () => {
  const artifacts = ['src/App.tsx', 'src/main.tsx', 'src/styles.css'].map((title, index) => ({
    ...baseArtifact,
    id: `source-${index + 1}`,
    type: 'code',
    title,
    files: [{ name: title, language: title.endsWith('.css') ? 'css' : 'tsx', content: '' }],
  }))

  assert.deepEqual(
    getOrderedMessageArtifacts([...artifacts].reverse()).map((artifact) => artifact.id),
    ['source-3', 'source-2', 'source-1']
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

test('message artifact lists default to the first three sorted items before expansion', () => {
  const artifacts = Array.from({ length: 7 }, (_, index) => ({
    ...baseArtifact,
    id: `artifact-${index + 1}`,
    type: 'code',
    title: `file-${index + 1}.ts`,
  }))

  const collapsed = getVisibleMessageArtifacts(artifacts, false)
  const expanded = getVisibleMessageArtifacts(artifacts, true)

  assert.equal(MESSAGE_ARTIFACT_COLLAPSE_LIMIT, 3)
  assert.deepEqual(
    collapsed.visibleArtifacts.map((artifact) => artifact.id),
    ['artifact-1', 'artifact-2', 'artifact-3']
  )
  assert.equal(collapsed.hiddenCount, 4)
  assert.deepEqual(expanded.visibleArtifacts.map((artifact) => artifact.id), artifacts.map((artifact) => artifact.id))
  assert.equal(expanded.hiddenCount, 0)
})

test('collapsed message artifact lists show priority artifacts first', () => {
  const artifacts = [
    {
      ...baseArtifact,
      id: 'source-1',
      type: 'code',
      title: 'src/App.tsx',
      files: [{ name: 'src/App.tsx', language: 'tsx', content: '' }],
    },
    {
      ...baseArtifact,
      id: 'source-2',
      type: 'code',
      title: 'src/main.tsx',
      files: [{ name: 'src/main.tsx', language: 'tsx', content: '' }],
    },
    {
      ...baseArtifact,
      id: 'readme',
      type: 'document',
      title: 'README.md',
      files: [{ name: 'README.md', language: 'markdown', content: '# Project' }],
    },
    {
      ...baseArtifact,
      id: 'html',
      type: 'webpage',
      title: 'index.html',
      previewUrl: '/preview/conv/index.html',
    },
    {
      ...baseArtifact,
      id: 'source-3',
      type: 'code',
      title: 'src/theme.ts',
      files: [{ name: 'src/theme.ts', language: 'ts', content: '' }],
    },
  ]
  const ordered = getOrderedMessageArtifacts(artifacts)
  const collapsed = getVisibleMessageArtifacts(ordered, false)

  assert.deepEqual(
    collapsed.visibleArtifacts.map((artifact) => artifact.id),
    ['html', 'readme', 'source-1']
  )
  assert.equal(collapsed.hiddenCount, 2)
})
