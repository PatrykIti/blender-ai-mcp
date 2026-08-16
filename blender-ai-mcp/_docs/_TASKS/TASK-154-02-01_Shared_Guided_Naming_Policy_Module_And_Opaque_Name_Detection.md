# TASK-154-02-01: Shared Guided Naming Policy Module And Opaque Name Detection

**Parent:** [TASK-154-02](./TASK-154-02_Runtime_Advisory_And_Enforcement_Integration_For_Guided_Naming.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Create the shared runtime naming-policy module and define how it decides
whether a role-sensitive object name is acceptable, weak-but-recoverable, or
too opaque.

## Repository Touchpoints

- `server/adapters/mcp/guided_naming_policy.py`
- `server/adapters/mcp/session_capabilities.py`
- `server/application/services/spatial_graph.py`
- `server/adapters/mcp/areas/reference.py`
- `tests/unit/adapters/mcp/test_guided_naming_policy.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`

## Planned Code Shape

```python
def evaluate_guided_object_name(
    *,
    object_name: str,
    role: str | None,
    domain_profile: str | None,
    current_step: str | None,
    mode: str = "warn",
) -> GuidedNamingPolicyDecision: ...
```

## Detailed Implementation Notes

- the policy should distinguish:
  - fully semantic names
  - weak but still legible names
  - opaque abbreviations
  - placeholder/generated junk names
- keep seam/attachment heuristics available as fallback input, but do not let
  heuristic recoverability be the only policy criterion
- the module should stay pure/deterministic and avoid direct FastMCP context
  dependencies

## Planned File Change Map

- `server/adapters/mcp/guided_naming_policy.py`
  - add pure evaluators and suggestion lookup
- `server/adapters/mcp/session_capabilities.py`
  - import role/domain helpers if needed, but do not bury policy logic there
- `server/application/services/spatial_graph.py`
  - keep heuristics independent from the new policy module
- `server/adapters/mcp/areas/reference.py`
  - keep reference-stage heuristics independent from the new policy module
- `tests/unit/adapters/mcp/test_guided_naming_policy.py`
  - cover pure evaluator states and reason codes
- `tests/unit/adapters/mcp/test_reference_images.py`
  - verify heuristic backstop expectations remain intact
- `tests/unit/tools/test_handler_rpc_alignment.py`
  - verify relation graph backstop expectations remain intact

## Pseudocode Sketch

```python
if object_name in suggested_names:
    return allowed(...)
if looks_opaque(object_name) and mode == "block_opaque_role_sensitive":
    return blocked(message=..., suggested_names=suggested_names)
if looks_weak(object_name):
    return warning(message=..., suggested_names=suggested_names)
return allowed(...)
```

## Acceptance Criteria

- one shared module owns guided naming-policy evaluation
- opaque-name detection is explicit and testable

## Docs To Update

- none directly

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_naming_policy.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`

## Changelog Impact

- include in the parent TASK-154 changelog entry

## Completion Summary

- added the shared policy module, placeholder-name detection, weak-abbreviation
  handling, and domain-specific role naming specs
