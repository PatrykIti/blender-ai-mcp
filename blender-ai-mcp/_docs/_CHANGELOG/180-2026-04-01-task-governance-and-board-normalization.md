# 180. Task governance and board normalization

Date: 2026-04-01

## Summary

Normalized task-administration rules, clarified the changelog split between
historical repo work and release notes, and cleaned up task-tree drift around
the completed `TASK-121` vision wave.

## What Changed

- updated `AGENTS.md` with explicit rules for:
  - task hierarchy and promoted board scope
  - task completion checklist
  - `_docs/_CHANGELOG` vs root `CHANGELOG.md`
  - multi-agent work guidance
- updated `_docs/_TASKS/README.md` to clarify:
  - board scope
  - hierarchy rules
  - follow-on handling after a parent task is closed
- normalized the stale `TASK-121` branch so completed descendants are marked
  done and only the real Gemini follow-on stays open
- converted `TASK-121-04-01-05` from an open child of a closed parent into an
  explicit follow-on task
- expanded open `TASK-122` task docs so the umbrella, subtree tasks, and leaf
  tasks all carry stronger administrative and execution guidance

## Why

The repo had drift between board-level tracking, nested task-file statuses, and
the real state of the shipped `TASK-121` work. It also needed one explicit rule
that `_docs/_CHANGELOG` is the historical implementation log while root
`CHANGELOG.md` is reserved for semantic-release and release notes.
