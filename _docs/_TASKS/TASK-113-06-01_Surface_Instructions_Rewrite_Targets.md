# TASK-113-06-01: Surface Instructions Rewrite Targets

**Parent:** [TASK-113-06](./TASK-113-06_Surface_Instructions_And_Prompt_Layer_Rewrite.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

---

## Objective

List the exact surface `instructions` updates required by the new strategy.

---

## Exact Documentation / Code Targets

- `server/adapters/mcp/surfaces.py`
- `_docs/_MCP_SERVER/README.md`

---

## Required Rewrite Areas

- `llm-guided`
  - `set_goal`-first
  - small public catalog
  - macro/workflow preference
  - verify/measure/assert guidance
- `legacy-manual`
  - maintainer/manual-only positioning
- `legacy-flat`
  - compatibility/control positioning, not preferred product path
- `internal-debug`
  - maintainer/debug scope

---

## Acceptance Criteria

- each surface instruction block aligns with the new architecture, not the old flat-catalog mentality
**Completion Summary:** `surfaces.py` instructions now distinguish production vs manual/debug/experimental surfaces and explicitly describe goal-first, hidden-layer, and verification expectations where appropriate.
