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

### Deliverables

- implement the slice behavior end-to-end across: `server/adapters/mcp/sampling/assistant_runner.py`, `server/adapters/mcp/sampling/result_types.py`, `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`, `tests/unit/adapters/mcp/test_assistant_runner.py`
- keep ownership boundaries explicit (FastMCP platform vs router policy vs inspection truth)
- preserve the parent task contract so this slice can be merged independently

### Implementation Checklist

- touch `server/adapters/mcp/sampling/assistant_runner.py` with an explicit change note (or explicit no-change rationale)
- touch `server/adapters/mcp/sampling/result_types.py` with an explicit change note (or explicit no-change rationale)
- touch `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md` with an explicit change note (or explicit no-change rationale)
- touch `tests/unit/adapters/mcp/test_assistant_runner.py` with an explicit change note (or explicit no-change rationale)
- add or update focused regression coverage for the changed slice behavior
- capture one before/after example of the affected runtime surface (payload, config, or execution flow)

### Review Notes To Attach

- short rationale for every changed touchpoint
- explicit note of any deferred work (if present) and why it is safe to defer
- exact test commands used for slice validation

---

## Acceptance Criteria

- every listed touchpoint is either updated or explicitly marked as no-change with justification
- the slice has at least one focused regression test proving intended behavior
- no boundary violations are introduced relative to `RESPONSIBILITY_BOUNDARIES.md`
- parent-level behavior remains compatible when this slice lands alone

---

## Atomic Work Items

1. Implement the scoped behavior in the listed touchpoints with explicit boundary ownership.
2. Add/adjust regression tests for the changed behavior and verify deterministic outcomes.
3. Record before/after evidence for the changed surface (contract, visibility, routing, or runtime behavior).
4. Document any deferred edges and why they do not block parent-task acceptance.
