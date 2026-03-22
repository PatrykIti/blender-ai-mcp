# TASK-094-02: Read-Only Code Mode Pilot Surface

**Parent:** [TASK-094](./TASK-094_Code_Mode_Exploration.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-094-01](./TASK-094-01_Code_Mode_Experiment_Design_and_Guardrails.md)

---

## Objective

Build a read-only pilot surface for discovery, inspection, and workflow exploration use cases.

---

## Repository Touchpoints

- `server/adapters/mcp/factory.py`
- `server/adapters/mcp/surfaces.py`
- `server/adapters/mcp/settings.py`
- `server/adapters/mcp/transforms/discovery.py`
- `tests/unit/adapters/mcp/test_server_factory.py`

### Boundary Rule

Code Mode pilot work belongs to the MCP platform composition layer.
Do not fork or rewrite business handlers just to expose a read-only Code Mode surface.
The pilot may orchestrate only existing MCP capabilities on the composed server surface and must not expose raw Python or direct `bpy` execution.

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-094-02-01](./TASK-094-02-01_Core_Read_Code_Pilot.md) | Core Read-Only Code Mode Pilot Surface | Core implementation layer |
| [TASK-094-02-02](./TASK-094-02-02_Tests_Read_Code_Pilot.md) | Tests and Docs Read-Only Code Mode Pilot Surface | Tests, docs, and QA |

---

## Acceptance Criteria

- the pilot surface does not expose direct destructive write paths by default
- pilot behavior is delivered through profile composition and transforms, not handler-layer forks
- the pilot surface preserves the tools-only execution model and does not create a raw-code escape hatch
