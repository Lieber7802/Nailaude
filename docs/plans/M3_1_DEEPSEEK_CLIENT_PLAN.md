# M3_1 DeepSeek Client Plan

## Goal
Provide a reusable DeepSeek OpenAI-compatible client and LLM adapter.

## Scope
- Backend-only config, injectable transport, JSON and streaming requests.
- Timeout, one retry, usage metadata, clear missing-key errors.

## Tests
- Fake transport JSON, stream, retry, timeout, usage, adapter event flow.
