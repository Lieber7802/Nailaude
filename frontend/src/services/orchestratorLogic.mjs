export const shouldAcceptSnapshot = (current, incoming) =>
  !(current?.runId === incoming.runId && current.sequence >= incoming.sequence)

export const reconnectDelay = (attempt) => Math.min(4000, 250 * 2 ** attempt)

export const hasAllClarificationAnswers = (questions, answers) =>
  questions.every((question) => Boolean(answers[question.id]?.trim()))
