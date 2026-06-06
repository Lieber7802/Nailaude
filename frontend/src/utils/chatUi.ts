export interface AttachmentSummaryInput {
  name: string
  size: number
}

export interface ConversationListTimeInput {
  createdAt?: string
  updatedAt?: string
}

const LOCAL_TIME_FORMATTER = new Intl.DateTimeFormat('zh-CN', {
  hour: '2-digit',
  minute: '2-digit',
  hour12: false,
})

const ISO_WITH_TIMEZONE_PATTERN = /(?:Z|[+-]\d{2}:?\d{2})$/i
const ISO_WITH_TIME_PATTERN = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/

export function parseBackendTimestamp(value: string): Date {
  const normalized = ISO_WITH_TIME_PATTERN.test(value) && !ISO_WITH_TIMEZONE_PATTERN.test(value) ? `${value}Z` : value
  const date = new Date(normalized)
  return Number.isNaN(date.getTime()) ? new Date() : date
}

export function formatChatTime(value: string | Date): string {
  const date = value instanceof Date ? value : parseBackendTimestamp(value)
  return LOCAL_TIME_FORMATTER.format(date)
}

export function formatConversationListTime(conversation: ConversationListTimeInput): string {
  const timestamp = conversation.updatedAt || conversation.createdAt
  return timestamp ? formatChatTime(timestamp) : '新建'
}

export function buildAttachmentSummary(files: AttachmentSummaryInput[]): string {
  if (files.length === 0) return ''
  return files.map((file) => `- ${file.name} (${formatFileSize(file.size)})`).join('\n')
}

export function getAvailableConversationAgentIds<T extends { id: string }>(
  agents: T[],
  participantIds: string[]
): string[] {
  const participantIdSet = new Set(participantIds)
  return agents.filter((agent) => !participantIdSet.has(agent.id)).map((agent) => agent.id)
}

export function mergeConversationAgentIds(participantIds: string[], selectedAgentIds: string[]): string[] {
  return [...new Set([...participantIds, ...selectedAgentIds])]
}

export function normalizeWorkspaceNameInput(value: string): string {
  const trimmed = value.trim().replace(/\\/g, '/').replace(/^\/+|\/+$/g, '')
  if (!trimmed) return ''
  return trimmed.toLowerCase().startsWith('workspaces/') ? trimmed : `workspaces/${trimmed}`
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}
