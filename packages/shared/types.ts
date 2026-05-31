// ═══════════════════════════════════════════════════════════════
// AgentHub Shared Types
// 基于 PRD v1.6 + TECH_DESIGN v1.1 设计的 MVP 共享类型定义
// ═══════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────
// 基础类型
// ─────────────────────────────────────────────────

export type UUID = string;
export type Timestamp = string; // ISO 8601

// ─────────────────────────────────────────────────
// Agent 平台层（用户不可见）
// ─────────────────────────────────────────────────

export type PlatformId = "mock" | "llm" | "opencode" | "codex";
export type PlatformStatus = "available" | "not_installed" | "error" | "unknown";

export interface AgentPlatform {
  id: PlatformId;
  name: string;
  binaryPath: string;
  config: Record<string, unknown>; // api_key, model, extra_args 等
  status: PlatformStatus;
}

// ─────────────────────────────────────────────────
// Agent 角色层（用户可见）
// ─────────────────────────────────────────────────

export interface Agent {
  id: UUID;
  name: string;            // 用户看到的角色名："代码工匠"
  avatar: string;          // emoji 或图片 URL
  description: string;     // 能力描述（面向用户）
  capabilities: string[];  // 能力标签：["代码生成", "前端"]
  systemInstruction: string; // 附加指令（传给底层 Agent）
  platformId: PlatformId;  // 绑定的底层平台（用户不可见）
  isBuiltin: boolean;
  createdAt: Timestamp;
}

export interface CreateAgentDTO {
  name: string;
  avatar?: string;
  description: string;
  capabilities: string[];
  systemInstruction?: string;
  platformId?: PlatformId; // 可选，默认自动选择
}

// ─────────────────────────────────────────────────
// 会话（统一使用 Conversation，不混用 Session）
// ─────────────────────────────────────────────────

export type ConversationType = "single" | "group";

export interface Conversation {
  id: UUID;
  title: string;
  type: ConversationType;
  workDir: string;              // 用户指定的项目目录
  participantIds: UUID[];       // 参与的 Agent ID 列表
  participants?: Agent[];       // 填充后的 Agent 对象（前端用）
  createdBy: UUID;
  createdAt: Timestamp;
  updatedAt: Timestamp;
  lastMessage?: string;         // 最近一条消息摘要（列表展示用）
}

export interface CreateConversationDTO {
  title?: string;
  type: ConversationType;
  workDir: string;
  participantIds: UUID[];
}

// ─────────────────────────────────────────────────
// 消息
// ─────────────────────────────────────────────────

export type MessageRole = "user" | "agent" | "orchestrator" | "system" | "team_activity";
export type ContentType = "text" | "code" | "mixed";

/** @ 提及的 Agent */
export interface Mention {
  agentId: UUID;
  agentName: string;
}

export interface Message {
  id: UUID;
  conversationId: UUID;
  role: MessageRole;
  agentId: UUID | null;         // Agent 角色 ID（agent/team_activity 消息）
  agentName?: string;           // 冗余：Agent 角色名（前端渲染用）
  content: string;
  contentType: ContentType;
  artifacts: Artifact[];
  parentMessageId: UUID | null; // 引用回复
  metadata: MessageMetadata;
  createdAt: Timestamp;
}

export interface MessageMetadata {
  tokenUsage?: number;
  executionTime?: number;       // ms
  platform?: PlatformId;        // 实际执行的平台
}

export interface SendMessageDTO {
  content: string;
  mentions: Mention[];           // @ 提及的 Agent
  parentMessageId?: UUID;        // 引用回复
}

// ─────────────────────────────────────────────────
// 产物 (Artifact)
// ─────────────────────────────────────────────────

export type ArtifactType =
  | "code"
  | "webpage"
  | "diff"
  | "document"
  | "file"
  | "log"
  | "deploy_status";

export interface ArtifactFile {
  name: string;       // 文件名（含相对路径）
  content: string;    // 文件内容
  language: string;   // 语言标识（jsx, html, css, etc）
}

export interface DiffHunk {
  oldStart: number;
  oldLines: number;
  newStart: number;
  newLines: number;
  content: string;    // unified diff 文本
}

