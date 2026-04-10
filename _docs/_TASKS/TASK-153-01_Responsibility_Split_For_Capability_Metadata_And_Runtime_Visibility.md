# TASK-153-01: Responsibility Split For Capability Metadata And Runtime Visibility

**Parent:** [TASK-153](./TASK-153_Guided_Visibility_Authority_And_Manifest_Demotion.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Make the architecture explicit:

- tags/manifest = coarse/static metadata
- visibility policy = runtime exposure authority on `llm-guided`

## Detailed Implementation Notes

- this subtask is the design contract for the code leaves under `TASK-153-02`
- it should answer, in writing, three concrete questions before runtime
  refactoring starts:
  1. which metadata stays on capability tags/manifest
  2. which runtime decisions belong only to visibility policy + session state
  3. where parity tests should assert that no second authority reappears
- the goal is to remove ambiguity, not to invent a second abstraction layer

## Repository Touchpoints

- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
- `_docs/_MCP_SERVER/README.md`
- `server/adapters/mcp/visibility/tags.py`
- `server/adapters/mcp/platform/capability_manifest.py`
- `server/adapters/mcp/guided_mode.py`

## Planned File Change Map

- `_docs/_TASKS/TASK-153*.md`
  - expand the hierarchy into an implementation-ready plan with file-by-file
    ownership and test expectations
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
  - make the runtime-vs-metadata ownership split explicit
- `_docs/_MCP_SERVER/README.md`
  - document how `list_tools()`, `search_tools(...)`, and
    `router_get_status().visibility_rules` relate to one runtime authority
- `server/adapters/mcp/visibility/tags.py`
  - update docstrings/comments so tags are clearly metadata-first
- `server/adapters/mcp/platform/capability_manifest.py`
  - update docstrings/comments so manifest semantics stay coarse/static
- `server/adapters/mcp/guided_mode.py`
  - update docstrings/comments to state that diagnostics mirror runtime policy,
    not an independent metadata gate

## Acceptance Criteria

- the intended split is written down in code-adjacent docs and reflected in the
  task plan
- the task defines exactly which responsibilities remain in tags/manifest and
  which move to runtime visibility policy

## Planned Validation Matrix

- task/docs audit:
  - every `TASK-153` descendant clearly names the runtime authority owner
  - every `TASK-153` descendant clearly names the metadata-only owner
- docs parity:
  - `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md` and `_docs/_MCP_SERVER/README.md`
    say the same thing about visibility authority
- implementation handoff:
  - `TASK-153-02-*` has enough detail to modify code without rediscovering the
    architecture from scratch

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-153-01-01](./TASK-153-01-01_Audit_Current_Dual_Layer_Visibility_Decisions.md) | Audit where tags/manifest currently act like a second hidden runtime gate |
| 2 | [TASK-153-01-02](./TASK-153-01-02_Document_The_Single_Runtime_Visibility_Authority.md) | Document the desired split and the demotion of metadata-phase authority |

## Docs To Update

- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- docs parity assertions in `tests/unit/adapters/mcp/test_public_surface_docs.py`
  land once the runtime implementation leaves ship

## Changelog Impact

- include in the parent TASK-153 changelog entry
