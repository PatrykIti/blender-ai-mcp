# TASK-152-01: Spatial Tool Prompting And Seam Interpretation Guidance

**Parent:** [TASK-152](./TASK-152_Guided_Spatial_Gate_Usability_Prompt_Semantics_And_Inspect_Alignment.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Make `llm-guided` prompt assets and public docs explicit about:

- when `scene_scope_graph(...)`, `scene_relation_graph(...)`, and
  `scene_view_diagnostics(...)` are usable
- the fact that attached reference images are the primary grounding for the
  initial blockout shape/placement
- why full semantic object names matter for heuristic role/seam inference
- how the model should choose valid scope
- which seam verdicts still require correction versus which are acceptable for
  organic blockout embeddings

## Repository Touchpoints

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Acceptance Criteria

- prompt/docs guidance says plainly that spatial tools need explicit scope
- prompt/docs guidance tells the model to actually inspect/read the attached
  reference images before deciding how to start the blockout
- prompt/docs guidance tells the model to prefer full semantic object names
  like `ForeLeg_L`, `HindLeg_R`, `Head`, `Body`, `Tail` over abbreviations that
  degrade heuristics
- prompt/docs guidance says the initial spatial gate is meaningful only after a
  real target scope exists
- prompt/docs guidance distinguishes:
  - `intersecting` as potentially acceptable for embedded ear/head or
    snout/head blockout seams
  - `floating_gap` as still actionable for head/body, tail/body, and limb/body
    segment seams

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-152-01-01](./TASK-152-01-01_Valid_Spatial_Scope_Preconditions_In_LLM_Guides.md) | Clarify valid scope preconditions and when the spatial gate is actually satisfiable |
| 2 | [TASK-152-01-02](./TASK-152-01-02_Reference_Image_Grounding_In_Guided_Blockout_Prompts.md) | Make attached reference images an explicit required grounding input for initial guided blockout decisions |
| 3 | [TASK-152-01-03](./TASK-152-01-03_Heuristic_Friendly_Object_Naming_Guidance_And_Gates.md) | Make naming guidance explicit and consider lightweight gates/warnings for opaque abbreviations |
| 4 | [TASK-152-01-04](./TASK-152-01-04_Seam_Verdict_Interpretation_For_Guided_Creature_Blockout.md) | Clarify which seam verdicts are acceptable vs actionable during creature blockout |

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Changelog Impact

- include in the parent TASK-152 changelog entry
