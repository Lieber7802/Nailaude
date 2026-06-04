# M3 Agent Chain Blockers Checklist

## Docs

- [x] Spec created for the three blockers.
- [x] Plan created for implementation and verification.
- [x] DEVLOG updated with final changes and evidence.

## Research

- [x] WSL OpenCode CLI `run --format json` observed returning only protocol events.
- [x] WSL OpenCode server API observed returning nested assistant text.
- [x] DeepSeek direct API observed healthy while `LLMClient.health_check()` returned false.
- [x] Real WSL group chain observed review text plus failed review task.
- [x] Real WSL Codex review handoff reproduced DeepSeek bridge failures after reading generated workspace files.
- [x] Real WSL planner smoke showed a too-small generic plan when prompt/validation did not enforce explicit multi-Agent coverage.

## Tests First

- [x] RED test for `LLMClient.health_check()` semantic `ok: true` and sufficient token budget.
- [x] RED test allowing no-change review/validation tasks with summary text.
- [x] RED test preserving failure for no-change build/write tasks.
- [x] RED test for OpenCode server response text extraction.
- [x] RED test for OpenCode adapter server execution path.
- [x] RED test for runtime executor exceptions preserving task metadata for shared-state refresh.
- [x] RED test for Codex bridge truncating oversized tool outputs.
- [x] RED test for Codex bridge including DeepSeek error response bodies.
- [x] RED test for Codex bridge preserving DeepSeek `reasoning_content` across tool-call turns.
- [x] RED test for grouping consecutive Responses `function_call` items before Chat Completions tool outputs.
- [x] RED test for planner replan when explicit mentions or requested stages are omitted.
- [x] RED test for Markdown-wrapped planner JSON content parsing and invalid JSON diagnostics.
- [x] RED test for DeepSeek loose planner aliases and top-level dependency tables.
- [x] RED test for repairing a copied-invalid agent id from task stage/capability context.
- [x] RED test for enforcing app-stage dependencies through README after review.

## Implementation

- [x] `LLMClient.health_check()` fixed.
- [x] Runtime no-change review/validation task classification implemented.
- [x] OpenCode server/API execution path implemented.
- [x] Runtime executor exception fallback preserves `taskId`, `agentId`, and `batchId`.
- [x] Codex isolated homes are created outside `/tmp` for WSL.
- [x] Codex prompts are sent through stdin.
- [x] `ProcessPoolError` reports stdout when stderr is empty.
- [x] DeepSeek bridge truncates large tool outputs, preserves reasoning content, and groups tool calls.
- [x] Planner prompt and contextual coverage validation preserve multi-Agent staged workflows.
- [x] Planner prompt now specifies exact schema shapes, field names, agent id copy rules, and hard JSON-only output.
- [x] Planner normalization handles loose DeepSeek aliases, access aliases, copied-invalid agent ids, and common staged DAG ordering.
- [x] `LLMClient.request_json()` accepts Markdown-wrapped or embedded JSON objects and surfaces bounded raw-content previews on parse failure.
- [x] WebSocket planner materializes participant/catalog agents before reuse.
- [x] CLI parser kept as fallback/helper.
- [x] No shared type changes introduced.
- [x] MockAdapter preserved.
- [x] Planner validation regression tests aligned with available-agent catalog enforcement.
- [x] WebSocket planner wrapper test aligned with planner `available_agent_ids` signature.

## Verification

- [x] Targeted WSL tests pass.
- [x] Broader M3 WebSocket/e2e tests pass or residual failures are explained.
- [x] Real WSL smoke shows OpenCode model text, artifact creation, Codex review text, and no false failed review task.
- [x] Real WSL handoff repro shows Codex review task completes after bridge fixes.
- [x] Real WSL three-Agent chain completes four staged tasks with no warnings using an ASCII prompt.
- [x] Real WSL Chinese planner smoke returns four staged tasks for requirements, implementation, review, and README.
- [x] Real WSL Pomodoro planner-only stability check passed 10/10 attempts with no planner failures and no bad staged DAG.
- [x] Backend full test attempt timed out after 304 seconds; targeted changed-area tests were rerun successfully.
- [x] Windows workspace and WSL workspace statuses reviewed.
- [x] Local macOS targeted regression tests pass for validator and WebSocket planner wrapper.
