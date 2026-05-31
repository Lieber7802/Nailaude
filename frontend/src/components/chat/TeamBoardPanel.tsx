import type { ProjectState, TeamBoard } from '../../../../packages/shared/types'

const TeamBoardPanel = ({ board, projectState }: { board?: TeamBoard; projectState?: ProjectState }) => {
  if (!board && !projectState) return null
  return (
    <details className="team-board-panel">
      <summary>Shared context {board ? `- Team Board v${board.version}` : ''}</summary>
      {board && (
        <>
          <p>Completed tasks: {board.progress.completedTaskIds.length}</p>
          <p>Open questions: {board.openQuestions.length}</p>
          <p>Recent notes: {board.recentNotes.length}</p>
        </>
      )}
      {projectState && (
        <>
          <p>Project State v{projectState.version}: {projectState.progressSummary || 'Facts refreshed'}</p>
          <p>Workspace files: {projectState.fileTree.totalFiles}</p>
        </>
      )}
    </details>
  )
}

export default TeamBoardPanel
