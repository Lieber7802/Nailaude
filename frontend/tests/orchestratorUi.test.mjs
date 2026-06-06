import test from 'node:test'
import assert from 'node:assert/strict'

import {
  formatTaskDuration,
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
    { id: 'docs', name: '文档专家', status: '思考中', tone: 'pending' },
  ])
})

test('collaboration status falls back to participants before a run starts', () => {
  assert.deepEqual(visibleCollaborationAgents([{ id: 'code', name: '代码工匠' }], [], []), [
    { id: 'code', name: '代码工匠', status: '等待中', tone: 'idle' },
  ])
})

test('collaboration status marks failed and blocked agents differently and exposes duration', () => {
  const agents = [
    { id: 'code', name: '代码工匠' },
    { id: 'review', name: '审查大师' },
    { id: 'docs', name: '文档专家' },
  ]
  const tasks = [
    { agentName: '代码工匠', status: 'completed' },
    { agentName: '审查大师', status: 'failed' },
    { agentName: '文档专家', status: 'blocked' },
  ]
  const timings = {
    代码工匠: { startedAt: 1_000, endedAt: 3_600 },
    审查大师: { startedAt: 2_000, endedAt: 9_500 },
    文档专家: { startedAt: 4_000, endedAt: 65_000 },
  }

  assert.deepEqual(visibleCollaborationAgents(agents, tasks, [], timings, 70_000), [
    { id: 'code', name: '代码工匠', status: '已完成', tone: 'done', durationMs: 2_600 },
    { id: 'review', name: '审查大师', status: '失败', tone: 'danger', durationMs: 7_500 },
    { id: 'docs', name: '文档专家', status: '已阻塞', tone: 'warning', durationMs: 61_000 },
  ])
  assert.equal(formatTaskDuration(2_600), '2.6s')
  assert.equal(formatTaskDuration(61_000), '1m 1s')
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
