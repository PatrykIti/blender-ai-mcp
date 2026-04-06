# TASK-141-01: Guided Call Path Compatibility and Public Contract Ergonomics

**Parent:** [TASK-141](./TASK-141_Guided_Creature_Run_Contract_And_Schema_Drift_Hardening.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Harden the first guided creature utility/call-path surfaces so early
`llm-guided` sessions stop wasting turns on wrapper-shape drift, cleanup-flag
guessing, and `reference_images(...)` attach-shape rediscovery.

## Business Problem

Before the useful creature build loop starts, the session still hits avoidable
contract drift on the small bootstrap/utility seam:

- `call_tool(...)` wrapper shape is easy for models to guess wrong
- `scene_clean_scene(...)` still attracts stale split cleanup flags
- `reference_images(action="attach", ...)` still gets treated like a batch
  upload surface instead of one-reference-per-attach

This subtask owns the guided call-path policy: where runtime compatibility is
worth adding, where canonical public forms must remain explicit, and where the
repo should fail with better guidance instead of generic validation noise.

## Repository Touchpoints

- `server/adapters/mcp/discovery/search_surface.py`
- `server/adapters/mcp/areas/reference.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`

## Acceptance Criteria

- the canonical public `call_tool(...)` form is explicit and regression-tested
- the runtime policy for wrapper-shape drift is deterministic:
  - either narrow compatibility aliases are supported intentionally
  - or repeated wrong shapes fail with actionable contract guidance
- `scene_clean_scene(...)` cleanup-flag compatibility remains narrow,
  canonical, and explicit on the guided surface
- `reference_images(action="attach", source_path=..., ...)` is treated as the
  one canonical attach shape for guided creature sessions
- batch-like `reference_images(...)` attach drift no longer fails as opaque
  schema noise when the runtime can detect the mistake
- docs and tests agree on which forms are canonical public contract and which
  forms are compatibility-only or rejected

## Docs To Update

- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Changelog Impact

- include in the parent `TASK-141` changelog entry when shipped

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-141-01-01](./TASK-141-01-01_Call_Tool_Wrapper_Aliases_And_Cleanup_Flag_Compatibility.md) | Decide and implement the guided `call_tool(...)` wrapper/cleanup compatibility policy |
| 2 | [TASK-141-01-02](./TASK-141-01-02_Reference_Images_Attach_Shape_And_Error_Guidance.md) | Define one-reference-per-attach `reference_images(...)` behavior plus guided error guidance for repeated wrong attach shapes |

## Status / Board Update

- keep board tracking on the parent `TASK-141`
- do not promote this subtask independently unless the call-path policy needs a
  separate review/ship checkpoint
