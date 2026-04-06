# TASK-141: Guided Creature Run Contract and Schema Drift Hardening

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Category:** Product Reliability / Guided Runtime UX
**Follow-on After:** [TASK-128](./TASK-128_Reference_Guided_Creature_Build_Surface_And_Perception_Reliability.md)

## Objective

Reduce schema-guessing and prompt/runtime drift during real
reference-guided creature sessions on `llm-guided`, so an operator can launch a
low-poly squirrel run without the model repeatedly discovering basic
tool-signature mismatches the hard way.

## Business Problem

The `TASK-128` surface is now materially better, but a real squirrel run still
showed several avoidable failures before the useful build loop took over:

- `call_tool(...)` was invoked with the wrong wrapper shape before the model
  settled on `name` + `arguments`
- the model tried legacy cleanup flags (`keep_lights` / `keep_cameras`) before
  the canonical `keep_lights_and_cameras`
- `reference_images(...)` was attempted as one batch `images=[...]` call even
  though the current public surface is one-reference-per-attach
- `collection_manage(...)` and `modeling_create_primitive(...)` were called
  with guessed argument names (`name`, `scale`, `subdivisions`,
  `collection_name`) that do not exist on the current public contract
- after `loop_disposition="inspect_validate"`, the session still relied on
  operator interpretation instead of the prompt/runtime strongly steering the
  next step

These are not "the model was bad" issues in isolation. They are product-surface
issues: prompt guidance, examples, search/discovery cues, and public contract
ergonomics still leave too much room for first-try schema drift in exactly the
creature flow the repo is trying to promote.

## Scope

This follow-on covers:

- tightening prompt/docs examples around the exact public signatures used in
  guided creature sessions
- deciding where ergonomics should be improved in runtime instead of only in
  docs, especially when the same wrong call shape is likely to recur
- reducing rediscovery cost for:
  - `call_tool(name=..., arguments=...)`
  - `scene_clean_scene(keep_lights_and_cameras=...)`
  - `reference_images(action="attach", source_path=..., ...)`
  - `collection_manage(...)`
  - `modeling_create_primitive(...)`
- making `inspect_validate` handling more explicit in creature prompt/runtime
  guidance
- locking the final operator story with focused regression coverage

This follow-on does **not** cover:

- broader bootstrap-default consistency under [TASK-130](./TASK-130_Default_Guided_Surface_Bootstrap_Consistency.md)
- anatomy-aware creature reconstruction under [TASK-135](./TASK-135_Anatomy_Aware_Reference_Guided_Low_Poly_Creature_Reconstruction.md)
- expanding the external `vision_contract_profile` family matrix under
  [TASK-140](./TASK-140_Expand_External_Vision_Contract_Profiles_Across_Qwen_Anthropic_OpenAI_And_NVIDIA.md)

## Acceptance Criteria

- the repo has one explicit product story for the first-run guided creature
  path that no longer relies on guessed wrapper shapes or stale examples
- prompt/docs/examples use the canonical public argument names for the current
  guided surface
- the task explicitly decides which observed drifts are:
  - documentation/prompt fixes only
  - public-surface ergonomics fixes in code
- creature runs do not need to rediscover the basic `call_tool(...)`,
  `reference_images(...)`, and `scene_clean_scene(...)` contract shapes from
  validation errors alone
- `inspect_validate` is described and regression-tested as a true stop-and-check
  branch, not a soft suggestion buried in prose
- regression coverage protects the chosen operator story using the squirrel run
  failure shapes as concrete negative examples

## Repository Touchpoints

- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `README.md`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/discovery/search_documents.py`
- `server/adapters/mcp/discovery/search_surface.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/areas/router.py`
- `server/adapters/mcp/areas/collection.py`
- `server/adapters/mcp/areas/modeling.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/e2e/router/test_guided_manual_handoff.py`
- `tests/e2e/vision/test_reference_stage_silhouette_contract.py`

## Docs To Update

- `README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/e2e/router/test_guided_manual_handoff.py`
- `tests/e2e/vision/test_reference_stage_silhouette_contract.py`

## Changelog Impact

- add a dedicated `_docs/_CHANGELOG/*` entry when this follow-on ships

## Status / Board Update

- promote this as a board-level follow-on after the first real `TASK-128`
  squirrel run
- keep it separate from `TASK-130` because this is guided creature
  operator-path/schema drift, not the broader default-bootstrap story