export interface DiffData {
  file: string;
  hunks: DiffHunk[];
  additions: number;
  deletions: number;
  oldContent?: string;
  newContent?: string;
}

export interface Artifact {
  id: UUID;
  messageId: UUID;
  type: ArtifactType;
  title: string;                // 展示标题
  files: ArtifactFile[];        // 代码/文档类型使用
  diffData: DiffData | null;    // diff 类型使用
  version: number;
  previousVersionId: UUID | null;
  previewUrl: string | null;    // 网页预览 URL
  createdAt: Timestamp;
}

// ─────────────────────────────────────────────────
// Orchestrator 任务调度
// ─────────────────────────────────────────────────

export type TaskStatus = "pending" | "ready" | "running" | "completed" | "failed" | "blocked" | "cancelled";
export type ExecutionMode = "sequential" | "parallel";
export type AccessMode = "read" | "write";
export type BatchStatus = "pending" | "running" | "completed" | "partial" | "failed" | "cancelled";
export type OrchestratorRunStatus =
  | "queued"
  | "planning"
  | "awaiting_input"
  | "validating"
  | "replanning"
  | "awaiting_approval"
  | "executing"
  | "summarizing"
  | "completed"
  | "failed"
  | "cancelled";

export interface RiskHints {
  mayDeleteOrRenameFiles: boolean;
  mayTouchConfigFiles: boolean;
  estimatedFilesTouched: number;
}

export interface Task {
  id: string;
  agentId: UUID;          // 分派给哪个 Agent
  agentName: string;      // 冗余：Agent 角色名
  title: string;
  objective: string;
  instruction: string;    // 任务指令
  acceptanceCriteria: string[];
  constraints: string[];
  accessMode: AccessMode;
  status: TaskStatus;
  dependsOn: string[];     // 语义依赖的前置任务 ID
  priority: number;
  riskHints: RiskHints;
  result?: string;        // 完成后的结果摘要
}

export interface DispatchPlan {
  tasks: Task[];
  executionMode: ExecutionMode;
}

export interface PlanningQuestionOption {
  id: string;
  label: string;
  recommended: boolean;
}

export interface PlanningQuestion {
  id: string;
  question: string;
  reason: string;
  options: PlanningQuestionOption[];
  allowCustomInput: boolean;
}

export interface RecommendedAgent {
  agentId: UUID;
  reason: string;
}

export type PlannerResult =
  | { status: "ready"; reasoningSummary: string; tasks: Task[] }
  | { status: "needs_clarification"; questions: PlanningQuestion[] }
  | { status: "capability_gap"; missingCapabilities: string[]; recommendedAgents: RecommendedAgent[] }
  | { status: "cannot_plan"; reason: string; recoverable: boolean };

export interface PlannerContext {
  userRequest: string;
  mentions: Mention[];
  clarificationAnswers: Record<string, string>[];
  participants: Pick<Agent, "id" | "name" | "description" | "capabilities">[];
  availableAgentCatalog: Pick<Agent, "id" | "name" | "description" | "capabilities">[];
  projectPlanningSummary: Partial<ProjectState>;
  teamBoardSummary: Partial<TeamBoard>;
  recentConversationSummary: Array<Pick<Message, "role" | "content">>;
  fileTreeSummary: string[];
  previousValidationErrors: string[];
}

// ─────────────────────────────────────────────────
// Agent 输入/输出（Adapter 层）
// ─────────────────────────────────────────────────

export interface ContextPayload {
  systemInstruction: string;           // Layer 0
  projectState: ProjectState | null;   // Layer 1
  relevantFiles: ArtifactFile[];       // Layer 2
  relevantHistory: Message[];          // Layer 2
  teamBoard: TeamBoard | null;         // Team Protocol
  teamNotes: TeamNote[];               // 来自队友的便签
}

export interface AgentInput {
  workDir: string;
  instruction: string;
  context: ContextPayload;
}

export type AgentOutputStatus = "success" | "failed" | "partial";

export interface AgentOutput {
  status: AgentOutputStatus;
  content: string;         // 完整回复文本
  filesChanged: string[];  // 变更的文件路径列表
  teamNote: TeamNote | null;
  artifacts: Artifact[];
  error?: string;          // status 为 failed/partial 时的错误描述
}

