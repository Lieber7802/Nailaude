const API_BASE = '/api/v1'

export interface ApiResponse<T> {
  success: boolean
  data: T | null
  error: string | null
  timestamp: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
}

export interface Agent {
  id: string
  name: string
  avatar: string
  description: string
  capabilities: string[]
  systemInstruction: string
  platformId: string
  isBuiltin: boolean
  createdAt: string
}

export interface Conversation {
  id: string
  title: string
  type: 'single' | 'group'
  workDir: string
  participantIds: string[]
  createdBy: string
  createdAt: string
  updatedAt: string
  lastMessage?: string
}

export interface Mention {
  agentId: string
  agentName: string
}

export interface Message {
  id: string
  conversationId: string
  role: 'user' | 'agent' | 'orchestrator' | 'system' | 'team_activity'
  agentId: string | null
  agentName?: string
  content: string
  contentType: 'text' | 'code' | 'mixed'
  artifacts: Artifact[]
  parentMessageId: string | null
  metadata: Record<string, unknown>
  mentions?: Mention[]
  createdAt: string
}

export interface ArtifactFile {
  name: string
  content: string
  language: string
}

export interface Artifact {
  id: string
  messageId: string
  type: string
  title: string
  files: ArtifactFile[]
  diffData: unknown | null
  version: number
  previousVersionId: string | null
  previewUrl: string | null
  createdAt: string
}

export interface CreateConversationInput {
  title?: string
  type: 'single' | 'group'
  workDir: string
  participantIds: string[]
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
  list: (page = 1, pageSize = 20) =>
    fetchJSON<PaginatedResponse<Conversation>>(`/conversations?page=${page}&pageSize=${pageSize}`),
  create: (data: CreateConversationInput) =>
    fetchJSON<Conversation>('/conversations', { method: 'POST', body: JSON.stringify(data) }),
  get: (id: string) => fetchJSON<Conversation>(`/conversations/${id}`),
  delete: (id: string) => fetchJSON<{ id: string }>(`/conversations/${id}`, { method: 'DELETE' }),
}

export const agentApi = {
  list: () => fetchJSON<Agent[]>('/agents'),
  get: (id: string) => fetchJSON<Agent>(`/agents/${id}`),
}

export const messageApi = {
  list: (conversationId: string, page = 1, pageSize = 50) =>
    fetchJSON<PaginatedResponse<Message>>(
      `/conversations/${conversationId}/messages?page=${page}&pageSize=${pageSize}`
    ),
}
