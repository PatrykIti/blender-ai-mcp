# TASK-141-02-02: Search Metadata, Prompt Examples, and Public Docs for Creature Signatures

**Parent:** [TASK-141-02](./TASK-141-02_Creature_Build_Signature_Cues_And_Discovery_Surface_Alignment.md)
**Depends On:** [TASK-141-02-01](./TASK-141-02-01_Collection_Manage_And_Modeling_Create_Primitive_Contract_Cues.md)
**Status:** ✅ Done
**Priority:** 🔴 High

**Completion Summary:** Search metadata, prompts, MCP docs, and client-config
examples now point to the same creature bootstrap contract. The early squirrel
path stays small and actionable enough to surface the intended primitive and
collection signatures without relying on first-failure rediscovery loops.

## Objective

Make the chosen creature blockout signatures easy to discover and hard to
misread across search cues, prompt examples, and public docs, even when a real
session is operating under token pressure and noisy search responses.

## Business Problem

Even a good runtime policy is not enough if a real guided session still has to
search through large or misleading discovery payloads before it finds the right
blockout tools.

The guided creature flow needs one coherent operator-facing story for:

- how to create a primitive on the blockout path
- how to create/link/move collections
- when to use those tools directly versus when to keep working from macros or
  guided handoff cues
- how to reach those signatures quickly enough that the model does not fall
  back to guesswork

## Repository Touchpoints

- `server/adapters/mcp/discovery/search_documents.py`
- `server/adapters/mcp/discovery/search_surface.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/router/test_guided_manual_handoff.py`
- `tests/e2e/integration/test_guided_inspect_validate_handoff.py`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`
- `README.md`

## Acceptance Criteria

- search/discovery cues help surface the intended creature blockout tools for
  natural creature-part queries
- prompt/docs examples show canonical signatures for `collection_manage(...)`
  and `modeling_create_primitive(...)`
- the guided creature prompt no longer implies unsupported primitive or
  collection shortcuts
- focused regressions protect the chosen signature story across docs and
  discovery surfaces
- the early squirrel blockout search path stays small and actionable enough
  that the session does not need repeated rediscovery loops for basic tool
  signatures

## Leaf Work Items

- update discovery/search clues for the chosen signature story
- add explicit prompt/doc examples for canonical primitive and collection calls
- align guided creature handoff docs/tests with the same blockout-tool story
- add regressions that treat giant/noisy early creature-search responses as a
  product problem, not just a documentation gap

## Docs To Update

- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`
- `README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/router/test_guided_manual_handoff.py`
- `tests/e2e/integration/test_guided_inspect_validate_handoff.py`

## Changelog Impact

- include in the parent follow-on changelog entry when shipped

## Status / Board Update

- keep board tracking on `TASK-141`
- update the parent summary when this leaf closes so the final search/docs
  signature story and its real-session regression seam are explicit

## Validation

- `poetry run pytest tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `poetry run pytest tests/e2e/integration/test_guided_surface_contract_parity.py -q`
