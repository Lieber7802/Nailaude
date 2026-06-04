import type { Artifact } from '../services/api'
import { isMarkdownFile } from './markdownPreview.ts'

export type ArtifactCardKind = 'code' | 'diff' | 'markdown' | 'webpage' | 'file'

export interface ArtifactCardPresentation {
  actionLabel: string
  detail: string
  kind: ArtifactCardKind
  title: string
}

export function getOrderedMessageArtifacts(artifacts: Artifact[]): Artifact[] {
  return [...artifacts].sort((left, right) => artifactMessageOrder(left) - artifactMessageOrder(right))
}

export function getOutputArtifacts(artifacts: Artifact[]): Artifact[] {
  return artifacts.filter((artifact) => artifact.type !== 'diff')
}

export function getChangeArtifacts(artifacts: Artifact[]): Artifact[] {
  return artifacts.filter((artifact) => artifact.type === 'diff' && artifact.diffData)
}

export function getArtifactCardPresentation(artifact: Artifact): ArtifactCardPresentation {
  const firstFile = artifact.files[0]
  const lineCount = firstFile?.content ? firstFile.content.split('\n').length : 0
  const byteCount = firstFile?.content.length || 0

  if (artifact.type === 'diff') {
    return {
      actionLabel: '在右侧查看',
      detail: `+${artifact.diffData?.additions || 0} / -${artifact.diffData?.deletions || 0} · ${
        artifact.diffData?.file || 'diff'
      }`,
      kind: 'diff',
      title: artifact.title,
    }
  }

  if (artifact.type === 'webpage') {
    return {
      actionLabel: '在右侧预览',
      detail: `${artifact.previewUrl ? '可预览' : '无预览链接'} · ${artifact.files.length || 1} 个文件`,
      kind: 'webpage',
      title: artifact.title,
    }
  }

  const markdown = isMarkdownFile(firstFile)
  return {
    actionLabel: markdown ? '在右侧预览' : '在右侧查看',
    detail: `${(firstFile?.language || artifact.type).toUpperCase()} · ${lineCount} 行 · ${formatBytes(byteCount)}`,
    kind: markdown ? 'markdown' : artifact.type === 'file' ? 'file' : 'code',
    title: artifact.title,
  }
}

export function formatBytes(chars: number): string {
  if (chars <= 0) return '0 B'
  const kb = chars / 1024
  return kb >= 1 ? `${kb.toFixed(1)} KB` : `${chars} B`
}

function artifactMessageOrder(artifact: Artifact): number {
  if (artifact.type === 'diff') return 30
  if (artifact.type === 'webpage') return 20
  return 10
}
