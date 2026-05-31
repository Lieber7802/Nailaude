import test from 'node:test'
import assert from 'node:assert/strict'

import {
  hasAllClarificationAnswers,
  reconnectDelay,
  shouldAcceptSnapshot,
} from '../src/services/orchestratorLogic.mjs'

test('rejects stale snapshots from the same run before side effects', () => {
  assert.equal(shouldAcceptSnapshot({ runId: 'run-1', sequence: 4 }, { runId: 'run-1', sequence: 3 }), false)
  assert.equal(shouldAcceptSnapshot({ runId: 'run-1', sequence: 4 }, { runId: 'run-2', sequence: 1 }), true)
})

test('uses bounded reconnect backoff', () => {
  assert.deepEqual([0, 1, 2, 3, 4, 5].map(reconnectDelay), [250, 500, 1000, 2000, 4000, 4000])
})

test('requires all clarification answers before atomic submit', () => {
  const questions = [{ id: 'scope' }, { id: 'storage' }]

  assert.equal(hasAllClarificationAnswers(questions, { scope: 'minimal' }), false)
  assert.equal(hasAllClarificationAnswers(questions, { scope: 'minimal', storage: 'memory' }), true)
})
