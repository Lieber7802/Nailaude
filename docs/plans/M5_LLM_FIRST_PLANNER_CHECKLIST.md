# M5 LLM-first Planner Checklist

## Docs
- [x] Plan created or updated
- [x] Checklist created or updated
- [x] Shared types reviewed; no change needed
- [x] API behavior note updated
- [x] DEVLOG updated

## Tests First
- [x] Ecommerce requirements task with page wording preserves product architect agent id
- [x] Review task with implementation/page wording preserves review agent id
- [x] Valid agent id wins even when agentName conflicts
- [x] Invalid agent id still repairs through name or stage fallback
- [x] Explicit read access is not keyword-forced to write
- [x] True omission of explicitly mentioned agent still fails after replan

## Implementation
- [x] `_resolve_agent_id()` trusts valid participant ids first
- [x] Stage/profile inference downgraded to fallback
- [x] Explicit `accessMode` no longer keyword-overridden
- [x] Structural validation, mention coverage, and replan behavior retained
- [x] Frontend, WebSocket protocol, and shared types untouched

## Verification
- [x] Targeted planner tests pass
- [x] WebSocket orchestration smoke tests pass
- [x] Full backend tests pass or reason recorded
- [x] `git diff --check` passes
- [x] Manual ecommerce four-agent dispatch smoke pending noted; planner regression test covers the same failure path
