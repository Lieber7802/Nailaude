import type { WSOrchestratorStatus } from '../../../../packages/shared/types'

const OrchestratorStatus = ({ snapshot }: { snapshot: WSOrchestratorStatus }) => (
  <article className="collaboration-card">
    <div className="collaboration-card__title">
      <span className="brand-dot">O</span>
      <strong>Orchestrator: {snapshot.status}</strong>
    </div>
    <p>{snapshot.reasoningSummary || snapshot.message}</p>
    {snapshot.queuePosition && <p>Queue position: {snapshot.queuePosition}</p>}
    {snapshot.warnings.map((warning) => (
      <p className="orchestrator-warning" key={warning}>{warning}</p>
    ))}
    {snapshot.batches.length > 0 && (
      <p>
        Batches: {snapshot.batches.map((batch) => `#${batch.index + 1} ${batch.status} (${batch.taskIds.join(', ')})`).join(' | ')}
      </p>
    )}
    <div className="collaboration-card__agents">
      {snapshot.tasks.map((task) => (
        <span className="task-pill" key={task.id}>
          {task.agentName}: {task.title}
          <strong>{task.status}</strong>
        </span>
      ))}
    </div>
  </article>
)

export default OrchestratorStatus
