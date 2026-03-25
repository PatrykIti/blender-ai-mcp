# TASK-121-04: Lightweight Vision Runtime and Evaluation

**Parent:** [TASK-121](./TASK-121_Goal_Aware_Vision_Assist_And_Reference_Context.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

---

## Objective

Choose the lightweight vision runtime/model path and add enough evaluation and
governance to keep the feature bounded and trustworthy.

---

## Repository Touchpoints

- `server/adapters/mcp/sampling/`
- `server/infrastructure/config.py`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
- `_docs/_TESTS/README.md`
- `tests/unit/adapters/mcp/`
- `tests/e2e/`

---

## Leaf Breakdown

| Leaf | Purpose |
|------|---------|
| [TASK-121-04-01](./TASK-121-04-01_Small_Vision_Runtime_Selection_And_Execution_Policy.md) | Select the lightweight runtime/model strategy and define execution constraints |
| [TASK-121-04-02](./TASK-121-04-02_Evaluation_Harness_Goldens_And_Safety_Review.md) | Add evaluation datasets, goldens, and governance checks for the vision layer |

---

## Acceptance Criteria

- the vision layer has an explicit runtime/model strategy
- lightweight vision behavior is evaluated and governed before broad rollout