export interface TaskResult {
  status: AgentOutputStatus;
  summary: string;
  filesRead: string[];
  filesChanged: string[];
  filesCreated: string[];
  filesDeleted: string[];
  warnings: string[];
  teamNotes: TeamNote[];
  error?: string;
}

export interface AgentHandoffEnvelope {
  runId: UUID;
  taskId: string;
  batchId: string;
  workspace: { path: string; accessMode: AccessMode; snapshotId: string };
  task: Task;
  collaboration: {
    projectSummary: string;
    teamStandards: CodeStandard[];
    relevantTeamNotes: TeamNote[];
    dependencyResults: TaskResult[];
  };
  navigationHints: { inspectFirst: string[]; changedFiles: string[]; diffSummary: string };
  manifest: { estimatedTokens: number; warnings: string[]; omittedItems: string[] };
}

// ─────────────────────────────────────────────────
// Agent 事件流（Adapter 内部，后端使用）
// ─────────────────────────────────────────────────

export type AgentEventType =
  | "text_delta"
  | "file_created"
  | "file_modified"
  | "done"
  | "error"
  | "team_note";

export interface AgentEvent {
  type: AgentEventType;
  content: string;
  metadata: Record<string, unknown>;
}

// ─────────────────────────────────────────────────
// WebSocket 消息协议（Discriminated Union）
// ─────────────────────────────────────────────────

// ── 客户端 → 服务器 ──

export interface WSSendMessage {
  type: "send_message";
  data: SendMessageDTO;
}

export interface WSStopGeneration {
  type: "stop_generation";
  data: { messageId: UUID };
}

export interface WSOrchestratorInputResponse {
  type: "orchestrator_input_response";
  data: { runId: UUID; answers?: Record<string, string>; approvedAgentIds?: UUID[] };
}

export interface WSOrchestratorApprovalResponse {
  type: "orchestrator_approval_response";
  data: { runId: UUID; approved: boolean };
}

export type WSClientMessage =
  | WSSendMessage
  | WSStopGeneration
  | WSOrchestratorInputResponse
  | WSOrchestratorApprovalResponse;

// ── 服务器 → 客户端 ──

export interface WSAgentThinking {
  agentId: UUID;
  agentName: string;
}

export interface WSTextDelta {
  messageId: UUID;
  agentName: string;
  delta: string;
}

export interface WSArtifact {
  messageId: UUID;
  artifact: Artifact;
}

export interface WSUserMessage extends Message {
  clientMessageId?: string;
}

export interface OrchestratorBatch {
  id: string;
  index: number;
  status: BatchStatus;
  taskIds: string[];
}

export interface WSOrchestratorStatus {
  runId: UUID;
  sequence: number;
  status: OrchestratorRunStatus;
  message: string;
  reasoningSummary: string;
  currentBatchIndex: number | null;
  totalBatches: number;
  tasks: Task[];
  batches: OrchestratorBatch[];
  warnings: string[];
  queuePosition?: number;
  teamBoardVersion: number;
  projectStateVersion: number;
  createdAt: Timestamp;
  updatedAt: Timestamp;
}

export interface WSTeamActivity {
  fromAgent: string;
  to: string;         // "all" 或指定 Agent 名
  content: string;
  noteType: "decision" | "heads_up" | "question";
}

export interface WSMessageDone {
  messageId: UUID;
  agentName: string;
}

export interface WSError {
  messageId?: UUID;
  error: string;
  recoverable: boolean;
}

export type WSServerMessage =
  | { type: "user_message"; data: WSUserMessage }
  | { type: "agent_thinking"; data: WSAgentThinking }
  | { type: "text_delta"; data: WSTextDelta }
  | { type: "orchestrator_status"; data: WSOrchestratorStatus }
  | { type: "artifact"; data: WSArtifact }
  | { type: "team_activity"; data: WSTeamActivity }
  | { type: "orchestrator_input_required"; data: { runId: UUID; result: Extract<PlannerResult, { status: "needs_clarification" | "capability_gap" }> } }
  | { type: "orchestrator_approval_required"; data: { runId: UUID; reason: string; tasks: Task[] } }
  | { type: "team_board_updated"; data: { conversationId: UUID; version: number } }
  | { type: "project_state_updated"; data: { conversationId: UUID; version: number } }
  | { type: "message_done"; data: WSMessageDone }
  | { type: "error"; data: WSError };

