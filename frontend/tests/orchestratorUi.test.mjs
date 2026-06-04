import test from 'node:test'
import assert from 'node:assert/strict'

import {
  orchestratorMessageLabel,
  orchestratorStatusLabel,
  batchStatusLabel,
  visibleCollaborationAgents,
  visibleOrchestratorWarnings,
} from '../src/utils/orchestratorUi.ts'

test('collaboration status only shows agents involved in current tasks or thinking', () => {
  const agents = [
    { id: 'code', name: '代码工匠' },
    { id: 'review', name: '审查大师' },
    { id: 'docs', name: '文档专家' },
  ]
  const tasks = [{ agentName: '文档专家', status: 'running' }]

  assert.deepEqual(visibleCollaborationAgents(agents, tasks, ['文档专家']), [
    { id: 'docs', name: '文档专家', status: '思考中' },
  ])
})

test('collaboration status falls back to participants before a run starts', () => {
  assert.deepEqual(visibleCollaborationAgents([{ id: 'code', name: '代码工匠' }], [], []), [
    { id: 'code', name: '代码工匠', status: '等待中' },
  ])
})

test('orchestrator labels are localized and summary failures are hidden', () => {
  assert.equal(orchestratorStatusLabel('executing'), '执行中')
  assert.equal(batchStatusLabel('partial'), '部分完成')
  assert.equal(orchestratorMessageLabel('completed', 'Run completed'), '运行已完成')
  assert.deepEqual(
    visibleOrchestratorWarnings([
      'Project summary unavailable: DeepSeek request failed:',
      'Adapter downgraded to llm',
    ]),
    ['Adapter downgraded to llm']
  )
})
