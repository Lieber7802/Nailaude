import { Button, Input, Tag } from 'antd'
import { useState } from 'react'
import type { PlannerResult } from '../../../../packages/shared/types'
import { hasAllClarificationAnswers } from '../../services/orchestratorLogic.mjs'
import { wsClient } from '../../services/websocket'

type Requirement = Extract<PlannerResult, { status: 'needs_clarification' | 'capability_gap' }>

const OrchestratorInputCard = ({ runId, result }: { runId: string; result: Requirement }) => {
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [sendError, setSendError] = useState<string | null>(null)
  if (result.status === 'capability_gap') {
    return (
      <article className="collaboration-card">
        <strong>Additional agent capability required</strong>
        <p>{result.missingCapabilities.join(', ')}</p>
        {result.recommendedAgents.map((agent) => (
          <Button
            key={agent.agentId}
            onClick={() => {
              const sent = wsClient.send({
                type: 'orchestrator_input_response',
                data: { runId, approvedAgentIds: [agent.agentId] },
              })
              setSendError(sent ? null : 'WebSocket is disconnected. Reconnect before adding this agent.')
            }}
          >
            Add recommended agent: {agent.reason}
          </Button>
        ))}
        {sendError && <p role="alert">{sendError}</p>}
      </article>
    )
  }

  return (
    <article className="collaboration-card">
      <strong>Planner needs clarification</strong>
      {result.questions.map((question) => (
        <section key={question.id}>
          <strong>{question.question}</strong>
          <p>{question.reason}</p>
          <div className="orchestrator-actions">
            {question.options.map((option) => (
              <Button
                className={answers[question.id] === option.id ? 'is-active' : ''}
                key={option.id}
                onClick={() => setAnswers((current) => ({ ...current, [question.id]: option.id }))}
              >
                {option.label} {option.recommended && <Tag color="orange">Recommended</Tag>}
              </Button>
            ))}
          </div>
          {question.allowCustomInput && (
            <div className="orchestrator-actions">
              <Input
                value={answers[question.id] || ''}
                onChange={(event) => setAnswers((current) => ({ ...current, [question.id]: event.target.value }))}
                placeholder="Add details"
              />
            </div>
          )}
        </section>
      ))}
      <Button
        disabled={!hasAllClarificationAnswers(result.questions, answers)}
        type="primary"
        onClick={() => {
          const sent = wsClient.send({ type: 'orchestrator_input_response', data: { runId, answers } })
          setSendError(sent ? null : 'WebSocket is disconnected. Your answers were kept for retry.')
        }}
      >
        Submit answers
      </Button>
      {sendError && <p role="alert">{sendError}</p>}
    </article>
  )
}

export default OrchestratorInputCard
