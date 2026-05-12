# TASK-136-02: Guided Building Handoff, Search, And Bounded Surface

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-136](./TASK-136_Reference_Guided_Architecture_And_Building_Reconstruction.md)
**Depends On:** [TASK-136-01](./TASK-136-01_Building_Contract_Vocabulary_And_Gate_Templates.md)
**Objective:** Extend the shipped `building` guided/runtime path with architecture-specific prompt assets, guided-state sequencing, visibility/search shaping, and bounded scene/modeling/mesh surfaces for reconstruction-oriented building work.
**Repository Touchpoints:** `server/adapters/mcp/prompts/prompt_catalog.py`, `server/adapters/mcp/prompts/provider.py`, `server/adapters/mcp/prompts/rendering.py`, `server/adapters/mcp/contracts/guided_flow.py`, `server/adapters/mcp/contracts/router.py`, `server/adapters/mcp/guided_mode.py`, `server/adapters/mcp/guided_naming_policy.py`, `server/adapters/mcp/platform/capability_manifest.py`, `server/adapters/mcp/platform/public_contracts.py`, `server/adapters/mcp/session_capabilities.py`, `server/adapters/mcp/session_capabilities_bootstrap.py`, `server/adapters/mcp/session_capabilities_registry.py`, `server/adapters/mcp/session_capabilities_state.py`, `server/adapters/mcp/session_capabilities_flow.py`, `server/adapters/mcp/session_capabilities_runtime_glue.py`, `server/adapters/mcp/transforms/prompts_bridge.py`, `server/adapters/mcp/transforms/visibility_policy.py`, `server/adapters/mcp/discovery/tool_inventory.py`, `server/adapters/mcp/discovery/search_surface.py`, `server/adapters/mcp/areas/router.py`, `server/adapters/mcp/areas/scene.py`, `server/adapters/mcp/areas/scene_guided_runtime.py`, `server/adapters/mcp/areas/modeling.py`, `server/adapters/mcp/areas/mesh.py`, `server/application/tool_handlers/router_handler.py`, `server/router/application/workflows/custom/simple_house.yaml`, `server/router/infrastructure/tools_metadata/scene/`, `server/router/infrastructure/tools_metadata/modeling/`, `server/router/infrastructure/tools_metadata/mesh/`, `server/router/infrastructure/tools_metadata/reference/`, `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`, `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`, `tests/unit/adapters/mcp/test_guided_mode.py`, `tests/unit/adapters/mcp/test_guided_naming_policy.py`, `tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py`, `tests/unit/adapters/mcp/test_prompt_provider_flow_bundles.py`, `tests/unit/router/application/test_router_contracts.py`, `tests/unit/adapters/mcp/test_router_elicitation.py`, `tests/unit/adapters/mcp/test_visibility_policy.py`, `tests/unit/adapters/mcp/test_search_surface.py`, `tests/e2e/router/test_guided_manual_handoff.py`, `tests/e2e/router/test_guided_direct_calls_do_not_trigger_workflows.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, `tests/e2e/integration/test_guided_search_first_call_tool_boundary.py`, `tests/e2e/integration/test_guided_streamable_spatial_support.py`
**Acceptance Criteria:**
- a building-oriented guided session emits an architecture-specific sequence on the existing guided-flow substrate, with typed guided-flow/control-plane changes wherever the current step model is too coarse
- prompt recommendations and prompt assets expose a dedicated architecture reconstruction story instead of only generic building or hard-surface wording
- search and visibility unlock only the bounded architecture-relevant tools for the current step, while broad hard-surface or hidden/internal surfaces remain unavailable
- the shipped control-plane seams preserve typed building flow initialization, registry-driven role advancement, prompt exposure, visibility/search shaping, and router-handoff behavior

## Implementation Notes

- keep the prompt surface on the existing MCP prompt catalog/provider path
- treat the shipped `building` domain profile, flow state, and visibility order
  as the baseline; this subtask extends those seams instead of inventing a second
  guided building runtime
- add a concrete architecture handoff recipe id,
  `reference_guided_architecture_build`, to the live router contract and tests
  if the architecture path needs a recipe distinct from generic manual build
- add one explicit building guided story that teaches:
  - footprint / shell first
  - openings/supports next
  - roof form after shell stability
  - final dimensional/facade checks after structure exists
- shape visibility/search around the current families and tool ids; do not
  invent a second guided flow system
- if the current `building` step model (`primary_masses` /
  `secondary_parts`) is too coarse for shell/opening/roof/support sequencing,
  extend the typed guided-flow contract explicitly instead of burying the new
  semantics in prose-only prompt hints
- implement architecture handoff on the current owners:
  - extend `RouterGuidedHandoffContract.recipe_id` in
    `server/adapters/mcp/contracts/router.py`
  - extend `build_guided_handoff_payload(...)` in
    `server/adapters/mcp/transforms/visibility_policy.py`
  - add architecture/reference/plan/elevation/facade manual-build detection in
    `RouterToolHandler._GUIDED_MANUAL_BUILD_PATTERNS` and keep generic
    `simple_house_workflow` available for simple house workflow requests
  - update search/visibility tests so reference-guided architecture requests do
    not silently fall back to the generic handoff or import workflow path
- prefer existing bounded layout/cutout/support tools first; new macros or tools
  should appear only when a concrete repeated building operation cannot be
  expressed safely enough otherwise

## Intended Owner Flow

```python
class RouterGuidedHandoffContract(MCPContract):
    recipe_id: Literal[
        "low_poly_creature_blockout",
        "mid_poly_organic_refine",
        "reference_guided_architecture_build",
    ] | None = None

