# TASK-113-04-01: Macro Tool Definition and Boundaries

**Parent:** [TASK-113-04](./TASK-113-04_Macro_And_Workflow_Tool_Design_Rules.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

---

## Objective

Define the default LLM-facing tool layer: macro tools.

---

## Exact Documentation Targets

- `_docs/_MCP_SERVER/README.md`
- `README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`

---

## Required Rules

- macro tools represent one meaningful task responsibility
- they may orchestrate atomic tools internally
- they should return task-relevant structured outputs
- they should not become open-ended process engines

---

## Acceptance Criteria

- future contributors can distinguish a macro tool from both an atomic helper and a workflow process tool
**Completion Summary:** Macro tools are now explicitly documented as the default LLM-facing layer: one meaningful task responsibility, possibly orchestrating atomics internally, but not open-ended process engines.
