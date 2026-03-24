# TASK-113-01-01: Canonical Policy Doc and Ownership

**Parent:** [TASK-113-01](./TASK-113-01_Tool_Layering_Policy_And_Terminology.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

---

## Objective

Decide exactly which `_docs/` file becomes the canonical policy source for the new tool-layering strategy.

---

## Exact Documentation Targets

- create or repurpose one canonical doc, likely one of:
  - `_docs/_MCP_SERVER/TOOL_LAYERING_POLICY.md`
  - `_docs/_MCP_SERVER/README.md` with a clearly delimited canonical policy section
  - `_docs/ARCHITECTURE.md` with links out to a dedicated policy file
- add explicit backlinks from:
  - `_docs/_MCP_SERVER/README.md`
  - `_docs/AVAILABLE_TOOLS_SUMMARY.md`
  - `_docs/_TASKS/README.md`
  - `README.md`

---

## Required Content

- problem statement
- layered tool model
- public-surface rules
- `set_goal`-first policy
- vision/assertion boundary
- ownership statement:
  - which docs define policy
  - which docs are inventory/reference only

---

## Acceptance Criteria

- the canonical policy location is unambiguous
- every major doc points back to it rather than redefining the rules ad hoc
