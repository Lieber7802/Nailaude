# M5 UI Bugfix Checklist

## Docs
- [x] Plan created or updated
- [x] Checklist created or updated

## Implementation
- [x] Contract reviewed
- [x] Tests written first
- [x] Conversation list time uses real timestamps
- [x] Custom Agent button moved below new conversation button with matching size
- [x] Message artifacts default to first 5 with expand/collapse
- [x] Collaboration status shows duration and error/blocked styling
- [x] Narrow preview viewport buttons hide labels and keep icons
- [x] Narrow preview zoom controls shrink to the pane width
- [x] Wide preview zoom controls keep compact width without empty filler
- [x] Conversation list scrolls inside the left sidebar instead of being clipped
- [x] Workspace empty state hides Mock implementation copy
- [x] Empty right preview hides unsupported-webpage copy
- [x] Fullscreen Markdown preview fills the preview panel
- [x] Completed task snapshots do not restart duration after refresh
- [x] Backend runtime emits authoritative task `startedAt` / `endedAt`
- [x] Frontend runtime duration uses backend task timestamps
- [x] Left search conversation/message UI removed
- [x] Conversation rows keep content height when the list has extra space
- [x] Custom Agent management supports list/create/delete

## Verification
- [x] Targeted frontend tests pass
- [x] Targeted backend tests pass
- [x] Frontend build passes
- [x] DEVLOG updated
- [x] Sidebar scroll regression test passes
- [x] Experience polish regression tests pass
- [x] Runtime timing regression test passes
