# M2 DeepSeek Adapter Checklist

## Docs
- [x] Plan created.
- [x] Checklist created.
- [x] API docs reviewed; existing `PUT /agents/{id}` and `llm` platform examples remain aligned.

## Implementation
- [x] Contract reviewed.
- [x] Tests written first and verified failing.
- [x] `LLMProviderAdapter` streams DeepSeek text deltas.
- [x] Missing DeepSeek API key yields adapter `error` then `done`.
- [x] `AgentManagerService` creates and health-checks adapters.
- [x] WebSocket dispatch uses Agent platform adapters.
- [x] Agent update supports API-spec `PUT`.

## Verification
- [x] Targeted backend tests pass.
- [x] Backend suite passes.
- [x] Frontend build passes.
- [x] DEVLOG updated.
