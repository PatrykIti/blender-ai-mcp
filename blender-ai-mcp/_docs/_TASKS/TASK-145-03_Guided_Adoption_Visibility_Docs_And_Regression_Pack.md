# TASK-145-03: Guided Adoption, Visibility, Docs, and Regression Pack

**Parent:** [TASK-145](./TASK-145_Spatial_Repair_Planner_And_Sculpt_Handoff_Context.md)
**Status:** ✅ Done
**Priority:** 🔴 High
**Depends On:** [TASK-145-01](./TASK-145-01_Repair_Planner_Payload_And_Family_Selection_Policy.md), [TASK-145-02](./TASK-145-02_Sculpt_Handoff_Context_And_Precondition_Model.md)

## Objective

Ship planner-first operating guidance for `llm-guided` without reopening the
large-catalog problem. This means:

- shaping delivery on the public surface
- teaching prompt/docs consumers how to read planner output first
- locking the contract down with focused regression coverage

## Business Problem

The current repo already has the platform pieces needed for adoption:

- `visibility_policy.py`
- `guided_mode.py`
- `prompt_catalog.py`
- shaped prompt docs and search/discovery tests

But planner-first usage is still incomplete:

- prompt guidance is not yet consistently planner-first
- route/handoff ordering differs between docs
- search/visibility rules do not yet have a clear home for planner-context
  disclosure driven by current handoff state
- regression coverage is strong for the current loop, but not yet organized
  around the planner / sculpt-handoff contract that TASK-145 wants to harden

## Technical Direction

Use the current FastMCP-guided shaping stack instead of inventing a separate
adoption path:

- visibility and discovery remain platform-owned
- planner / sculpt policy remains deterministic and typed
- docs and prompts teach the compact planner story before lower-level edits
- regression coverage protects compact delivery and recommendation-only sculpt
  behavior

## Implementation Notes

- Visibility and search changes must stay on the existing FastMCP platform
  surfaces: `visibility_policy.py`, `guided_mode.py`,
  `session_capabilities.py`, capability manifest, and search metadata.
- Guided sculpt execution enforcement remains owned by `router_helper.py` and
  covered by `tests/unit/adapters/mcp/test_context_bridge.py`; include that
  lane whenever handoff-driven visibility can expose mutating `sculpt_*` tools.
- If planner or sculpt handoff state changes the bounded visible surface,
  native MCP visibility should refresh in the active request path. Do not rely
  on stale session catalog state.
- `ReferenceRefinementHandoffContract` is response-local today. If a later
  implementation needs it to affect native visibility, normalize only the
  bounded visibility-relevant facts into existing `guided_handoff` and/or
  `guided_flow_state`; do not add a separate planner-state persistence or
  catalog gate.
- Prompt/docs changes must describe shipped fields and visible tools only.
  Hidden or future-only planner details should be described as future work or
  omitted.

## Pseudocode

```python
# V1 can keep planner_handoff response-local and make no native visibility
# change. If planner_handoff must affect native visibility, wire the bounded
# visibility facts into the existing reference iteration / session-capability
# path before that path applies visibility.
planner_handoff = compare_result.refinement_handoff
advanced_state = await advance_guided_flow_from_iteration_async(
    ctx,
    loop_disposition=loop_disposition,
)
advanced_state = normalize_planner_handoff_visibility_facts(
    advanced_state,
    planner_handoff,
)
await apply_visibility_for_session_state(ctx, advanced_state)

# `normalize_planner_handoff_visibility_facts(...)` is a proposed pseudocode
# shape. Implement it by extending existing guided_handoff / guided_flow_state
# handling, not by adding planner_state or a second catalog. Search/discovery
# remains covered by existing search metadata and test_search_surface.py.
```

## Repository Touchpoints

- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/guided_mode.py`
- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/router_helper.py`
- `server/adapters/mcp/platform/capability_manifest.py`
- `server/adapters/mcp/prompts/prompt_catalog.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_context_bridge.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_prompt_catalog.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/vision/test_reference_guided_creature_comparison.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_VISION/README.md`
- `_docs/_VISION/CROSS_DOMAIN_REFINEMENT_ROUTING_EVAL.md`

## Acceptance Criteria

- planner / sculpt-handoff delivery on `llm-guided` remains small and
  intentional
- prompt and docs guidance consistently teaches planner-first interpretation
  before broader free-form edits
- search / visibility / prompt selection rules do not leak a broad new planner
  or sculpt family onto bootstrap by default
- native MCP visibility refreshes when planner/handoff state changes the
  bounded visible surface
- any handoff-driven visibility change is represented through existing
  `guided_handoff` / `guided_flow_state`, not a second planner-state flow
- regression coverage protects the compact delivery model and sculpt
  recommendation boundaries

## Docs To Update

- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`
- `_docs/_VISION/CROSS_DOMAIN_REFINEMENT_ROUTING_EVAL.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_context_bridge.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_prompt_catalog.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/vision/test_reference_guided_creature_comparison.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`

## Validation Category

- Unit visibility/search/prompt lane:
  `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_guided_mode.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_context_bridge.py tests/unit/adapters/mcp/test_guided_surface_benchmarks.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_prompt_catalog.py tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- Integration/E2E visibility lane when native MCP visibility behavior changes:
  `poetry run pytest tests/e2e/integration/test_guided_streamable_spatial_support.py tests/e2e/integration/test_guided_surface_contract_parity.py -q`
- Docs/preflight:
  `git diff --check`

## Changelog Impact

- covered by [_docs/_CHANGELOG/276-2026-04-30-task-145-repair-planner-handoff.md](../_CHANGELOG/276-2026-04-30-task-145-repair-planner-handoff.md)

## Completion Summary

Closed by shipping planner-first docs, compact/rich contract coverage, guided
execution fail-closed coverage for unmapped `sculpt_*` mutators, and visibility
policy preservation: no broad planner or sculpt family is bootstrap-visible by
default, and the v1 handoff does not create a separate native visibility state.

## Status / Board Update

- closed under the completed TASK-145 umbrella
- no separate board row is needed because TASK-145 remains the promoted item

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-145-03-01](./TASK-145-03-01_Planner_And_Sculpt_Delivery_On_LLM_Guided.md) | Decide how compact planner and sculpt-context artifacts are surfaced or discovered on `llm-guided` without widening bootstrap |
| 2 | [TASK-145-03-02](./TASK-145-03-02_Planner_First_Prompting_And_Documentation.md) | Update prompts/docs so operators read planner output before dropping to lower-level tools |
| 3 | [TASK-145-03-03](./TASK-145-03-03_Regression_Pack_For_Planner_And_Sculpt_Handoff.md) | Protect the new planner / sculpt-handoff contract with focused unit, discovery, prompt, and e2e coverage |
