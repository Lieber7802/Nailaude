import assert from 'node:assert/strict'
import { test } from 'node:test'

import { useUIStore } from '../src/stores/uiStore.ts'

const completedTask = {
  id: 'task-1',
  agentId: 'agent-1',
  agentName: '代码工匠',
  title: 'Done',
  objective: 'Done',
  instruction: 'Done',
  acceptanceCriteria: [],
  constraints: [],
  accessMode: 'read',
  status: 'completed',
  dependsOn: [],
  priority: 1,
  riskHints: {
    mayDeleteOrRenameFiles: false,
    mayTouchConfigFiles: false,
    estimatedFilesTouched: 0,
  },
}

test('completed task snapshots do not create fake duration after refresh', () => {
  useUIStore.setState({ runtimeByConversation: {} })

  useUIStore.getState().setOrchestratorStatus('conv-refresh', 'completed', [completedTask])

  assert.deepEqual(useUIStore.getState().runtimeByConversation['conv-refresh'].taskTimings, {})
})

test('running task snapshots do not restart duration after refresh without a local start event', () => {
  useUIStore.setState({ runtimeByConversation: {} })

  useUIStore.getState().setOrchestratorStatus('conv-refresh-running', 'executing', [
    { ...completedTask, status: 'running' },
  ])

  assert.deepEqual(useUIStore.getState().runtimeByConversation['conv-refresh-running'].taskTimings, {})
})
