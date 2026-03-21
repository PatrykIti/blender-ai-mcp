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

- Implement the concrete leaf scope implied by the parent task in the listed touchpoints.
- Keep responsibilities aligned with Clean Architecture and `RESPONSIBILITY_BOUNDARIES.md`.
- Avoid introducing new bootstrap side effects outside the platform composition root.

---

## Acceptance Criteria

- tool discovery no longer depends on LaBSE classifiers
---

## Atomic Work Items

1. Implement the leaf scope in the listed touchpoints.
2. Keep the implementation aligned with the parent task boundaries and the existing runtime call path.
