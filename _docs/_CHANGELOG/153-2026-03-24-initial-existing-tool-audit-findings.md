# 153 - 2026-03-24: Initial existing-tool audit findings

**Status**: ✅ Completed  
**Type**: Audit / Execution Backlog  
**Task**: TASK-114-01, TASK-114-02

---

## Summary

Completed the first actual audit pass after `TASK-113`.

This wave does not yet fix the underlying tool/docs drift everywhere.
It records the first concrete findings and turns them into a prioritized backlog.

---

## Findings (high level)

- user-facing docs still overuse the old “mega tools for LLM context optimization” framing
- some MCP area docstrings still encode older product assumptions like “preferred method” / `ALT TO`
- prompt and demo layers are much better aligned now, but demos still need a later cleanup so workflow-first is the stronger default
- the next code/doc wave should start with wording and semantics cleanup in the highest-signal tool areas before new measure/assert atomics land

---

## Files Modified (high level)

- `_docs/_TASKS/TASK-114-01*`
- `_docs/_TASKS/TASK-114-02*`
- `_docs/_CHANGELOG/README.md`
