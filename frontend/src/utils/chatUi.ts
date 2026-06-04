export interface AttachmentSummaryInput {
  name: string
  size: number
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

export function buildAttachmentSummary(files: AttachmentSummaryInput[]): string {
  if (files.length === 0) return ''
  return files.map((file) => `- ${file.name} (${formatFileSize(file.size)})`).join('\n')
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}
