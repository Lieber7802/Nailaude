import { marked } from 'marked'

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
export type MarkdownInlineNode =
  | { type: 'text'; text: string }
  | { type: 'code'; text: string }
  | { type: 'strong'; children: MarkdownInlineNode[] }

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

export function renderMarkdownToHtml(content: string): string {
  const html = marked.parse(content, {
    async: false,
    breaks: false,
    gfm: true,
  }) as string

  return addCodeLanguageLabels(addHeadingIds(html))
}

export function slugifyMarkdownHeading(text: string): string {
  return decodeHtmlEntities(stripHtmlTags(text))
    .trim()
    .toLowerCase()
    .replace(/[`~!@#$%^&*()+=[\]{}\\|;:'",.<>/?，。！？、；：“”‘’（）【】《》]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
}

function addHeadingIds(html: string): string {
  const seen = new Map<string, number>()

  return html.replace(/<h([1-6])>([\s\S]*?)<\/h\1>/g, (_fullMatch, level: string, body: string) => {
    const baseSlug = slugifyMarkdownHeading(body) || `heading-${seen.size + 1}`
    const count = seen.get(baseSlug) || 0
    seen.set(baseSlug, count + 1)
    const slug = count === 0 ? baseSlug : `${baseSlug}-${count + 1}`

    return `<h${level} id="${escapeHtmlAttribute(slug)}">${body}</h${level}>`
  })
}

function addCodeLanguageLabels(html: string): string {
  return html.replace(/<pre><code class="language-([^"]+)">/g, (_match, language: string) => {
    return `<pre data-language="${escapeHtmlAttribute(language.toUpperCase())}"><code class="language-${escapeHtmlAttribute(
      language
    )}">`
  })
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

    const fenceMatch = trimmed.match(/^(```|~~~)([a-zA-Z0-9_-]*)\s*$/)
    if (fenceMatch) {
      flushParagraph()
      const marker = fenceMatch[1]
      const codeLines: string[] = []
      index += 1
      while (index < lines.length && !lines[index].trim().startsWith(marker)) {
        codeLines.push(lines[index])
        index += 1
      }
      if (index < lines.length) index += 1
      blocks.push({ type: 'code', language: fenceMatch[2] || 'text', code: codeLines.join('\n') })
      continue
    }

    if (/^( {4}|\t)/.test(line)) {
      flushParagraph()
      const codeLines: string[] = []
      while (index < lines.length) {
        const codeLine = lines[index]
        if (!codeLine.trim()) {
          codeLines.push('')
          index += 1
          continue
        }
        if (!/^( {4}|\t)/.test(codeLine)) break
        codeLines.push(codeLine.startsWith('\t') ? codeLine.slice(1) : codeLine.slice(4))
        index += 1
      }
      blocks.push({ type: 'code', language: 'text', code: trimTrailingBlankLines(codeLines).join('\n') })
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

export function parseInlineMarkdown(text: string): MarkdownInlineNode[] {
  const nodes: MarkdownInlineNode[] = []
  let cursor = 0

  while (cursor < text.length) {
    const nextCode = text.indexOf('`', cursor)
    const nextStrong = text.indexOf('**', cursor)
    const candidates = [nextCode, nextStrong].filter((index) => index >= 0)

    if (candidates.length === 0) {
      pushText(nodes, text.slice(cursor))
      break
    }

    const nextToken = Math.min(...candidates)
    if (nextToken > cursor) pushText(nodes, text.slice(cursor, nextToken))

    if (text.startsWith('`', nextToken)) {
      const end = text.indexOf('`', nextToken + 1)
      if (end === -1) {
        pushText(nodes, text.slice(nextToken))
        break
      }
      nodes.push({ type: 'code', text: text.slice(nextToken + 1, end) })
      cursor = end + 1
      continue
    }

    const end = text.indexOf('**', nextToken + 2)
    if (end === -1) {
      pushText(nodes, text.slice(nextToken))
      break
    }
    nodes.push({ type: 'strong', children: parseInlineMarkdown(text.slice(nextToken + 2, end)) })
    cursor = end + 2
  }

  return nodes
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

function trimTrailingBlankLines(lines: string[]): string[] {
  const nextLines = [...lines]
  while (nextLines.length > 0 && nextLines[nextLines.length - 1] === '') {
    nextLines.pop()
  }
  return nextLines
}

function stripHtmlTags(value: string): string {
  return value.replace(/<[^>]*>/g, '')
}

function decodeHtmlEntities(value: string): string {
  return value
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&#x([0-9a-f]+);/gi, (_match, hex: string) => String.fromCodePoint(Number.parseInt(hex, 16)))
    .replace(/&#(\d+);/g, (_match, code: string) => String.fromCodePoint(Number.parseInt(code, 10)))
}

function escapeHtmlAttribute(value: string): string {
  return value.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

function pushText(nodes: MarkdownInlineNode[], text: string) {
  if (!text) return
  const previous = nodes[nodes.length - 1]
  if (previous?.type === 'text') {
    previous.text += text
    return
  }
  nodes.push({ type: 'text', text })
}
