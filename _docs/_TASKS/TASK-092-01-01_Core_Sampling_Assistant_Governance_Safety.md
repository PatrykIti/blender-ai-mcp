# TASK-092-01-01: Core Sampling Assistant Governance and Safety Boundaries

**Parent:** [TASK-092-01](./TASK-092-01_Sampling_Assistant_Governance_and_Safety_Boundaries.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-095](./TASK-095_LaBSE_Semantic_Layer_Boundaries.md)

---

## Objective

Implement the core code changes for **Sampling Assistant Governance and Safety Boundaries**.

---

## Repository Touchpoints

- `server/adapters/mcp/sampling/assistant_runner.py`
- `server/adapters/mcp/sampling/result_types.py`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
- `tests/unit/adapters/mcp/test_assistant_runner.py`
---

## Planned Work

- Implement the concrete leaf scope implied by the parent task in the listed touchpoints.
- Keep responsibilities aligned with Clean Architecture and `RESPONSIBILITY_BOUNDARIES.md`.
- Avoid introducing new bootstrap side effects outside the platform composition root.

---

## Acceptance Criteria

- assistant usage boundaries are explicit and aligned with the semantic/safety/truth split
---

## Atomic Work Items

1. Implement the leaf scope in the listed touchpoints.
2. Keep the implementation aligned with the parent task boundaries and the existing runtime call path.
