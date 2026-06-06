import test from 'node:test'
import assert from 'node:assert/strict'

import {
  clampPreviewZoom,
  FULLSCREEN_ACTIONS,
  PREVIEW_VIEWPORT_LABEL_CLASS,
  PREVIEW_VIEWPORT_LABEL_HIDE_WIDTH,
  PREVIEW_ZOOM_CONTROL_MAX_WIDTH,
  PREVIEW_ZOOM_SLIDER_MIN_WIDTH,
  PREVIEW_ZOOM,
  VIEWPORT_OPTIONS,
} from '../src/utils/previewControls.ts'

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

test('preview viewport labels hide before narrow panes force vertical text', () => {
  assert.equal(PREVIEW_VIEWPORT_LABEL_HIDE_WIDTH, 430)
})

test('preview viewport hidden label class is scoped to text only', () => {
  assert.equal(PREVIEW_VIEWPORT_LABEL_CLASS, 'viewport-switcher__label')
})

test('preview zoom slider keeps a narrow-pane minimum width', () => {
  assert.equal(PREVIEW_ZOOM_SLIDER_MIN_WIDTH, 56)
})

test('preview zoom controls stay compact in wide panes', () => {
  assert.equal(PREVIEW_ZOOM_CONTROL_MAX_WIDTH, 340)
})

test('fullscreen action labels include enter and exit states', () => {
  assert.equal(FULLSCREEN_ACTIONS.enter.label, '全屏预览')
  assert.equal(FULLSCREEN_ACTIONS.exit.label, '退出全屏')
})

test('preview zoom supports a broad free scaling range', () => {
  assert.deepEqual(PREVIEW_ZOOM, { min: 25, max: 300, step: 10 })
  assert.equal(clampPreviewZoom(5), 25)
  assert.equal(clampPreviewZoom(138.4), 138)
  assert.equal(clampPreviewZoom(500), 300)
})
