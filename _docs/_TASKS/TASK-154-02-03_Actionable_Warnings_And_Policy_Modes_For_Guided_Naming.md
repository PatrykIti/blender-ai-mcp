# TASK-154-02-03: Actionable Warnings And Policy Modes For Guided Naming

**Parent:** [TASK-154-02](./TASK-154-02_Runtime_Advisory_And_Enforcement_Integration_For_Guided_Naming.md)
**Depends On:** [TASK-154-02-02](./TASK-154-02-02_Integrate_Naming_Policy_Into_Guided_Register_Part_And_Build_Calls.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Define the runtime policy modes and the exact warning/block guidance surfaced
to models and operators when object names are too weak for guided semantics.

## Repository Touchpoints

- `server/adapters/mcp/guided_naming_policy.py`
- `server/adapters/mcp/router_helper.py`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `tests/unit/adapters/mcp/test_guided_naming_policy.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Planned Code Shape

```python
GUIDED_NAMING_POLICY_MODE = Literal[
    "off",
    "warn",
    "block_opaque_role_sensitive",
]
```

## Detailed Implementation Notes

- recommended initial rollout:
  - default mode: `warn`
  - strict mode available for targeted follow-up or experiments
- warning/block messages should always include:
  - current role
  - why the name is weak/opaque
  - suggested better names
- consider machine-readable reason codes such as:
  - `opaque_abbreviation`
  - `placeholder_name`
  - `generic_mass_name`
- avoid vague prose such as “bad name”; guidance should be concrete

## Pseudocode Sketch

```python
message = (
    "Guided naming prefers a semantic name for role "
    f"'{role}'. Rename or create this object as one of: {', '.join(suggested_names)}."
)
```

## Acceptance Criteria

- policy modes are explicit
- warning/block messages are deterministic and actionable

## Docs To Update

- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_naming_policy.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Changelog Impact

- include in the parent TASK-154 changelog entry

## Completion Summary

- shipped deterministic warning/block messages plus explicit rollout config via
  `MCP_GUIDED_NAMING_POLICY_MODE`
