import { Button } from 'antd'
import { useState } from 'react'
import { wsClient } from '../../services/websocket'

const OrchestratorApprovalCard = ({ runId, reason }: { runId: string; reason: string }) => {
  const [sendError, setSendError] = useState<string | null>(null)
  const sendApproval = (approved: boolean) => {
    const sent = wsClient.send({ type: 'orchestrator_approval_response', data: { runId, approved } })
    setSendError(sent ? null : 'WebSocket is disconnected. Reconnect before submitting approval.')
  }

  return (
    <article className="collaboration-card">
      <strong>Elevated write approval required</strong>
      <p>{reason}</p>
      <div className="orchestrator-actions">
        <Button onClick={() => sendApproval(false)}>Reject</Button>
        <Button type="primary" onClick={() => sendApproval(true)}>
          Allow execution
        </Button>
      </div>
      {sendError && <p role="alert">{sendError}</p>}
    </article>
  )
}

export default OrchestratorApprovalCard
