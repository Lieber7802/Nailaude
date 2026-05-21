const API_BASE = '/api/v1'

export async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) throw new Error(`API Error: ${res.status}`)
  return res.json()
}

// Conversation API
export const conversationApi = {
  list: () => fetchJSON('/conversations'),
  create: (data: unknown) =>
    fetchJSON('/conversations', { method: 'POST', body: JSON.stringify(data) }),
  get: (id: string) => fetchJSON(`/conversations/${id}`),
  delete: (id: string) =>
    fetchJSON(`/conversations/${id}`, { method: 'DELETE' }),
}

// Agent API
export const agentApi = {
  list: () => fetchJSON('/agents'),
  create: (data: unknown) =>
    fetchJSON('/agents', { method: 'POST', body: JSON.stringify(data) }),
  get: (id: string) => fetchJSON(`/agents/${id}`),
}

// Message API
export const messageApi = {
  list: (conversationId: string) =>
    fetchJSON(`/conversations/${conversationId}/messages`),
}
