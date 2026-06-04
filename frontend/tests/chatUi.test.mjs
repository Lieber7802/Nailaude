import test from 'node:test'
import assert from 'node:assert/strict'

import { buildAttachmentSummary, parseBackendTimestamp } from '../src/utils/chatUi.ts'

test('treats backend ISO timestamps without timezone as UTC', () => {
  assert.equal(parseBackendTimestamp('2026-06-04T07:00:00').toISOString(), '2026-06-04T07:00:00.000Z')
})

test('preserves explicit timezone offsets in timestamps', () => {
  assert.equal(parseBackendTimestamp('2026-06-04T15:00:00+08:00').toISOString(), '2026-06-04T07:00:00.000Z')
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
