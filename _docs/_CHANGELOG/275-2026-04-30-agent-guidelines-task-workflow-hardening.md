# 275. Agent guidelines task workflow hardening

Date: 2026-04-30
Version: -

## Summary

- expanded `AGENTS.md` with a mandatory task-start checklist for reading task
  docs, owner code, tests, and area contracts before implementation
- added repo-specific guidance for branch/worktree isolation, execution-ready
  leaves, runtime/security contract notes, and validation by dependency shape
- clarified contract ownership, schema-first payload handling, no test-only
  production fallbacks, and manual commit validation expectations

## Validation

- docs-only change; ran `git diff --check`
