# TASK-113-02-03: Public Catalog Curation and Escape Hatches

**Parent:** [TASK-113-02](./TASK-113-02_Surface_Exposure_Matrix_And_Hidden_Atomic_Layer.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium

**Completion Summary:** The docs now define escape-hatch public atomics as explicit exceptions rather than the default surface model, with `router_set_goal`, `router_get_status`, and truth/inspection tools called out as the typical allowed class.

---

## Objective

Define the handful of public single-purpose tools that are still allowed even in a macro/workflow-first surface.

---

## Exact Documentation Targets

- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- prompt docs that teach public-tool usage

---

## Examples To Classify

- truth/inspection essentials
- explicit measure/assert tools
- small number of emergency/escape-hatch actions
- `router_set_goal` / `router_get_status`

---

## Acceptance Criteria

- the repo has a documented “allowed public atomics” rule
- public catalogs stay intentionally small instead of growing by convenience
