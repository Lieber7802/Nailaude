# M3_0 Contracts Plan

## Goal
Freeze M3 shared and Python contracts before runtime work.

## Scope
- Update `packages/shared/types.ts` and `docs/API_SPEC.md`.
- Add `backend/app/schemas/orchestrator.py`.
- Add schema tests before implementation.

## Tests
- Parse all Planner result variants.
- Reject invalid dependencies, access modes, and empty acceptance criteria.

## Out Of Scope
- Runtime execution and UI behavior.
