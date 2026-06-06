import type { Agent, Task } from '../services/api'
import type { OrchestratorRunStatus } from '../../../packages/shared/types'

export type CollaborationAgentTone = 'done' | 'pending' | 'danger' | 'warning' | 'idle'

export interface CollaborationTaskTiming {
  startedAt: number
  endedAt?: number
}

export interface VisibleCollaborationAgent {
  durationMs?: number
  id: string
  name: string
  status: string
  tone: CollaborationAgentTone
}

export function visibleCollaborationAgents(
  participantAgents: Pick<Agent, 'id' | 'name'>[],
  tasks: Pick<Task, 'agentName' | 'status'>[],
  thinkingAgents: string[],
  taskTimings: Record<string, CollaborationTaskTiming> = {},
  now = Date.now()
): VisibleCollaborationAgent[] {
  const activeNames = new Set([...tasks.map((task) => task.agentName), ...thinkingAgents])
  const visibleAgents = participantAgents.filter((agent) => activeNames.has(agent.name))

  if (visibleAgents.length === 0 && activeNames.size === 0) {
    return participantAgents.map((agent) => ({ id: agent.id, name: agent.name, status: '等待中', tone: 'idle' }))
  }

  return visibleAgents.map((agent) => {
    const task = tasks.find((item) => item.agentName === agent.name)
    const isThinking = thinkingAgents.includes(agent.name)
    const durationMs = taskDurationMs(taskTimings[agent.name], now)
    const visibleAgent: VisibleCollaborationAgent = {
      id: agent.id,
      name: agent.name,
      status: isThinking ? '思考中' : taskStatusLabel(task?.status),
      tone: isThinking ? 'pending' : taskStatusTone(task?.status),
    }
    if (durationMs !== undefined) visibleAgent.durationMs = durationMs
    return visibleAgent
  })
}

export function taskStatusLabel(status?: Task['status']): string {
  if (status === 'completed') return '已完成'
  if (status === 'running') return '进行中'
  if (status === 'failed') return '失败'
  if (status === 'cancelled') return '已终止'
  if (status === 'blocked') return '已阻塞'
  return '等待中'
}

export function taskStatusTone(status?: Task['status']): CollaborationAgentTone {
  if (status === 'completed') return 'done'
  if (status === 'running') return 'pending'
  if (status === 'failed' || status === 'cancelled') return 'danger'
  if (status === 'blocked') return 'warning'
  return 'idle'
}

export function formatTaskDuration(durationMs?: number): string {
  if (durationMs === undefined) return ''
  const safeDuration = Math.max(0, durationMs)
  const totalSeconds = Math.round(safeDuration / 1000)

  if (totalSeconds < 60) {
    return `${(safeDuration / 1000).toFixed(totalSeconds < 10 ? 1 : 0)}s`
  }

  const minutes = Math.floor(totalSeconds / 60)
  const seconds = totalSeconds % 60
  return seconds > 0 ? `${minutes}m ${seconds}s` : `${minutes}m`
}

export function batchStatusLabel(status: string): string {
  if (status === 'completed') return '已完成'
  if (status === 'running') return '进行中'
  if (status === 'failed') return '失败'
  if (status === 'partial') return '部分完成'
  if (status === 'cancelled') return '已终止'
  return '等待中'
}

function taskDurationMs(timing: CollaborationTaskTiming | undefined, now: number): number | undefined {
  if (!timing) return undefined
  return Math.max(0, (timing.endedAt ?? now) - timing.startedAt)
}

export function orchestratorStatusLabel(status: OrchestratorRunStatus): string {
  const labels: Record<OrchestratorRunStatus, string> = {
    queued: '排队中',
    planning: '规划中',
    awaiting_input: '等待补充信息',
    validating: '校验中',
    replanning: '重新规划中',
    awaiting_approval: '等待确认',
    executing: '执行中',
    summarizing: '总结中',
    completed: '已完成',
    failed: '失败',
    cancelled: '已终止',
  }
  return labels[status]
}

export function orchestratorMessageLabel(status: OrchestratorRunStatus, message: string): string {
  if (message.startsWith('Executing batch')) return '正在执行任务批次'
  if (message.startsWith('Completed batch')) return '任务批次已完成'
  if (message === 'Run completed') return '运行已完成'
  if (message === 'Run cancelled') return '运行已终止'
  if (message === 'Run queued') return '任务已排队'
  if (message === 'Starting orchestrator run') return '正在启动协作流程'
  if (message === 'Finalizing shared state') return '正在整理协作状态'
  return orchestratorStatusLabel(status)
}

export function visibleOrchestratorWarnings(warnings: string[]): string[] {
  return warnings.filter(
    (warning) =>
      !warning.startsWith('Project summary unavailable:') &&
      !warning.startsWith('Team Board summary unavailable:')
  )
}
