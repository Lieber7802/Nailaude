export function shouldAcceptSnapshot(
  current: { runId: string; sequence: number } | undefined,
  incoming: { runId: string; sequence: number }
): boolean

export function reconnectDelay(attempt: number): number

export function hasAllClarificationAnswers(
  questions: Array<{ id: string }>,
  answers: Record<string, string>
): boolean
