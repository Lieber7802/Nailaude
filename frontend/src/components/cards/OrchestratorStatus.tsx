import { CheckCircleFilled, CloseCircleFilled, LoadingOutlined, PauseCircleFilled } from '@ant-design/icons'
import type { WSOrchestratorStatus } from '../../../../packages/shared/types'
import {
  orchestratorMessageLabel,
  orchestratorStatusLabel,
  batchStatusLabel,
  taskStatusLabel,
  visibleOrchestratorWarnings,
} from '../../utils/orchestratorUi'

const OrchestratorStatus = ({ snapshot }: { snapshot: WSOrchestratorStatus }) => {
  const warnings = visibleOrchestratorWarnings(snapshot.warnings)

  return (
    <article className="collaboration-card orchestrator-card">
      <div className="collaboration-card__title">
        <span className="brand-dot">主</span>
        <strong>主智能体：{orchestratorStatusLabel(snapshot.status)}</strong>
      </div>
      <p>{snapshot.reasoningSummary || orchestratorMessageLabel(snapshot.status, snapshot.message)}</p>
      {snapshot.queuePosition && <p>队列位置：第 {snapshot.queuePosition} 位</p>}
      {warnings.map((warning) => (
        <p className="orchestrator-warning" key={warning}>
          {warning}
        </p>
      ))}
      {snapshot.batches.length > 0 && (
        <p>
          批次：
          {snapshot.batches
            .map((batch) => `第 ${batch.index + 1} 批 ${batchStatusLabel(batch.status)}`)
            .join(' ｜ ')}
        </p>
      )}
      {snapshot.tasks.length > 0 && (
        <ul className="orchestrator-task-list" aria-label="任务清单">
          {snapshot.tasks.map((task) => (
            <li className={`orchestrator-task orchestrator-task--${task.status}`} key={task.id}>
              <span className="orchestrator-task__icon">{taskIcon(task.status)}</span>
              <span className="orchestrator-task__title">{task.title}</span>
              <strong>{taskStatusLabel(task.status)}</strong>
            </li>
          ))}
        </ul>
      )}
    </article>
  )
}

const taskIcon = (status: string) => {
  if (status === 'running') return <LoadingOutlined />
  if (status === 'completed') return <CheckCircleFilled />
  if (status === 'failed' || status === 'cancelled') return <CloseCircleFilled />
  return <PauseCircleFilled />
}

export default OrchestratorStatus
