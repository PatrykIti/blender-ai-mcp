# TASK-143-03-02: Regression, Docs, and Prompt Surface Alignment

**Parent:** [TASK-143-03](./TASK-143-03_Goal_Aware_Disclosure_Guided_Adoption_And_Regression_Pack.md)
**Depends On:** [TASK-143-03-01](./TASK-143-03-01_Goal_Phase_Aware_Visibility_And_On_Demand_Expansion_Policy.md)
**Status:** ✅ Done
**Priority:** 🔴 High

**Completion Summary:** Completed on 2026-04-07. Public docs, prompt guidance,
task/changelog history, and regression coverage now all describe the shipped
scope/relation graph layer as explicit read-only artifacts rather than more
default stage-payload growth.

## Objective

Align the final TASK-143 story across docs, prompts, and regression coverage so
the shipped surface says the same thing as the actual runtime behavior.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`
- `_docs/LLM_GUIDE_V2.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_CHANGELOG/`

## Acceptance Criteria

- docs explain the graph layer as explicit read-only artifacts rather than as
  hidden stage-payload growth
- prompt/operator guidance explains when to query scope/relation graphs and
  when to stay on the existing checkpoint/truth loop only
- regression coverage protects:
  - stage-loop boundedness
  - guided surface footprint
  - truth-layer alignment with the graph semantics
- historical tracking requirements are called out for the implementation branch
  that actually ships TASK-143 behavior

## Docs To Update

- `_docs/LLM_GUIDE_V2.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`

## Changelog Impact

- add the TASK-143 historical `_docs/_CHANGELOG/*` entry when implementation
  lands

## Status / Board Update

- keep board tracking on `TASK-143`
- implementation branches should update `_docs/_TASKS/README.md` only if the
  promoted board state changes; this planning pass intentionally does not
