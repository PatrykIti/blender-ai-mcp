# TASK-130: Default Guided Surface Bootstrap Consistency

**Status:** ⏳ To Do
**Priority:** 🟠 High
**Category:** Product Surface / Bootstrap Consistency
**Dependencies:** TASK-120, TASK-128 audit follow-on

## Objective

Close the docs/runtime drift around the repo's default bootstrap story so the
documented "default production" surface matches the actual configured
bootstrap surface, examples, and regression coverage.

## Business Problem

Current public docs describe `llm-guided` as the default production-oriented
surface, but runtime config still boots with `legacy-flat` unless the operator
overrides `MCP_SURFACE_PROFILE`.

That mismatch is not creature-specific, but it directly weakens the broader
product story:

- operators can start on a broad compatibility surface while reading docs that
  assume a small guided surface
- audit findings against `llm-guided` can be misread as default-runtime
  behavior even when the default bootstrap path still points elsewhere
- examples, onboarding, and production guidance become harder to trust

## Scope

This follow-on covers:

- deciding one explicit product story for the bootstrap default:
  - make `llm-guided` the real runtime default
  - or keep `legacy-flat` as the runtime default and update docs so they stop
    claiming otherwise
- aligning config defaults, README/docs wording, and client/config examples
- adding focused regression coverage so this default/bootstrap contract cannot
  silently drift again

This follow-on does **not** cover:

- creature-specific prompt/handoff/search shaping under TASK-128 Slice A
- perception-side silhouette or segmentation work under TASK-128 Slice B/C

## Acceptance Criteria

- one explicit bootstrap/default-surface story is chosen and reflected in both
  runtime and docs
- `server/infrastructure/config.py`, `README.md`, and MCP-facing docs do not
  disagree about which surface is the default bootstrap path
- examples/config snippets no longer assume a different default than runtime
- focused regressions fail if docs/runtime drift back out of alignment
- TASK-128 Slice A can refer to this broader bootstrap posture as a separate
  resolved follow-on instead of carrying the ambiguity implicitly

## Repository Touchpoints

- `server/infrastructure/config.py`
- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- focused bootstrap/default-surface regression coverage under `tests/unit/adapters/mcp/`
- `_docs/_TASKS/README.md`

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- focused bootstrap/default-surface regression coverage under `tests/unit/adapters/mcp/`

## Changelog Impact

- add a dedicated `_docs/_CHANGELOG/*` entry when this follow-on ships

## Status / Board Update

- promote this as a board-level follow-on from the TASK-128 audit
- keep it separate from Slice A so creature-surface closure and broader
  bootstrap-default closure do not get conflated
