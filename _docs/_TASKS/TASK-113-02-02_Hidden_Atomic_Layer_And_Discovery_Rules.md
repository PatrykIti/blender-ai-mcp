# TASK-113-02-02: Hidden Atomic Layer and Discovery Rules

**Parent:** [TASK-113-02](./TASK-113-02_Surface_Exposure_Matrix_And_Hidden_Atomic_Layer.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

---

## Objective

Define how hidden atomic tools remain available internally without polluting the normal LLM-facing catalog.

---

## Exact Documentation Targets

- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
- any discovery/search docs under `_docs/_TASKS/TASK-084*`

---

## Required Rules

- hidden atomic tools should not appear in normal public bootstrap catalogs
- discovery should prioritize macro/workflow tools over raw atomic tools
- if an atomic tool is discoverable at all, its place should be justified explicitly
- internal/debug surfaces may still expose more of the atomic layer

---

## Acceptance Criteria

- hidden atomic tooling becomes an explicit platform rule
- search/discovery docs stop implying that “every tool is a normal public discovery candidate”
