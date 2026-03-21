# TASK-095-02-01: Core Discovery Handoff from LaBSE to FastMCP Search

**Parent:** [TASK-095-02](./TASK-095-02_Discovery_Handoff_From_LaBSE_to_FastMCP_Search.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-084-02](./TASK-084-02_Search_Transform_and_Pinned_Entry_Surface.md)

---

## Objective

Implement the core code changes for **Discovery Handoff from LaBSE to FastMCP Search**.

---

## Repository Touchpoints

- `server/adapters/mcp/transforms/discovery.py`
- `server/adapters/mcp/platform/capability_manifest.py`
- `server/adapters/mcp/factory.py`
- `server/router/application/classifier/intent_classifier.py`
- `tests/unit/adapters/mcp/test_tool_inventory.py`
---

## Planned Work

### Deliverables

- implement the slice behavior end-to-end across: `server/adapters/mcp/transforms/discovery.py`, `server/adapters/mcp/platform/capability_manifest.py`, `server/adapters/mcp/factory.py`, `server/router/application/classifier/intent_classifier.py`
- keep ownership boundaries explicit (FastMCP platform vs router policy vs inspection truth)
- preserve the parent task contract so this slice can be merged independently

### Implementation Checklist

- touch `server/adapters/mcp/transforms/discovery.py` with an explicit change note (or explicit no-change rationale)
- touch `server/adapters/mcp/platform/capability_manifest.py` with an explicit change note (or explicit no-change rationale)
- touch `server/adapters/mcp/factory.py` with an explicit change note (or explicit no-change rationale)
- touch `server/router/application/classifier/intent_classifier.py` with an explicit change note (or explicit no-change rationale)
- touch `tests/unit/adapters/mcp/test_tool_inventory.py` with an explicit change note (or explicit no-change rationale)
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
