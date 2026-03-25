# TASK-120-04: Macro Validation and Adoption

**Parent:** [TASK-120](./TASK-120_Macro_Tool_Layer_And_Guided_Surface_Collapse.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

---

## Objective

Protect the macro layer with regression/benchmark coverage and roll it into the
public guidance stack cleanly.

---

## Repository Touchpoints

- `tests/unit/`
- `tests/e2e/`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_PROMPTS/`
- `_docs/_TESTS/README.md`

---

## Leaf Breakdown

| Leaf | Purpose |
|------|---------|
| [TASK-120-04-01](./TASK-120-04-01_Macro_Regression_And_Benchmark_Pack.md) | Protect macro contracts, visibility effects, and public payload size with automated checks |
| [TASK-120-04-02](./TASK-120-04-02_Prompt_Instruction_And_Workflow_Integration.md) | Update prompts/instructions/workflows so models naturally adopt the macro layer |

---

## Acceptance Criteria

- macro behavior and surface effects are regression-protected
- prompts and guided instructions actively teach the new macro layer
