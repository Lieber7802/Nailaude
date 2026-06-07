import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { test } from 'node:test'

const chatArea = await readFile(new URL('../src/components/chat/ChatArea.tsx', import.meta.url), 'utf8')
const iframePreview = await readFile(new URL('../src/components/preview/IframePreview.tsx', import.meta.url), 'utf8')
const previewPanel = await readFile(new URL('../src/components/preview/PreviewPanel.tsx', import.meta.url), 'utf8')
const agentManage = await readFile(new URL('../src/pages/AgentManage.tsx', import.meta.url), 'utf8')
const api = await readFile(new URL('../src/services/api.ts', import.meta.url), 'utf8')
const css = await readFile(new URL('../src/index.css', import.meta.url), 'utf8')

function cssRule(selector) {
  const matches = [...css.matchAll(/(?<selectors>[^{}]+){(?<body>[^}]*)}/g)].filter((match) =>
    (match.groups?.selectors || '')
      .split(',')
      .map((item) => item.trim())
      .includes(selector)
  )
  assert.ok(matches.length > 0, `missing CSS rule for ${selector}`)
  return matches.map((match) => match.groups?.body || '').join('\n')
}

test('workspace empty and preview empty copy avoid implementation details', () => {
  assert.doesNotMatch(chatArea, /Mock 智能体会返回流式产物/)
  assert.doesNotMatch(iframePreview, /当前产出物暂不支持网页预览/)
  assert.match(previewPanel, /点击聊天中的产物卡片/)
})

test('fullscreen markdown preview stretches to the available panel body', () => {
  const rule = cssRule('.preview-panel--fullscreen .markdown-preview')

  assert.match(rule, /width:\s*100%/)
  assert.match(rule, /min-height:\s*0/)
  assert.match(rule, /border:\s*0/)
})

test('agent management page exposes custom agent administration actions', () => {
  assert.doesNotMatch(agentManage, /return <div>智能体管理<\/div>/)
  assert.match(agentManage, /自定义智能体/)
  assert.match(agentManage, /删除智能体/)
  assert.match(api, /delete:\s*\(id:\s*string\)/)
})
