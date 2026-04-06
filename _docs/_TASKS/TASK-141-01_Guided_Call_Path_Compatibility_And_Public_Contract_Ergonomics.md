# TASK-141-01: Guided Call Path Compatibility and Public Contract Ergonomics

**Parent:** [TASK-141](./TASK-141_Guided_Creature_Run_Contract_And_Schema_Drift_Hardening.md)
**Status:** ✅ Done
**Priority:** 🔴 High

**Completion Summary:** Guided utility/intake parity now holds on the active
surface: `call_tool(...)`, direct `reference_images(...)`, and direct/proxied
cleanup all use the same narrow compatibility envelope with actionable
contract guidance instead of raw schema noise.

## Objective

Make the early guided creature utility/intake contract behave correctly on the
actual active shaped surface, so real sessions stop losing setup turns to
`call_tool(...)`, cleanup, and reference-intake drift before the first useful
checkpoint even happens.

## Business Problem

The repo already has local policy/docs fixes for the early guided seam, but a
real creature session can still hit contract drift on the active surface:

- `call_tool(...)` compatibility behavior is not yet proven end to end on the
  same server/profile/transport path the client actually uses
- `scene_clean_scene(...)` compatibility may exist locally while the real run
  still rediscovers it by trial and error
- `reference_images(action="attach", ...)` remains easy to misread as a batch
  intake surface during live setup

This subtask therefore owns active-surface parity for the guided utility/intake
seam: not just the policy, but proof that the policy reaches the real shaped
surface intact.

## Repository Touchpoints

- `server/adapters/mcp/discovery/search_surface.py`
- `server/adapters/mcp/factory.py`
- `server/adapters/mcp/surfaces.py`
- `server/adapters/mcp/areas/reference.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`

## Acceptance Criteria

- the canonical public `call_tool(...)` form is explicit and regression-tested
  on the real active shaped surface
- the runtime policy for wrapper-shape drift is deterministic and proven end to
  end:
  - either narrow compatibility aliases are supported intentionally
  - or repeated wrong shapes fail with actionable contract guidance
- `scene_clean_scene(...)` cleanup-flag compatibility remains narrow,
  canonical, explicit, and identical between unit and E2E surface paths
- `reference_images(action="attach", source_path=..., ...)` is treated as the
  one canonical attach shape for guided creature sessions
- batch-like `reference_images(...)` attach drift no longer fails as opaque
  schema noise when the runtime can detect the mistake
- docs, unit tests, and E2E surface regressions agree on which forms are
  canonical public contract and which forms are compatibility-only or rejected

## Docs To Update

- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`

## Changelog Impact

- include in the parent `TASK-141` changelog entry when shipped

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-141-01-01](./TASK-141-01-01_Call_Tool_Wrapper_Aliases_And_Cleanup_Flag_Compatibility.md) | Prove `call_tool(...)` and cleanup compatibility behavior on the actual active guided surface instead of only in local helper tests |
| 2 | [TASK-141-01-02](./TASK-141-01-02_Reference_Images_Attach_Shape_And_Error_Guidance.md) | Make one-reference-per-attach reference intake and its recovery guidance hold on the real shaped surface and staged-goal path |

## Status / Board Update

- keep board tracking on the parent `TASK-141`
- do not promote this subtask independently unless the call-path policy needs a
  separate review/ship checkpoint

## Validation

- `poetry run pytest tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `poetry run pytest tests/e2e/integration/test_guided_surface_contract_parity.py -q`
