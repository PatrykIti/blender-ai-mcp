# TASK-114-01: Public Tool Semantics and Docstring Audit

**Parent:** [TASK-114](./TASK-114_Existing_Tool_Surface_Audit_And_Alignment.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

---

## Objective

Audit the actual MCP-facing tool descriptions and semantics for drift against the new layered product model.

---

## Repository Touchpoints

- `server/adapters/mcp/areas/*.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `README.md`

---

## Planned Work

- identify tool docstrings that still imply the old flat-catalog mindset
- identify tools described as more autonomous/open-ended than they should be
- identify tools whose wording should move toward:
  - atomic helper
  - macro tool
  - workflow tool
  - verification/measure/assert support

---

## Acceptance Criteria

- the repo has a concrete list of MCP-facing tool semantics that need rewriting
- the audit distinguishes wording drift from actual missing capability
