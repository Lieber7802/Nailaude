import type { ProjectState, TeamBoard } from '../../../packages/shared/types'
import { fetchJSON } from './api'

export const orchestratorApi = {
  teamBoard: (conversationId: string) => fetchJSON<TeamBoard>(`/conversations/${conversationId}/team-board`),
  projectState: (conversationId: string) => fetchJSON<ProjectState>(`/conversations/${conversationId}/project-state`),
}
