# TASK-120-03: Guided Surface Collapse and Discovery Preference

**Parent:** [TASK-120](./TASK-120_Macro_Tool_Layer_And_Guided_Surface_Collapse.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

---

## Objective

Once a first macro layer exists, collapse the guided surface further and bias
discovery toward macro paths.

---

## Repository Touchpoints

- `server/adapters/mcp/surfaces.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/platform/naming_rules.py`
- `server/router/infrastructure/tools_metadata/`
- `tests/unit/adapters/mcp/`

---

## Leaf Breakdown

| Leaf | Purpose |
|------|---------|
| [TASK-120-03-01](./TASK-120-03-01_Guided_Visibility_Collapse_For_Atomic_Tools.md) | Hide more atomics on `llm-guided` once bounded macro alternatives exist |
| [TASK-120-03-02](./TASK-120-03-02_Router_And_Search_Bias_Toward_Macro_Layer.md) | Bias discovery, search, and router suggestions toward the macro layer |

---

## Acceptance Criteria

- guided surfaces expose more capability with fewer visible low-level tools
- search and router suggestions prefer the macro layer before atomics
