# TASK-119-01: Public Tool Semantics and Contract Hardening

**Parent:** [TASK-119](./TASK-119_Existing_Public_Surface_Hardening_After_TASK-113.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

---

## Objective

Normalize the behavior, wording, and structured result shape of the highest-value
public/grouped tools before the macro layer is introduced.

---

## Repository Touchpoints

- `server/adapters/mcp/areas/`
- `server/adapters/mcp/contracts/`
- `server/adapters/mcp/platform/naming_rules.py`
- `server/adapters/mcp/transforms/public_params.py`
- `server/adapters/mcp/contracts/compat.py`
- `tests/unit/adapters/mcp/`
- `tests/unit/tools/`

---

## Leaf Breakdown

| Leaf | Purpose |
|------|---------|
| [TASK-119-01-01](./TASK-119-01-01_Grouped_Tool_Semantic_Alignment.md) | Align grouped/public tool semantics, docstrings, and examples with the post-`TASK-113` model |
| [TASK-119-01-02](./TASK-119-01-02_Output_Schema_And_Result_Envelope_Normalization.md) | Normalize public output schemas and result envelopes across grouped/high-value tools |

---

## Acceptance Criteria

- grouped/public tools present one coherent public story
- argument names and hidden/expert-only flags are intentional and stable
- public contracts are consistent enough for later macro composition
