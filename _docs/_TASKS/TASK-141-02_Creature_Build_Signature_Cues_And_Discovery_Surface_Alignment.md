# TASK-141-02: Creature Build Signature Cues and Discovery Surface Alignment

**Parent:** [TASK-141](./TASK-141_Guided_Creature_Run_Contract_And_Schema_Drift_Hardening.md)
**Depends On:** [TASK-141-01](./TASK-141-01_Guided_Call_Path_Compatibility_And_Public_Contract_Ergonomics.md)
**Status:** ✅ Done
**Priority:** 🔴 High

**Completion Summary:** Creature blockout signature cues now match the active
guided surface instead of only local docs/helpers. Direct and proxied build
calls share the same contract hardening, and focused search/docs updates now
surface the canonical collection and primitive shapes under real client
pressure.

## Objective

Align runtime/search/docs cues for the creature blockout tools that the model
currently guesses wrong, and prove that those cues are strong enough under real
session pressure on the active guided surface.

## Business Problem

Real guided creature runs still show that "the signature exists somewhere in
docs/search" is not enough:

- `collection_manage(...)` still gets called with guessed names such as `name`
- `modeling_create_primitive(...)` still invites guessed knobs such as `scale`,
  `segments`, `rings`, `subdivisions`, or collection-placement shortcuts
- search output can become large/noisy enough that the model still burns turns
  rediscovering the correct blockout path instead of using it

This subtask owns the creature blockout signature story across runtime policy,
search quality, and operator-facing examples for the real active guided
surface.

## Repository Touchpoints

- `server/adapters/mcp/discovery/search_documents.py`
- `server/adapters/mcp/discovery/search_surface.py`
- `server/adapters/mcp/areas/collection.py`
- `server/adapters/mcp/areas/modeling.py`
- `server/router/infrastructure/tools_metadata/collection/collection_manage.json`
- `server/router/infrastructure/tools_metadata/modeling/modeling_create_primitive.json`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/router/test_guided_manual_handoff.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_inspect_validate_handoff.py`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`
- `README.md`

## Acceptance Criteria

- the canonical public signatures for `collection_manage(...)` and
  `modeling_create_primitive(...)` are explicit in discovery/docs examples
- the runtime policy for repeated guessed-argument drift is deliberate:
  - narrow compatibility aliases are supported only where they are
    high-confidence and low-risk
  - unsupported guesses fail with actionable guidance instead of generic noise
- search/discovery cues support the intended creature blockout use order under
  real session pressure rather than letting the model improvise signature lore
- the guided creature prompt/docs no longer imply hidden collection-placement
  or primitive-subdivision shortcuts that are not part of the public contract
- focused E2E/integration coverage proves that the discovered/canonicalized
  signatures work through the active shaped surface in the early squirrel path

## Docs To Update

- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`
- `README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/router/test_guided_manual_handoff.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_inspect_validate_handoff.py`

## Changelog Impact

- include in the parent `TASK-141` changelog entry when shipped

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-141-02-01](./TASK-141-02-01_Collection_Manage_And_Modeling_Create_Primitive_Contract_Cues.md) | Define the runtime/metadata policy for guessed `collection_manage(...)` and `modeling_create_primitive(...)` argument names and prove it on the real guided surface |
| 2 | [TASK-141-02-02](./TASK-141-02-02_Search_Metadata_Prompt_Examples_And_Public_Docs_For_Creature_Signatures.md) | Align search cues, prompt examples, and public docs so the early squirrel blockout path stays small, actionable, and hard to misread |

## Status / Board Update

- keep board tracking on the parent `TASK-141`
- do not promote this subtask independently unless discovery/runtime
  signature-policy work needs its own ship gate

## Validation

- `poetry run pytest tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `poetry run pytest tests/e2e/integration/test_guided_surface_contract_parity.py -q`
