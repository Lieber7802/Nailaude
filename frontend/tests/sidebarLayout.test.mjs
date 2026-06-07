import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { test } from 'node:test'

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

test('conversation list fills sidebar remainder before it scrolls', () => {
  const rule = cssRule('.conversation-list')

  assert.match(rule, /flex:\s*1\b/)
  assert.match(rule, /min-height:\s*0\b/)
  assert.match(rule, /overflow-y:\s*auto\b/)
})

test('conversation rows keep content height when the list has extra space', () => {
  const rule = cssRule('.conversation-list')

  assert.match(rule, /align-content:\s*start\b/)
  assert.match(rule, /grid-auto-rows:\s*max-content\b/)
})

test('sidebar keeps long agent lists from clipping conversations', () => {
  const sidebarRule = cssRule('.sidebar')
  const agentListRule = cssRule('.agent-list')

  assert.match(sidebarRule, /overflow-y:\s*auto\b/)
  assert.match(agentListRule, /max-height:\s*180px\b/)
  assert.match(agentListRule, /overflow-y:\s*auto\b/)
})

test('sidebar removes conversation search entry point', async () => {
  const conversationList = await readFile(
    new URL('../src/components/chat/ConversationList.tsx', import.meta.url),
    'utf8'
  )
  const workspace = await readFile(new URL('../src/pages/Workspace.tsx', import.meta.url), 'utf8')

  assert.doesNotMatch(conversationList, /搜索对话或消息/)
  assert.doesNotMatch(conversationList, /conversation-search/)
  assert.doesNotMatch(workspace, /useState\(''\)/)
})
