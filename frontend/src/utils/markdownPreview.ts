export type ArtifactPreviewMode = 'html' | 'markdown' | 'remote' | 'unsupported'

export interface FilePreviewInput {
  content?: string
  language?: string
  name: string
}

export interface ArtifactPreviewInput<TFile extends FilePreviewInput = FilePreviewInput> {
  files?: TFile[]
  previewUrl?: string | null
}

export type MarkdownBlock =
  | { type: 'heading'; level: number; text: string }
  | { type: 'paragraph'; text: string }
  | { type: 'list'; ordered: boolean; items: string[] }
  | { type: 'table'; headers: string[]; alignments: TableAlignment[]; rows: string[][] }
  | { type: 'code'; language: string; code: string }
  | { type: 'rule' }

export type TableAlignment = 'left' | 'center' | 'right'

const MARKDOWN_EXTENSIONS = ['.md', '.markdown', '.mdown', '.mkd']
const MARKDOWN_LANGUAGES = new Set(['markdown', 'md', 'gfm'])

export function isMarkdownFile(file?: FilePreviewInput): boolean {
  if (!file) return false
  const language = file.language?.trim().toLowerCase()
  const name = file.name.trim().toLowerCase()

  return Boolean(
    (language && MARKDOWN_LANGUAGES.has(language)) || MARKDOWN_EXTENSIONS.some((extension) => name.endsWith(extension))
  )
}

export function isHtmlFile(file?: FilePreviewInput): boolean {
  if (!file) return false
  const language = file.language?.trim().toLowerCase()
  const name = file.name.trim().toLowerCase()

  return language === 'html' || name.endsWith('.html') || name.endsWith('.htm')
}

export function findMarkdownFile<TFile extends FilePreviewInput>(artifact?: ArtifactPreviewInput<TFile>): TFile | undefined {
  return artifact?.files?.find((file) => isMarkdownFile(file))
}

export function getArtifactPreviewMode(artifact?: ArtifactPreviewInput): ArtifactPreviewMode {
  if (!artifact) return 'unsupported'
  if (artifact.files?.some((file) => isHtmlFile(file))) return 'html'
  if (artifact.files?.some((file) => isMarkdownFile(file))) return 'markdown'
  if (artifact.previewUrl) return 'remote'
  return 'unsupported'
}

export function parseMarkdownBlocks(content: string): MarkdownBlock[] {
  const blocks: MarkdownBlock[] = []
  const lines = content.replace(/\r\n?/g, '\n').split('\n')
  let index = 0
  let paragraphLines: string[] = []

  const flushParagraph = () => {
    if (paragraphLines.length === 0) return
    blocks.push({ type: 'paragraph', text: paragraphLines.join(' ') })
    paragraphLines = []
  }

  while (index < lines.length) {
    const line = lines[index]
    const trimmed = line.trim()

    if (!trimmed) {
      flushParagraph()
      index += 1
      continue
    }

    const fenceMatch = trimmed.match(/^```([a-zA-Z0-9_-]*)\s*$/)
    if (fenceMatch) {
      flushParagraph()
      const codeLines: string[] = []
      index += 1
      while (index < lines.length && !lines[index].trim().startsWith('```')) {
        codeLines.push(lines[index])
        index += 1
      }
      if (index < lines.length) index += 1
      blocks.push({ type: 'code', language: fenceMatch[1] || 'text', code: codeLines.join('\n') })
      continue
    }

    const headingMatch = trimmed.match(/^(#{1,6})\s+(.+)$/)
    if (headingMatch) {
      flushParagraph()
      blocks.push({ type: 'heading', level: headingMatch[1].length, text: headingMatch[2].trim() })
      index += 1
      continue
    }

    if (/^(-{3,}|\*{3,}|_{3,})$/.test(trimmed)) {
      flushParagraph()
      blocks.push({ type: 'rule' })
      index += 1
      continue
    }

    if (isTableHeader(lines, index)) {
      flushParagraph()
      const table = parseTable(lines, index)
      blocks.push(table.block)
      index = table.nextIndex
      continue
    }

    const unorderedMatch = trimmed.match(/^[-*]\s+(.+)$/)
    const orderedMatch = trimmed.match(/^\d+\.\s+(.+)$/)
    if (unorderedMatch || orderedMatch) {
      flushParagraph()
      const ordered = Boolean(orderedMatch)
      const items: string[] = []
      while (index < lines.length) {
        const itemLine = lines[index].trim()
        const itemMatch = ordered ? itemLine.match(/^\d+\.\s+(.+)$/) : itemLine.match(/^[-*]\s+(.+)$/)
        if (!itemMatch) break
        items.push(itemMatch[1].trim())
        index += 1
      }
      blocks.push({ type: 'list', ordered, items })
      continue
    }

    paragraphLines.push(trimmed)
    index += 1
  }

  flushParagraph()
  return blocks
}

function isTableHeader(lines: string[], index: number): boolean {
  if (index + 1 >= lines.length) return false
  const headerCells = parseTableRow(lines[index])
  const separatorCells = parseTableRow(lines[index + 1])
  if (headerCells.length < 2 || separatorCells.length !== headerCells.length) return false
  return separatorCells.every((cell) => /^:?-{3,}:?$/.test(cell.trim()))
}

function parseTable(lines: string[], startIndex: number): { block: Extract<MarkdownBlock, { type: 'table' }>; nextIndex: number } {
  const headers = parseTableRow(lines[startIndex])
  const alignments = parseTableRow(lines[startIndex + 1]).map(parseAlignment)
  const rows: string[][] = []
  let index = startIndex + 2

  while (index < lines.length) {
    const cells = parseTableRow(lines[index])
    if (cells.length === 0) break
    rows.push(normalizeTableRow(cells, headers.length))
    index += 1
  }

  return {
    block: {
      type: 'table',
      headers,
      alignments,
      rows,
    },
    nextIndex: index,
  }
}

function parseTableRow(line: string): string[] {
  const trimmed = line.trim()
  if (!trimmed.includes('|')) return []

  const normalized = trimmed.replace(/^\|/, '').replace(/\|$/, '')
  return normalized.split('|').map((cell) => cell.trim())
}

function parseAlignment(cell: string): TableAlignment {
  const trimmed = cell.trim()
  if (trimmed.startsWith(':') && trimmed.endsWith(':')) return 'center'
  if (trimmed.endsWith(':')) return 'right'
  return 'left'
}

function normalizeTableRow(cells: string[], expectedLength: number): string[] {
  if (cells.length === expectedLength) return cells
  if (cells.length > expectedLength) return cells.slice(0, expectedLength)
  return [...cells, ...Array.from({ length: expectedLength - cells.length }, () => '')]
}
