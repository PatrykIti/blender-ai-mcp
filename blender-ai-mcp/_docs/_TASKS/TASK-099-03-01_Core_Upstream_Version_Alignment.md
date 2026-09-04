# TASK-099-03-01: Core Upstream Version Alignment

**Parent:** [TASK-099-03](./TASK-099-03_Upstream_Version_Alignment_and_Validation.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-099-03](./TASK-099-03_Upstream_Version_Alignment_and_Validation.md)

---

## Objective

Implement the dependency/version selection work needed for one supported FastMCP+Docket pair.

---

## Repository Touchpoints

- `pyproject.toml`
- `poetry.lock`
- `_docs/_MCP_SERVER/runtime_baseline_matrix.md`

---

## Planned Work

- pick the supported version pair
- pin, constrain, or upgrade the repo baseline accordingly
- document the supported pair explicitly

### Dependency Policy Detail

- decide whether the repo should pin `fastmcp` more tightly
- decide whether the repo should declare the task runtime extra/dependency pair explicitly instead of relying on transitive resolution
- keep runtime baseline docs aligned with the actual dependency policy

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-099-03-01-01](./TASK-099-03-01-01_FastMCP_Docket_Version_Selection.md) | FastMCP Docket Version Selection | Dependency policy slice |
| [TASK-099-03-01-02](./TASK-099-03-01-02_Real_Task_Runtime_Validation.md) | Real Task Runtime Validation | Runtime validation slice |

---

## Acceptance Criteria

- dependency policy and selected pair are implemented in repo configuration/docs
