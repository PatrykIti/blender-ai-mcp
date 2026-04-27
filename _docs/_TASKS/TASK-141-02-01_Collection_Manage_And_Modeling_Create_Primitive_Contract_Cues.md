# TASK-141-02-01: `collection_manage(...)` and `modeling_create_primitive(...)` Contract Cues

**Parent:** [TASK-141-02](./TASK-141-02_Creature_Build_Signature_Cues_And_Discovery_Surface_Alignment.md)
**Status:** ✅ Done
**Priority:** 🔴 High

**Completion Summary:** `collection_manage(...)` and
`modeling_create_primitive(...)` now keep one deliberate guided contract on the
active surface. The narrow `name` alias is accepted end to end for collection
management, while unsupported primitive shortcuts fail with actionable guidance
on both direct and proxied guided paths.

## Objective

Define one explicit runtime/metadata policy for the repeated guessed argument
shapes around `collection_manage(...)` and `modeling_create_primitive(...)`,
then prove that the same policy reaches the live guided `call_tool(...)` path.

## Business Problem

The real squirrel run surfaced the same pattern more than once, even though the
repo already contains local guidance:

- `collection_manage(...)` guessed `name` instead of `collection_name`
- `modeling_create_primitive(...)` guessed extra knobs such as `scale`,
  `segments`, `rings`, `subdivisions`, or collection-placement semantics
- the live guided surface still allowed the caller to fall into raw validation
  churn before recovering

This leaf owns the concrete public-contract decision for those shapes and the
parity work required so the decision actually holds on the active surface.

## Repository Touchpoints

- `server/adapters/mcp/areas/collection.py`
- `server/adapters/mcp/areas/modeling.py`
- `server/adapters/mcp/discovery/search_surface.py`
- `server/router/infrastructure/tools_metadata/collection/collection_manage.json`
- `server/router/infrastructure/tools_metadata/modeling/modeling_create_primitive.json`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`

## Acceptance Criteria

- the canonical public arguments for both tools are explicit in code metadata
  and regression scope
- any accepted compatibility alias is narrow, deterministic, and justified by
  repeated real-session drift
- unsupported guesses such as non-canonical primitive subdivision/collection
  shortcuts fail with actionable guidance
- search/runtime cues no longer leave the caller to infer whether those guessed
  arguments are supported
- the active guided `call_tool(...)` path either honors the accepted
  compatibility story or fails with the same actionable guidance proven in unit
  coverage

## Leaf Work Items

- decide which guessed arguments should be compatibility-only, which should be
  rejected, and which already belong to the canonical contract
- close any gap between runtime handling, metadata cues, and the real active
  `call_tool(...)` surface
- add focused unit plus E2E regression cases for canonical success and
  wrong-shape guidance

## Docs To Update

- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`

## Changelog Impact

- include in the parent follow-on changelog entry when shipped

## Status / Board Update

- keep board tracking on `TASK-141`
- reflect the final signature-policy decisions and active-surface parity result
  in the parent summary when this leaf closes

## Validation

- `poetry run pytest tests/unit/adapters/mcp/test_search_surface.py -q`
- `poetry run pytest tests/e2e/integration/test_guided_surface_contract_parity.py -q`
