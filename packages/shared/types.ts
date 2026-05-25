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

export type TaskStatus = "pending" | "running" | "completed" | "failed";
export type ExecutionMode = "sequential" | "parallel";

export interface Task {
  id: string;
  agentId: UUID;          // 分派给哪个 Agent
  agentName: string;      // 冗余：Agent 角色名
  instruction: string;    // 任务指令
  status: TaskStatus;
  dependsOn: string | null; // 依赖的前置任务 ID
  result?: string;        // 完成后的结果摘要
}

export interface DispatchPlan {
  tasks: Task[];
  executionMode: ExecutionMode;
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

export type WSClientMessage = WSSendMessage | WSStopGeneration;

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

export interface WSOrchestratorStatus {
  status: "dispatching" | "executing" | "summarizing";
  tasks: Task[];
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
  | { type: "message_done"; data: WSMessageDone }
  | { type: "error"; data: WSError };

// ─────────────────────────────────────────────────
// Team Protocol
// ─────────────────────────────────────────────────

export interface TeamNote {
  from: string;         // Agent 角色名
  to: string;           // "all" 或指定 Agent 名
  decisions: string[];
  headsUp: string;
  questions: string[];
  createdAt: Timestamp;
}

export interface TeamDecision {
  decision: string;
  madeBy: string;       // Agent 角色名
  reason: string;
  agreedBy?: string;
  createdAt: Timestamp;
}

export interface TeamBoard {
  conversationId: UUID;
  teamMembers: Array<{ name: string; role: string; strengths: string }>;
  teamDecisions: TeamDecision[];
  codeStandards: Record<string, string>;
  progress: {
    completed: string[];
    inProgress: { agent: string; task: string } | null;
    pending: string[];
  };
  agentNotes: TeamNote[];
  updatedAt: Timestamp;
}

// ─────────────────────────────────────────────────
// 项目状态
// ─────────────────────────────────────────────────

export interface ProjectState {
  name: string;
  techStack: string[];
  fileTree: string[];
  decisions: string[];
  preferences: string[];
  progress: string;
  recentChanges: Array<{
    file: string;
    summary: string;
    agent: string;
  }>;
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
