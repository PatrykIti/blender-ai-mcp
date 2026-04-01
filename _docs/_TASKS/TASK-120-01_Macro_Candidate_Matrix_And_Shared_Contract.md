# TASK-120-01: Macro Candidate Matrix and Shared Contract

**Parent:** [TASK-120](./TASK-120_Macro_Tool_Layer_And_Guided_Surface_Collapse.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** The first bounded macro families are now explicitly selected from existing workflows, and a shared macro report envelope/status model exists in code/tests for later macro implementation work.

---

## Objective

Choose the first bounded macro families and define one shared contract/report
shape before any macro implementation work starts.

---

## Repository Touchpoints

- `server/router/application/workflows/custom/`
- `server/adapters/mcp/contracts/`
- `server/adapters/mcp/areas/`
- `server/adapters/mcp/platform/`
- `_docs/_MCP_SERVER/README.md`
- `tests/unit/adapters/mcp/`

---

## Leaf Breakdown

| Leaf | Purpose |
|------|---------|
| [TASK-120-01-01](./TASK-120-01-01_Macro_Candidate_Extraction_And_Selection_Rubric.md) | Extract the strongest macro candidates from existing workflows and public grouped-tool pain points |
| [TASK-120-01-02](./TASK-120-01-02_Shared_Macro_Report_Envelope_And_Status_Vocabulary.md) | Define one reusable report/result contract for the macro layer |

---

## Acceptance Criteria

- first macro candidates are chosen by explicit criteria, not ad hoc taste
- all later macro tools can share one bounded report/result vocabulary
