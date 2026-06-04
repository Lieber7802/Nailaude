import type { Agent, Task } from '../services/api'
import type { OrchestratorRunStatus } from '../../../packages/shared/types'

export function visibleCollaborationAgents(
  participantAgents: Pick<Agent, 'id' | 'name'>[],
  tasks: Pick<Task, 'agentName' | 'status'>[],
  thinkingAgents: string[]
): Array<{ id: string; name: string; status: string }> {
  const activeNames = new Set([...tasks.map((task) => task.agentName), ...thinkingAgents])
  const visibleAgents = participantAgents.filter((agent) => activeNames.has(agent.name))

  if (visibleAgents.length === 0 && activeNames.size === 0) {
    return participantAgents.map((agent) => ({ id: agent.id, name: agent.name, status: '等待中' }))
  }

  return visibleAgents.map((agent) => {
    const task = tasks.find((item) => item.agentName === agent.name)
    return {
      id: agent.id,
      name: agent.name,
      status: thinkingAgents.includes(agent.name) ? '思考中' : taskStatusLabel(task?.status),
    }
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

export function batchStatusLabel(status: string): string {
  if (status === 'completed') return '已完成'
  if (status === 'running') return '进行中'
  if (status === 'failed') return '失败'
  if (status === 'partial') return '部分完成'
  if (status === 'cancelled') return '已终止'
  return '等待中'
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
