import type {
  Agent,
  AgentPlatform,
  ApiResponse,
  Conversation,
  CreateAgentDTO,
  CreateConversationDTO,
  Mention,
  Message as SharedMessage,
  PaginatedResponse,
} from '../../../packages/shared/types'

const API_BASE = '/api/v1'

export type {
  Agent,
  AgentPlatform,
  ApiResponse,
  Artifact,
  ArtifactFile,
  Conversation,
  CreateAgentDTO,
  CreateConversationDTO,
  Mention,
  PaginatedResponse,
  Task,
} from '../../../packages/shared/types'

export type CreateAgentInput = CreateAgentDTO
export type CreateConversationInput = CreateConversationDTO
export type Message = Omit<SharedMessage, 'metadata'> & {
  mentions?: Mention[]
  metadata: SharedMessage['metadata'] & { clientMessageId?: string }
}

export async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json', ...(options?.headers || {}) },
    ...options,
  })
  const payload = (await res.json()) as ApiResponse<T>
  if (!res.ok || !payload.success) {
    throw new Error(payload.error || `API Error: ${res.status}`)
  }
  return payload.data as T
}

export const conversationApi = {
  list: (page = 1, pageSize = 20, search = '') => {
    const params = new URLSearchParams({ page: String(page), pageSize: String(pageSize) })
    if (search.trim()) params.set('search', search.trim())
    return fetchJSON<PaginatedResponse<Conversation>>(`/conversations?${params.toString()}`)
  },
  create: (data: CreateConversationInput) =>
    fetchJSON<Conversation>('/conversations', { method: 'POST', body: JSON.stringify(data) }),
  get: (id: string) => fetchJSON<Conversation>(`/conversations/${id}`),
  delete: (id: string) => fetchJSON<{ id: string }>(`/conversations/${id}`, { method: 'DELETE' }),
}

export const agentApi = {
  list: () => fetchJSON<Agent[]>('/agents'),
  create: (data: CreateAgentInput) => fetchJSON<Agent>('/agents', { method: 'POST', body: JSON.stringify(data) }),
  get: (id: string) => fetchJSON<Agent>(`/agents/${id}`),
}

export const platformApi = {
  list: () => fetchJSON<AgentPlatform[]>('/platforms'),
}

export const messageApi = {
  list: (conversationId: string, page = 1, pageSize = 50) =>
    fetchJSON<PaginatedResponse<Message>>(
      `/conversations/${conversationId}/messages?page=${page}&pageSize=${pageSize}`
    ),
}

export function formatConversationLastMessage(author: string, content: string): string {
  const compactContent = content.trim().replace(/\s+/g, ' ')
  const preview = compactContent.length > 80 ? `${compactContent.slice(0, 77)}...` : compactContent
  return `${author}: ${preview}`
}

export function extractMentions(content: string, agents: Agent[], fallbackAgents: Agent[] = []): Mention[] {
  const mentions: Mention[] = []
  const sortedAgents = [...agents].sort((left, right) => right.name.length - left.name.length)

  for (const agent of sortedAgents) {
    const pattern = new RegExp(`(^|[\\s，。！？、,.!?;；:：])@${escapeRegExp(agent.name)}(?=$|[\\s，。！？、,.!?;；:：])`)
    if (pattern.test(content) && !mentions.some((mention) => mention.agentId === agent.id)) {
      mentions.push({ agentId: agent.id, agentName: agent.name })
    }
  }

  if (mentions.length > 0) return mentions
  if (fallbackAgents.length === 1) {
    return [{ agentId: fallbackAgents[0].id, agentName: fallbackAgents[0].name }]
  }
  return []
}

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}
