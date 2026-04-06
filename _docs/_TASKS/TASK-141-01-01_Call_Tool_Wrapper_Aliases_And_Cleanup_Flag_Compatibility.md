# TASK-141-01-01: `call_tool(...)` Wrapper Aliases and Cleanup-Flag Compatibility

**Parent:** [TASK-141-01](./TASK-141-01_Guided_Call_Path_Compatibility_And_Public_Contract_Ergonomics.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Define one deterministic compatibility policy for guided `call_tool(...)`
wrapper drift and keep `scene_clean_scene(...)` cleanup-flag handling aligned
to that policy.

## Business Problem

Real creature sessions still lose time before useful modeling begins because
models drift on the small proxy contract itself:

- wrapper guesses such as `tool` / `params` compete with the canonical
  `name` / `arguments` form
- stale split cleanup flags compete with
  `keep_lights_and_cameras`
- proxy calls can become harder to reason about if compatibility is added
  ad hoc instead of as one explicit policy

This leaf must define the compatibility envelope instead of letting every
future prompt/runtime tweak reinvent it.

## Repository Touchpoints

- `server/adapters/mcp/discovery/search_surface.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `_docs/_PROMPTS/README.md`
- `_docs/_MCP_SERVER/README.md`

## Acceptance Criteria

- the canonical public form stays `call_tool(name=..., arguments=...)`
- the runtime behavior for wrapper drift is explicit and regression-tested:
  - accepted compatibility aliases, if any, are narrow and deterministic
  - rejected shapes fail with actionable guidance, not vague schema noise
- split cleanup flags remain compatibility-only and cannot silently override or
  blur `keep_lights_and_cameras`
- proxied validation/runtime failures still preserve the same failure
  semantics as direct tool execution

## Leaf Work Items

- decide whether wrapper alias compatibility is supported or rejected with
  guided contract messaging
- implement the chosen policy in the discovery `call_tool(...)` proxy
- keep `scene_clean_scene(...)` split-flag handling compatible with the same
  contract policy
- add focused regression coverage for canonical, compatibility, and ambiguous
  failure shapes

## Docs To Update

- `_docs/_PROMPTS/README.md`
- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Changelog Impact

- include in the parent follow-on changelog entry when shipped

## Status / Board Update

- keep board tracking on `TASK-141`
- reflect the final wrapper-policy decision in the parent task summary when
  this leaf closes