// ─────────────────────────────────────────────────
// Team Protocol
// ─────────────────────────────────────────────────

export interface TeamNote {
  id: UUID;
  conversationId: UUID;
  sourceTaskId: string;
  fromAgentId: UUID;
  fromAgentName: string;
  to: { type: "all" } | { type: "agent"; agentId: UUID };
  type: "decision" | "standard" | "heads_up" | "question" | "answer";
  content: string;
  relatedFiles: string[];
  relatedTaskIds: string[];
  resolvesNoteId?: UUID;
  status: "active" | "resolved" | "superseded" | "archived";
  injectionCount: number;
  lastInjectedAt?: Timestamp;
  createdAt: Timestamp;
  resolvedAt?: Timestamp;
}

export interface TeamDecision {
  id: UUID;
  content: string;
  rationale: string;
  madeByAgentId: UUID;
  madeByAgentName: string;
  sourceTaskId: string;
  status: "active" | "review_required" | "superseded";
  supersedesDecisionId?: UUID;
  createdAt: Timestamp;
  updatedAt: Timestamp;
}

export interface CodeStandard {
  id: UUID;
  category: "naming" | "structure" | "style" | "testing" | "security" | "other";
  content: string;
  sourceTaskId: string;
  status: "active" | "review_required" | "superseded";
  supersedesStandardId?: UUID;
  updatedAt: Timestamp;
}

export interface TeamQuestion {
  id: UUID;
  content: string;
  sourceTaskId: string;
  status: "active" | "resolved";
}

export interface TeamProgress {
  completedTaskIds: string[];
  activeTaskIds: string[];
  blockedTaskIds: string[];
  pendingTaskIds: string[];
  currentFocus: string;
}

export interface TeamBoard {
  conversationId: UUID;
  version: number;
  teamMembers: Array<{ agentId: UUID; name: string; role: string; capabilities: string[] }>;
  decisions: TeamDecision[];
  codeStandards: CodeStandard[];
  openQuestions: TeamQuestion[];
  progress: TeamProgress;
  recentNotes: TeamNote[];
  updatedAt: Timestamp;
}

// ─────────────────────────────────────────────────
// 项目状态
// ─────────────────────────────────────────────────

export interface ProjectState {
  conversationId: UUID;
  version: number;
  workspace: {
    name: string;
    workDir: string;
    scannedAt: Timestamp;
    fingerprint: string;
  };
  techStack: string[];
  fileTree: { totalFiles: number; paths: string[]; truncated: boolean };
  git: {
    isRepository: boolean;
    branch?: string;
    headCommit?: string;
    dirty: boolean;
    recentCommits: Array<{ sha: string; message: string }>;
  };
  progressSummary: string;
  recentChanges: Array<{
    file: string;
    changeType: "created" | "modified" | "deleted" | "renamed";
    summary: string;
    source: "agent" | "external";
    agentId?: UUID;
    taskId?: string;
    batchId?: string;
    createdAt: Timestamp;
  }>;
  warnings: string[];
  updatedAt: Timestamp;
}

// ─────────────────────────────────────────────────
// Skill / Rule 配置
// ─────────────────────────────────────────────────

export type SkillTrigger = "after_code_generation" | "on_mention" | "on_keyword" | "manual";

export interface SkillRule {
  id: UUID;
  name: string;           // 规则名称
  description: string;
  trigger: SkillTrigger;
  triggerCondition: string; // 触发条件（关键词、正则等）
  action: {
    agentId: UUID;        // 触发后调用哪个 Agent
    instruction: string;  // 自动生成的指令模板
  };
  enabled: boolean;
  createdAt: Timestamp;
}

// ─────────────────────────────────────────────────
// API 响应包装
// ─────────────────────────────────────────────────

export interface ApiResponse<T = unknown> {
  success: boolean;
  data: T | null;
  error: string | null;
  timestamp: Timestamp;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}