if _looks_like_reference_guided_architecture_goal(goal):
    result.continuation_mode = "guided_manual_build"
    result.guided_handoff = build_guided_handoff_payload(
        "guided_manual_build",
        surface_profile="llm-guided",
        phase="build",
        goal=goal,
    )

state = update_session_from_router_goal(ctx, goal, result, surface_profile="llm-guided")
visibility_rules = build_visibility_rules(
    "llm-guided",
    state.phase,
    guided_handoff=state.guided_handoff,
    guided_flow_state=state.guided_flow_state,
)
```

If a new helper is useful, place it in the owning module above and test it
directly. Do not leave architecture behavior only in prompt wording or invented
helper names.

## Runtime / Security Contract Notes

- visibility levels must remain explicit:
  - public guided entry and discovery stay on the existing `llm-guided`
    surface
  - router-only/internal tool exposure stays hidden unless the current guided
    step already owns it
- read-only checks and mutating building helpers must stay distinguishable on
  the guided surface so search/visibility can recommend inspect/validate before
  mutating repair when the step requires it
- when mutating building helpers are exposed by step, document the expected
  Blender mode/selection impact explicitly and preserve the repo goal of
  predictable guided-mode state transitions rather than relying on implicit
  operator knowledge
- stdio, Streamable HTTP, and local Blender RPC sessions must all consume the
  same typed guided-flow/search state; do not add an architecture-only auth or
  session fork
- any new architecture-facing prompt/runtime metadata must be typed,
  schema-first, and reject unknown fields on strict public contracts
- reference-guided architecture goals must define the workflow boundary:
  `simple_house_workflow` may remain the deterministic workflow for generic
  "simple house" requests, but plan/elevation/facade/reference reconstruction
  should enter the architecture guided handoff unless the user explicitly asks
  for the workflow
- side effects stay bounded to the current guided step, existing timeouts, and
  repo-supported recovery semantics; no compatibility shims beyond explicit
  typed normalizers on the existing guided/runtime surfaces
- do not broaden the public surface into unrestricted hard-surface modeling
- architecture hints from RU stay advisory-only; gate pass/fail remains on the
  verifier path
- any new architecture-facing tool must go through the normal MCP/app/domain
  playbook from `AGENTS.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_guided_naming_policy.py`
- `tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py`
- `tests/unit/adapters/mcp/test_prompt_provider.py`
- `tests/unit/adapters/mcp/test_prompt_provider_flow_bundles.py`
- `tests/unit/adapters/mcp/test_prompts_bridge.py`
- `tests/unit/router/application/test_router_contracts.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/e2e/router/test_guided_manual_handoff.py`
- `tests/e2e/router/test_guided_direct_calls_do_not_trigger_workflows.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`
- `tests/e2e/integration/test_guided_search_first_call_tool_boundary.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Docs To Update

- `_docs/_PROMPTS/README.md`
- likely new `_docs/_PROMPTS/REFERENCE_GUIDED_ARCHITECTURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_ROUTER/README.md`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_CHANGELOG/README.md`

## Changelog Impact

- Add a `_docs/_CHANGELOG/*` entry when the first architecture guided-surface
  slice ships.
- Update `_docs/_CHANGELOG/README.md` when that historical entry is added.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_guided_mode.py tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py tests/unit/adapters/mcp/test_router_elicitation.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_search_surface.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py -q`
- `poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_prompt_provider.py tests/unit/adapters/mcp/test_prompt_provider_flow_bundles.py tests/unit/adapters/mcp/test_prompts_bridge.py tests/unit/router/application/test_router_contracts.py -q`
- `poetry run pytest tests/e2e/router/test_guided_manual_handoff.py tests/e2e/router/test_guided_direct_calls_do_not_trigger_workflows.py tests/e2e/integration/test_guided_search_first_call_tool_boundary.py tests/e2e/integration/test_guided_streamable_spatial_support.py -q`
- `poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`
- `poetry run pre-commit run --all-files --show-diff-on-failure`
- `poetry run pre-commit run check-router-tool-metadata --all-files`

Adjacent shared regression when the architecture slice changes common guided
transport/public-surface behavior:

- `poetry run pytest tests/e2e/integration/test_guided_surface_contract_parity.py -q`

## Status / Board Update

- keep `_docs/_TASKS/README.md` unchanged while this subtask remains open unless
  the architecture guided surface itself becomes a promoted board milestone
- when this subtask lands, update `TASK-136-02` and the parent `TASK-136`
  progress notes together so the next closeout subtask inherits the corrected
  guided/runtime owner mapping
- add or refresh the completion summary and record which docs, unit tests,
  E2E lanes, pre-commit checks, and changelog updates were run or
  intentionally skipped
