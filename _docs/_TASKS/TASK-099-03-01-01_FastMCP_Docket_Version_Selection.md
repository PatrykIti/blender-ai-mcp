# TASK-099-03-01-01: FastMCP Docket Version Selection

**Parent:** [TASK-099-03-01](./TASK-099-03-01_Core_Upstream_Version_Alignment.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-099-02](./TASK-099-02_Runtime_Guards_and_Shim_Containment.md)

---

## Objective

Choose and encode the supported FastMCP+Docket version pair for this repo.

---

## Repository Touchpoints

- `pyproject.toml`
- `poetry.lock`
- `_docs/_MCP_SERVER/runtime_baseline_matrix.md`

---

## Planned Work

- compare feasible supported version pairs
- encode the supported choice in repo dependency policy

### Selection Criteria

- compatibility with current TASK-088 task mode
- compatibility with current FastMCP 3.x platform work already merged
- minimization of repo-local patching
- clarity of install/lock behavior for maintainers and CI

---

## Acceptance Criteria

- the repo has one explicit supported task-runtime pair
