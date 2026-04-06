# TASK-144-03-01: LLM-Guided Disclosure And Discovery Shaping For View Diagnostics

**Parent:** [TASK-144-03](./TASK-144-03_Goal_Aware_Disclosure_Guided_Adoption_And_Regression_Pack.md)  
**Status:** ⏳ To Do  
**Priority:** 🟠 High  
**Depends On:** [TASK-144-02-02](./TASK-144-02-02_Scene_View_Diagnostics_Surface_RPC_Wiring_And_Metadata.md)

## Objective

Make the new view diagnostics discoverable on `llm-guided` only when they add
real value for the current goal, phase, or shaped handoff.

This leaf exists to keep exposure policy where it belongs:

- FastMCP visibility/discovery shaping
- deterministic metadata
- bounded phase-aware/handoff-aware rules

not in the router and not in free-form prompt heuristics.

## Implementation Direction

- keep bootstrap tiny and unchanged unless a deliberate product decision says
  otherwise
- use `visibility_policy.py`, `guided_mode.py`, and scene/reference metadata
  to shape discovery
- let build/inspect or handoff states reveal the view diagnostics only when
  framing/occlusion reasoning is likely to matter
- keep the new diagnostics narrow enough that discovery/search can recommend
  them without reopening catalog sprawl

## Repository Touchpoints

- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/guided_mode.py`
- `server/router/infrastructure/tools_metadata/scene/`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_provider_inventory.py`

## Acceptance Criteria

- `llm-guided` bootstrap remains intentionally small after view diagnostics land
- build/inspect or shaped handoff surfaces can expose or rank the diagnostics
  when goal/phase metadata makes them relevant
- the shaping remains deterministic and metadata-driven
- discovery/regression tests protect against silent surface bloat

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_provider_inventory.py`

## Changelog Impact

- include in the parent TASK-144 changelog entry when shipped

## Status / Board Update

- this leaf owns the FastMCP disclosure/discovery side of TASK-144 adoption
- `_docs/_TASKS/README.md` remains unchanged in this planning pass per operator
  constraint
