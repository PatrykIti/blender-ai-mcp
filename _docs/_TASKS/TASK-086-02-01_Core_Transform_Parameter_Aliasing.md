# TASK-086-02-01: Core Transform-Based Tool and Parameter Aliasing

**Parent:** [TASK-086-02](./TASK-086-02_Transform_Based_Tool_and_Parameter_Aliasing.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-086-01](./TASK-086-01_Public_Surface_Manifest_and_Naming_Conventions.md)

---

## Objective

Implement the core code changes for **Transform-Based Tool and Parameter Aliasing**.

---

## Repository Touchpoints

- `server/adapters/mcp/transforms/naming.py`
- `server/adapters/mcp/transforms/public_params.py`
- `server/adapters/mcp/factory.py`
- `server/adapters/mcp/surfaces.py`
- `server/adapters/mcp/platform/capability_manifest.py`
- `server/adapters/mcp/platform/public_contracts.py`
- `server/adapters/mcp/router_helper.py`
- `server/adapters/mcp/dispatcher.py`
- `tests/unit/adapters/mcp/test_aliasing_transform.py`

---

## Planned Work

- create:
  - `server/adapters/mcp/transforms/naming.py`
  - `server/adapters/mcp/transforms/public_params.py`
  - `tests/unit/adapters/mcp/test_aliasing_transform.py`

### FastMCP Mechanism

Prefer built-in FastMCP `ToolTransform` with `ArgTransform`-style argument reshaping.
Custom code in this repo should mostly translate manifest rules into transform configuration.
---

## Acceptance Criteria

- aliases are applied at the public surface layer
- internal handler signatures remain stable
---

## Atomic Work Items

1. Translate manifest-owned public tool aliases into transform configuration instead of renaming handlers or dispatcher methods.
2. Translate public parameter aliases and hidden backend-only args into argument transforms for the first high-value capabilities: `scene_context`, `scene_inspect`, `mesh_inspect`, `router_set_goal`, and `workflow_catalog`.
3. Keep canonical internal names stable so router execution, dispatcher lookup, and metadata alignment continue to operate on one internal contract.
