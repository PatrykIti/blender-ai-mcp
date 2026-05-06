# TASK-136-02: Guided Building Handoff, Search, And Bounded Surface

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-136](./TASK-136_Reference_Guided_Architecture_And_Building_Reconstruction.md)
**Depends On:** [TASK-136-01](./TASK-136-01_Building_Contract_Vocabulary_And_Gate_Templates.md)
**Objective:** Turn the architecture contract into a usable `llm-guided` runtime path by shaping prompt assets, guided state, visibility, search, and bounded scene/modeling/mesh surfaces for building work.
**Repository Touchpoints:** `server/adapters/mcp/prompts/prompt_catalog.py`, `server/adapters/mcp/prompts/provider.py`, `server/adapters/mcp/prompts/rendering.py`, `server/adapters/mcp/guided_mode.py`, `server/adapters/mcp/session_capabilities_state.py`, `server/adapters/mcp/session_capabilities_flow.py`, `server/adapters/mcp/session_capabilities_runtime_glue.py`, `server/adapters/mcp/transforms/visibility_policy.py`, `server/adapters/mcp/discovery/search_surface.py`, `server/adapters/mcp/areas/scene.py`, `server/adapters/mcp/areas/modeling.py`, `server/adapters/mcp/areas/mesh.py`, `server/router/infrastructure/tools_metadata/scene/`, `server/router/infrastructure/tools_metadata/modeling/`, `server/router/infrastructure/tools_metadata/reference/`, `tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py`, `tests/unit/adapters/mcp/test_router_elicitation.py`, `tests/unit/adapters/mcp/test_visibility_policy.py`, `tests/unit/adapters/mcp/test_search_surface.py`
**Acceptance Criteria:** a building goal can reach a bounded architecture-oriented guided path with explicit shell/opening/roof/support sequencing, targeted search, and no fallback to broad hard-surface catalog behavior.

## Implementation Notes

- keep the prompt surface on the existing MCP prompt catalog/provider path
- add one explicit building guided story that teaches:
  - footprint / shell first
  - openings/supports next
  - roof form after shell stability
  - final dimensional/facade checks after structure exists
- shape visibility/search around the current families and tool ids; do not
  invent a second guided flow system
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

- do not broaden the public surface into unrestricted hard-surface modeling
- architecture hints from RU stay advisory-only; gate pass/fail remains on the
  verifier path
- any new architecture-facing tool must go through the normal MCP/app/domain
  playbook from `AGENTS.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_search_surface.py`

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
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py tests/unit/adapters/mcp/test_router_elicitation.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_search_surface.py -q`
