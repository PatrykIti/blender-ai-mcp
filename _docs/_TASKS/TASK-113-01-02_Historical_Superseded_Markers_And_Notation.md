# TASK-113-01-02: Historical Superseded Markers and Notation

**Parent:** [TASK-113-01](./TASK-113-01_Tool_Layering_Policy_And_Terminology.md)  
**Status:** ⏳ To Do  
**Priority:** 🟡 Medium

---

## Objective

Define how old docs should be marked when they describe now-superseded tool-surface assumptions.

---

## Exact Documentation Targets

- `_docs/_TASKS/*.md` where old tool assumptions remain historically useful
- `_docs/TOOLS_*.md`
- `_docs/_MCP_SERVER/README.md`
- any task docs that still assume flat public exposure as the preferred end-state

---

## Required Policy

- use a visible banner such as:
  - `Superseded by TASK-113 policy`
- retain old content for history where useful
- avoid silently editing history to look like the old plan never existed
- use strike-throughs sparingly; prefer short supersession notes plus backlinks

---

## Acceptance Criteria

- the repo has one standard method for historical preservation vs active policy
- future doc migration waves know when to rewrite vs when to mark superseded
