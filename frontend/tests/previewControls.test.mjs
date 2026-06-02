import test from 'node:test'
import assert from 'node:assert/strict'

import { FULLSCREEN_ACTIONS, VIEWPORT_OPTIONS } from '../src/utils/previewControls.ts'

test('preview viewport controls expose clear labels', () => {
  assert.deepEqual(
    VIEWPORT_OPTIONS.map((option) => ({ label: option.label, viewport: option.viewport })),
    [
      { label: '桌面', viewport: 'desktop' },
      { label: '平板', viewport: 'tablet' },
      { label: '手机', viewport: 'mobile' },
    ]
  )
})

test('fullscreen action labels include enter and exit states', () => {
  assert.equal(FULLSCREEN_ACTIONS.enter.label, '全屏预览')
  assert.equal(FULLSCREEN_ACTIONS.exit.label, '退出全屏')
})
