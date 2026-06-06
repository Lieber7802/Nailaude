import test from 'node:test'
import assert from 'node:assert/strict'

import {
  buildAttachmentSummary,
  formatConversationListTime,
  getAvailableConversationAgentIds,
  mergeConversationAgentIds,
  normalizeWorkspaceNameInput,
  parseBackendTimestamp,
} from '../src/utils/chatUi.ts'

test('treats backend ISO timestamps without timezone as UTC', () => {
  assert.equal(parseBackendTimestamp('2026-06-04T07:00:00').toISOString(), '2026-06-04T07:00:00.000Z')
})

test('preserves explicit timezone offsets in timestamps', () => {
  assert.equal(parseBackendTimestamp('2026-06-04T15:00:00+08:00').toISOString(), '2026-06-04T07:00:00.000Z')
})

test('formats conversation list time from updatedAt instead of a hard-coded placeholder', () => {
  assert.equal(
    formatConversationListTime({
      createdAt: '2026-06-04T01:00:00Z',
      updatedAt: '2026-06-04T07:23:00Z',
    }),
    '15:23'
  )
})

test('builds attachment summaries for selected files', () => {
  assert.equal(
    buildAttachmentSummary([
      { name: 'spec.md', size: 512 },
      { name: 'screenshot.png', size: 1536 },
    ]),
    '- spec.md (512 B)\n- screenshot.png (1.5 KB)'
  )
})

test('conversation agent picker only offers agents not already participating', () => {
  const agents = [{ id: 'agent-a' }, { id: 'agent-b' }, { id: 'agent-c' }]

  assert.deepEqual(getAvailableConversationAgentIds(agents, ['agent-a', 'agent-c']), ['agent-b'])
})

test('conversation agent updates merge selected agents without duplicates', () => {
  assert.deepEqual(mergeConversationAgentIds(['agent-a', 'agent-b'], ['agent-b', 'agent-c']), [
    'agent-a',
    'agent-b',
    'agent-c',
  ])
})

test('normalizes new conversation workspace names under workspaces', () => {
  assert.equal(normalizeWorkspaceNameInput('todo-app'), 'workspaces/todo-app')
  assert.equal(normalizeWorkspaceNameInput('  todo-app  '), 'workspaces/todo-app')
  assert.equal(normalizeWorkspaceNameInput('workspaces/existing'), 'workspaces/existing')
  assert.equal(normalizeWorkspaceNameInput(''), '')
})
