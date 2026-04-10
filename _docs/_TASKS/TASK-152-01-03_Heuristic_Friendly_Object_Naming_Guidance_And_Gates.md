# TASK-152-01-03: Heuristic-Friendly Object Naming Guidance And Gates

**Parent:** [TASK-152-01](./TASK-152-01_Spatial_Tool_Prompting_And_Seam_Interpretation_Guidance.md)
**Depends On:** [TASK-152-01-02](./TASK-152-01-02_Reference_Image_Grounding_In_Guided_Blockout_Prompts.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Reduce role/seam heuristic drift caused by opaque abbreviations such as
`ForeL`, `ForeR`, `HindL`, `HindR` by making naming guidance explicit and
evaluating whether a lightweight runtime gate or warning should exist.

## Repository Touchpoints

- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_PROMPTS/README.md`
- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `server/application/services/spatial_graph.py`
- `server/adapters/mcp/router_helper.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Planned Guidance Shape

- explicitly prefer full semantic names like:
  - `Body`
  - `Head`
  - `Tail`
  - `ForeLeg_L`
  - `ForeLeg_R`
  - `HindLeg_L`
  - `HindLeg_R`
- explicitly discourage opaque abbreviations like:
  - `ForeL`
  - `HindR`
  - `Hd`
  - `Bd`
- evaluate one lightweight enforcement option:
  - prompt-only rule
  - blocked/warning response on guided part registration or role-sensitive
    build calls when names are too opaque
  - heuristic expansion support for common abbreviations

## Acceptance Criteria

- prompt/docs guidance clearly tells the model to use full readable names
- the task decides whether prompt-only guidance is enough or whether a runtime
  gate/warning/fallback heuristic is needed

## Docs To Update

- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_PROMPTS/README.md`
- `README.md`
- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Changelog Impact

- include in the parent TASK-152 changelog entry
