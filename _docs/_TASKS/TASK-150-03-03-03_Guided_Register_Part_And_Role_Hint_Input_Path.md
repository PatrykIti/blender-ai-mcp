# TASK-150-03-03-03: Guided Register Part And Role Hint Input Path

**Parent:** [TASK-150-03-03](./TASK-150-03-03_Generic_Families_Part_Roles_And_Execution_Enforcement.md)
**Depends On:** [TASK-150-03-03-02](./TASK-150-03-03-02_Guided_Part_Role_Registry_And_Session_Contracts.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Add the minimal input path for assigning object roles to the guided server
without multiplying the public tool surface into one macro/mega tool per
domain part.

## Repository Touchpoints

- `server/adapters/mcp/areas/router.py`
- `server/adapters/mcp/contracts/router.py`
- `server/adapters/mcp/session_capabilities.py`
- `tests/unit/adapters/mcp/`

## Acceptance Criteria

- the runtime has one bounded way to register/confirm part roles
- the design supports either:
  - one small helper tool such as `guided_register_part(...)`
  - or one narrow optional role-hint path for existing build tools
- the solution does not require a separate build tool per part/domain

## Detailed Implementation Notes

- this leaf should explicitly compare the two intended input paths:
  - helper tool:
    - `guided_register_part(object_name=..., role=...)`
  - optional role hint on existing build/create paths:
    - `guided_role=...`
- prefer the smallest surface that still gives the server deterministic
  semantics
- if both paths exist, define which one is canonical and which one is only a
  narrow convenience path

## Current Code Anchors

- `server/adapters/mcp/areas/router.py`
  - lines 330-396: current `router_set_goal(...)` goal bootstrap pattern
  - top-of-file router public tool registration list
- `server/adapters/mcp/guided_contract.py`
  - lines 147-166: current guided canonicalization switchboard
- `server/adapters/mcp/areas/modeling.py`
  - lines 282-369: `_modeling_create_primitive_impl`
  - lines 415-440+: `_modeling_transform_object_impl`

## Pseudocode Sketch

```python
@mcp.tool
async def guided_register_part(
    ctx: Context,
    object_name: str,
    role: str,
    role_group: str | None = None,
) -> GuidedFlowStateContract: ...

def canonicalize_guided_tool_arguments(name, arguments):
    if canonical_name in {"modeling_create_primitive", "modeling_transform_object"}:
        # optionally preserve guided_role / role_group if present
        ...
```

## Planned Unit Test Scenarios

- role registration updates session state and public flow summary
- invalid roles are rejected with actionable guidance
- optional build-tool role hints either normalize cleanly or fail with one
  canonical error path

## Planned E2E / Transport Scenarios

- stdio guided creature session:
  - create body primitive
  - register `body_core`
  - status reflects one completed primary role
- streamable same-session flow:
  - role registration unlocks the next search surface without a manual session
    reset

## Execution Structure

| Order | Micro-Leaf | Purpose |
|------|------------|---------|
| 1 | [TASK-150-03-03-03-01](./TASK-150-03-03-03-01_Guided_Register_Part_Router_Tool_Surface.md) | Add the canonical minimal tool for registering object roles in guided sessions |
| 2 | [TASK-150-03-03-03-02](./TASK-150-03-03-03-02_Optional_Guided_Role_Hints_On_Build_Tools.md) | Decide and wire the optional `guided_role` convenience path on existing build tools |

## Docs To Update

- `_docs/_PROMPTS/README.md`
- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_search_surface.py`

## Changelog Impact

- include in the parent TASK-150 execution-enforcement changelog entry

## Completion Summary

- delivered the canonical `guided_register_part(...)` tool surface
- delivered the optional `guided_role` convenience path on existing build
  tools
- documented both paths with the rule that `guided_register_part(...)`
  remains canonical
