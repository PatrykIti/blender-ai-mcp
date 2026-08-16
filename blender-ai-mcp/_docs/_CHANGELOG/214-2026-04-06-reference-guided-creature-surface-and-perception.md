# 214. Reference-guided creature surface and perception reliability

Date: 2026-04-06

## Summary

Completed the TASK-128 creature-reliability wave by aligning the public
`llm-guided` creature prompt/handoff/search surface with deterministic
silhouette-driven perception outputs and an explicitly opt-in segmentation
sidecar contract.

## What Changed

- promoted `reference_guided_creature_build` into the real MCP prompt catalog,
  native prompt provider, prompt bridge, and guided prompt visibility surface
- extended `recommended_prompts` so phase/profile recommendations can also use
  explicit session goal and guided-handoff context for creature-oriented
  sessions
- introduced a stable creature-specific guided handoff recipe,
  `recipe_id="low_poly_creature_blockout"`, with session-applied visibility
  shaping instead of always falling back to the broad generic build surface
- enriched discovery metadata for creature blockout tools such as
  `modeling_create_primitive`, `mesh_extrude_region`, `mesh_loop_cut`,
  `macro_adjust_relative_proportion`, and `macro_adjust_segment_chain_arc`
  while keeping noisy vertex-group / randomize helpers out of the first-choice
  handoff path
- added deterministic `silhouette_analysis` metrics and typed `action_hints`
  to staged reference compare/iterate responses, keeping them explicitly in the
  perception layer alongside the existing truth-first loop outputs
- added a vendor-neutral `part_segmentation` contract plus a separate,
  default-off segmentation-sidecar config surface
  (`VISION_SEGMENTATION_*`) so optional part-aware perception no longer needs
  to overload `VISION_EXTERNAL_CONTRACT_PROFILE`
- updated product/docs/test surfaces so README, MCP docs, prompt docs, vision
  docs, config examples, and task/changelog history all describe the same
  shipped public story

## Why

Creature work already had a strong hybrid-loop baseline, but the runtime still
made the model rediscover too much on its own. The missing pieces were prompt
surface exposure, creature-specific guided narrowing, discovery bias, and a
machine-readable perception layer that could drive bounded next-tool hints
before any heavier segmentation runtime was considered.

## Validation

- `poetry run pytest tests/unit/adapters/mcp/test_prompt_catalog.py tests/unit/adapters/mcp/test_prompt_provider.py tests/unit/adapters/mcp/test_prompts_bridge.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_guided_mode.py tests/unit/adapters/mcp/test_session_phase.py tests/unit/router/application/test_router_contracts.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_guided_surface_benchmarks.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_vision_runtime_config.py -q`
