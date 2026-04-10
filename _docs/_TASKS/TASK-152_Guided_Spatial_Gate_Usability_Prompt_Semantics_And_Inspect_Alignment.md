# TASK-152: Guided Spatial Gate Usability, Prompt Semantics, And Inspect Alignment

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Category:** Guided Runtime / Prompt Contract / Inspect Surface
**Estimated Effort:** Medium
**Follow-on After:** [TASK-151](./TASK-151_Spatial_Check_Freshness_Target_Binding_And_Guided_Rearm.md)

## Objective

Align `llm-guided` prompt guidance, spatial-tool usage guidance, and
`inspect_validate` runtime exposure so the model:

- actually uses attached reference images as the grounding input for how to
  start the blockout
- does not try to satisfy the spatial gate with empty or meaningless scope
- uses full heuristic-friendly object names instead of opaque abbreviations
- interprets seam verdicts consistently
- does not see contradictory signals between `allowed_families`,
  inspect-visible tools, and macro availability

## Business Problem

Recent real guided runs after TASK-151 show that the spatial tools themselves
work, but the model-facing guidance is still underspecified in several
ways:

1. **Spatial gate usability**
   prompt assets tell the model to respect `establish_spatial_context`, but do
   not say clearly enough that:
   - `scene_scope_graph(...)` / `scene_relation_graph(...)` need explicit
     `target_object`, `target_objects`, or `collection_name`
   - `scene_view_diagnostics(...)` requires an explicit scope
   - the gate is only meaningful once a real target scope exists

2. **Reference-grounding drift**
   guided creature/building sessions can still behave as if the attached
   reference images are administrative context rather than the primary visual
   grounding for how the initial masses should be shaped and placed.

3. **Name/heuristic drift**
   object-name heuristics work better with full semantic names like
   `ForeLeg_L`, `HindLeg_R`, `Tail`, `Head`, `Body`, but the current guidance
   does not strongly prevent abbreviations like `ForeL` / `HindR` that degrade
   role inference and seam pairing.

4. **Inspect/runtime inconsistency**
   guided sessions can reach `inspect_validate` while:
   - `guided_flow_state.allowed_families` still mentions
     `attachment_alignment`
   - inspect-visible tools do not expose all attachment macros
   - the model can rationalize real `floating_gap` seam failures as “expected”
     instead of actionable defects

This is therefore not just a docs wording issue.
It is a model-facing contract alignment problem between:

- prompt assets
- MCP docs / README
- visibility policy
- guided-flow family semantics
- blocked/exposed repair surface in `inspect_validate`

## Acceptance Criteria

- prompt assets explicitly explain when the spatial gate is actually
  satisfiable and how to provide valid scope to the spatial tools
- prompt assets explicitly tell the model to inspect/read attached references
  before deciding how to start the blockout
- prompt/docs guidance explicitly prefer full semantic object names that the
  heuristic layer can classify reliably
- prompt/docs guidance explicitly distinguishes:
  - acceptable embedded organic seams
  - unacceptable `floating_gap` segment/body seams
- `inspect_validate` no longer presents contradictory guidance about whether
  attachment repair macros are available/allowed
- regression coverage proves the chosen `inspect_validate` policy and docs stay
  aligned

## Repository Touchpoints

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/router_helper.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`
- `_docs/_TASKS/README.md`

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`

## Changelog Impact

- add a dedicated `_docs/_CHANGELOG/*` entry when this follow-on ships

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-152-01](./TASK-152-01_Spatial_Tool_Prompting_And_Seam_Interpretation_Guidance.md) | Make prompt/docs guidance explicit about valid scope preconditions, reference grounding, naming hygiene, and seam verdict interpretation |
| 2 | [TASK-152-02](./TASK-152-02_Inspect_Validate_Surface_And_Attachment_Family_Alignment.md) | Remove the contradiction between inspect-visible tools and `attachment_alignment` family semantics |
| 3 | [TASK-152-03](./TASK-152-03_Regression_And_Docs_Closeout_For_Guided_Spatial_Usability.md) | Lock the revised guided contract in with parity tests and docs closeout |

## Status / Board Update

- proposed as the next board-level follow-on after TASK-151 because the
  remaining failures are now primarily model-facing contract/alignment issues
  rather than missing spatial-state mechanics
