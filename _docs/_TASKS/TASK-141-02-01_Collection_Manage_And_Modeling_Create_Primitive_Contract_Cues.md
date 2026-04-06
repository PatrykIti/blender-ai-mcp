# TASK-141-02-01: `collection_manage(...)` and `modeling_create_primitive(...)` Contract Cues

**Parent:** [TASK-141-02](./TASK-141-02_Creature_Build_Signature_Cues_And_Discovery_Surface_Alignment.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Define one explicit runtime/metadata policy for the repeated guessed argument
shapes around `collection_manage(...)` and `modeling_create_primitive(...)`.

## Business Problem

The real squirrel run surfaced the same pattern more than once:

- `collection_manage(...)` guessed `name` instead of `collection_name`
- `modeling_create_primitive(...)` guessed extra knobs such as `scale`,
  `subdivisions`, or collection-placement semantics

This leaf owns the concrete public-contract decision for those shapes instead
of leaving each call to rediscover the answer from validation errors.

## Repository Touchpoints

- `server/adapters/mcp/areas/collection.py`
- `server/adapters/mcp/areas/modeling.py`
- `server/router/infrastructure/tools_metadata/collection/collection_manage.json`
- `server/router/infrastructure/tools_metadata/modeling/modeling_create_primitive.json`
- `tests/unit/adapters/mcp/test_search_surface.py`

## Acceptance Criteria

- the canonical public arguments for both tools are explicit in code metadata
  and regression scope
- any accepted compatibility alias is narrow, deterministic, and justified by
  repeated real-session drift
- unsupported guesses such as non-canonical primitive subdivision/collection
  shortcuts fail with actionable guidance
- search/runtime cues no longer leave the caller to infer whether those guessed
  arguments are supported

## Leaf Work Items

- decide which guessed arguments should be compatibility-only, which should be
  rejected, and which already belong to the canonical contract
- implement the chosen policy in runtime handling and/or metadata-level cues
- add focused regression cases for canonical success and wrong-shape guidance

## Docs To Update

- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_search_surface.py`

## Changelog Impact

- include in the parent follow-on changelog entry when shipped

## Status / Board Update

- keep board tracking on `TASK-141`
- reflect the final signature-policy decisions in the parent summary when this
  leaf closes
