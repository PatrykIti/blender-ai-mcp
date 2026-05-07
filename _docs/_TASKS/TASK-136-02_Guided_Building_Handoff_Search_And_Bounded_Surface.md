# TASK-136-02: Guided Building Handoff, Search, And Bounded Surface

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-136](./TASK-136_Reference_Guided_Architecture_And_Building_Reconstruction.md)
**Depends On:** [TASK-136-01](./TASK-136-01_Building_Contract_Vocabulary_And_Gate_Templates.md)
**Objective:** Extend the shipped `building` guided/runtime path with architecture-specific prompt assets, guided-state sequencing, visibility/search shaping, and bounded scene/modeling/mesh surfaces for reconstruction-oriented building work.
**Repository Touchpoints:** `server/adapters/mcp/prompts/prompt_catalog.py`, `server/adapters/mcp/prompts/provider.py`, `server/adapters/mcp/prompts/rendering.py`, `server/adapters/mcp/contracts/guided_flow.py`, `server/adapters/mcp/guided_mode.py`, `server/adapters/mcp/session_capabilities.py`, `server/adapters/mcp/session_capabilities_registry.py`, `server/adapters/mcp/session_capabilities_state.py`, `server/adapters/mcp/session_capabilities_flow.py`, `server/adapters/mcp/session_capabilities_runtime_glue.py`, `server/adapters/mcp/transforms/visibility_policy.py`, `server/adapters/mcp/discovery/search_surface.py`, `server/adapters/mcp/areas/scene.py`, `server/adapters/mcp/areas/scene_guided_runtime.py`, `server/adapters/mcp/areas/modeling.py`, `server/adapters/mcp/areas/mesh.py`, `server/router/infrastructure/tools_metadata/scene/`, `server/router/infrastructure/tools_metadata/modeling/`, `server/router/infrastructure/tools_metadata/reference/`, `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`, `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`, `tests/unit/adapters/mcp/test_guided_mode.py`, `tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py`, `tests/unit/adapters/mcp/test_router_elicitation.py`, `tests/unit/adapters/mcp/test_visibility_policy.py`, `tests/unit/adapters/mcp/test_search_surface.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`
**Acceptance Criteria:**
- a building-oriented guided session emits an architecture-specific sequence on the existing guided-flow substrate, either by extending the current step model or by documenting a typed architecture sub-sequence on top of it
- prompt recommendations and prompt assets expose a dedicated architecture reconstruction story instead of only generic building or hard-surface wording
- search and visibility unlock only the bounded architecture-relevant tools for the current step, while broad hard-surface or hidden/internal surfaces remain unavailable
- the shipped control-plane seams preserve typed building flow initialization, registry-driven role advancement, prompt exposure, visibility/search shaping, and router-handoff behavior

## Implementation Notes

- keep the prompt surface on the existing MCP prompt catalog/provider path
- treat the shipped `building` domain profile, flow state, and visibility order
  as the baseline; this leaf extends those seams instead of inventing a second
  guided building runtime
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
- prefer existing bounded layout/cutout/support tools first; new macros or tools
  should appear only when a concrete repeated building operation cannot be
  expressed safely enough otherwise

## Pseudocode

```python
if domain_profile == "building":
    guided_handoff = build_architecture_handoff(goal, references)
    guided_flow_state = seed_building_flow_state(shell_then_openings_then_roof)
    visibility_rules = expose_bounded_building_tools(guided_flow_state.current_step)
    search_bias = rank_building_queries_against_layout_cutout_support_tools(goal)
```

## Runtime / Security Contract Notes

- visibility levels must remain explicit:
  - public guided entry and discovery stay on the existing `llm-guided`
    surface
  - router-only/internal tool exposure stays hidden unless the current guided
    step already owns it
- read-only checks and mutating building helpers must stay distinguishable on
  the guided surface so search/visibility can recommend inspect/validate before
  mutating repair when the step requires it
- stdio, Streamable HTTP, and local Blender RPC sessions must all consume the
  same typed guided-flow/search state; do not add an architecture-only auth or
  session fork
- any new architecture-facing prompt/runtime metadata must be typed,
  schema-first, and reject unknown fields on strict public contracts
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
- `tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`

## Docs To Update

- `_docs/_PROMPTS/README.md`
- likely new `_docs/_PROMPTS/REFERENCE_GUIDED_ARCHITECTURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`

## Changelog Impact

- Add a `_docs/_CHANGELOG/*` entry when the first architecture guided-surface
  slice ships.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_guided_mode.py tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py tests/unit/adapters/mcp/test_router_elicitation.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_search_surface.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py -q`
- `poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `poetry run pre-commit run check-router-tool-metadata --all-files`

Adjacent shared regression when the architecture slice changes common guided
transport/public-surface behavior:

- `poetry run pytest tests/e2e/integration/test_guided_surface_contract_parity.py -q`

## Status / Board Update

- keep `_docs/_TASKS/README.md` unchanged while this leaf remains open unless
  the architecture guided surface itself becomes a promoted board milestone
- when this leaf lands, update `TASK-136-02` and the parent `TASK-136`
  progress notes together so the next closeout leaf inherits the corrected
  guided/runtime owner mapping
