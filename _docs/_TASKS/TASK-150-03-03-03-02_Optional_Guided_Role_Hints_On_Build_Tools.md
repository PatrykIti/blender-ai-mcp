# TASK-150-03-03-03-02: Optional Guided Role Hints On Build Tools

**Parent:** [TASK-150-03-03-03](./TASK-150-03-03-03_Guided_Register_Part_And_Role_Hint_Input_Path.md)
**Depends On:** [TASK-150-03-03-03-01](./TASK-150-03-03-03-01_Guided_Register_Part_Router_Tool_Surface.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High

## Objective

Evaluate and, if approved, wire an optional `guided_role` convenience path on
existing build tools without making it the only or primary role-registration
mechanism.

## Repository Touchpoints

- `server/adapters/mcp/guided_contract.py`
- `server/adapters/mcp/areas/modeling.py`

## Current Code Anchors

- `guided_contract.py` lines 147-166: guided canonicalization dispatch
- `areas/modeling.py` lines 282-369: create primitive
- `areas/modeling.py` lines 415-440+: transform object

## Planned Code Shape

```python
canonicalize_guided_tool_arguments(...):
    preserve optional guided_role / role_group

modeling_create_primitive(..., guided_role: str | None = None)
modeling_transform_object(..., guided_role: str | None = None)
```

## Acceptance Criteria

- optional role hints are either explicitly supported or explicitly rejected in
  a documented way
- canonical path remains clear even if the convenience path exists

## Planned Unit Test Scenarios

- `guided_role` is preserved through guided argument canonicalization when
  allowed
- unsupported hint shapes fail with one canonical error
- direct and proxied calls behave the same for `guided_role`

## Planned E2E / Transport Scenarios

- if implemented:
  - create primitive with `guided_role="body_core"` over stdio and verify the
    role registry updates without a second tool call
- if rejected:
  - transport-backed call returns the same actionable guidance on direct and
    proxied paths

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_search_surface.py`
