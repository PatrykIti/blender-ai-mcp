# TASK-084-01-01: Core Tool Inventory Normalization and Discovery Taxonomy

**Parent:** [TASK-084-01](./TASK-084-01_Tool_Inventory_Normalization_and_Discovery_Taxonomy.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** None

---

## Objective

Implement the core code changes for **Tool Inventory Normalization and Discovery Taxonomy**.

---

## Repository Touchpoints

- `server/router/infrastructure/metadata_loader.py`
- `server/router/infrastructure/tools_metadata/**`
- `server/adapters/mcp/areas/*.py`
- `server/adapters/mcp/dispatcher.py`

---

## Planned Work

- Implement the primary code changes described in the parent task.
- Keep responsibilities aligned with Clean Architecture and `RESPONSIBILITY_BOUNDARIES.md`.
- Avoid introducing new bootstrap side effects outside the platform composition root.

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-084-01-01-01](./TASK-084-01-01-01_Capability_Manifest_Schema_and_Tags.md) | Capability Manifest Schema and Tags | Core slice |
| [TASK-084-01-01-02](./TASK-084-01-01-02_Inventory_Builder_and_Enrichment.md) | Inventory Builder and Enrichment | Core slice |

---

## Acceptance Criteria

- Core implementation is complete and aligned with the parent scope.

---

## Atomic Work Items

1. Apply the core changes in the relevant adapters/handlers.
2. Verify the core flow still matches the expected execution path.
