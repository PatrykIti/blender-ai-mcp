# 225 - Server-Driven Guided Flow State And Step Gating

**Date:** 2026-04-08
**Task:** TASK-150
**Status:** ✅ Done

---

## Summary

Landed the first server-owned guided flow contract for `llm-guided` so guided
sessions now expose machine-readable step state, domain overlays, required
checks, and prompt bundles instead of relying only on `guided_handoff`,
phase-level visibility, or prose prompt discipline.

---

## Changes

### 1. Guided Flow State Contract And Session Persistence

- added `GuidedFlowStateContract` and `GuidedFlowCheckContract`
- persisted `guided_flow_state` in `SessionCapabilityState`
- exposed `guided_flow_state` on:
  - `router_set_goal(...)`
  - `router_get_status()`
  - `reference_compare_stage_checkpoint(...)`
  - `reference_iterate_stage_checkpoint(...)`

### 2. Domain Profiles And Initial Step Semantics

- added deterministic domain-profile selection for:
  - `generic`
  - `creature`
  - `building`
- added one shared step vocabulary including:
  - `understand_goal`
  - `establish_spatial_context`
  - `create_primary_masses`
  - `place_secondary_parts`
  - `checkpoint_iterate`
  - `inspect_validate`
  - `finish_or_stop`
- fixed same-goal follow-up routing so `needs_input -> ready` advances from
  `understand_goal` into the spatial-context gate instead of leaving the flow
  stuck on the clarification step

### 3. Step-Gated Visibility And Flow Mutation

- extended guided visibility diagnostics and visibility application to consult
  `guided_flow_state`
- narrowed build visibility during `establish_spatial_context` to bounded
  spatial/reference/inspection support tools
- recorded spatial-check completion from:
  - `scene_scope_graph`
  - `scene_relation_graph`
  - `scene_view_diagnostics`
- advanced guided flow state from staged iterate outcomes so
  `loop_disposition="inspect_validate"` now updates the server-owned flow step

### 4. Prompt Bundles And Recommendation Surface

- added `required_prompts` / `preferred_prompts` to the guided flow state
- rendered those bundles through `recommended_prompts`
- documented prompt bundles as support for the server-driven flow rather than
  as a replacement for it

### 5. Regression Coverage And Docs

- added regression coverage for:
  - flow-state round-tripping
  - domain-profile overlays
  - prompt-bundle mapping
  - flow-aware visibility/search shaping
  - router/status payload parity
  - router-style end-to-end guided handoff/status exposure
- updated:
  - `README.md`
  - `_docs/_MCP_SERVER/README.md`
  - `_docs/_PROMPTS/README.md`
  - `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
  - `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
  - `_docs/_TASKS/README.md`

---

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py tests/unit/adapters/mcp/test_prompt_provider_flow_bundles.py tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py tests/unit/adapters/mcp/test_session_phase.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_router_elicitation.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_guided_mode.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_prompt_provider.py tests/unit/adapters/mcp/test_prompt_catalog.py -q`

Transport/E2E broadening can continue under TASK-150, but the server-owned
flow-state baseline, prompt-bundle contract, and visibility gating are now in
place and regression-covered.
