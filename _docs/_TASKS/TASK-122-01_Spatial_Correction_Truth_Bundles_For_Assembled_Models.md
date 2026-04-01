# TASK-122-01: Spatial Correction Truth Bundles For Assembled Models

**Parent:** [TASK-122](./TASK-122_Hybrid_Vision_Truth_And_Correction_Macro_Wave.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

## Objective

Build correction-oriented truth bundles on top of the existing measure/assert
family so assembled models can prove contact, gap, overlap, and alignment
problems instead of only inferring them visually.

## Business Problem

The repo already has the raw truth tools:

- `scene_measure_gap`
- `scene_measure_overlap`
- `scene_measure_alignment`
- `scene_assert_contact`
- `scene_assert_containment`
- `scene_assert_proportion`

But those tools still return mostly tool-local facts, not one correction-ready
bundle for a multi-part assembled target.

## Acceptance Criteria

- one assembled-model truth bundle can summarize contact/gap/overlap/alignment findings
- the correction loop can consume that bundle without ad hoc LLM interpretation
- truth findings stay deterministic and separate from vision interpretation

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/scene.py`
- `server/adapters/mcp/contracts/vision.py`
- `server/adapters/mcp/session_capabilities.py`
- `tests/unit/adapters/mcp/`
- `tests/unit/tools/scene/`
- `tests/e2e/vision/`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`

## Completion Update Requirements

- update the truth-bundle contract docs and loop docs in `_docs/` when a leaf here ships
- add or update unit coverage for contract shape and truth-bundle handoff behavior
- add or update E2E coverage when the shipped behavior depends on real scene state
- add the historical `_docs/_CHANGELOG/*` entry and sync the task board when this subtree changes promoted state

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-122-01-01](./TASK-122-01-01_Assembled_Target_Scope_And_Part_Group_Contract.md) | Define how assembled targets and part groups are named, scoped, and passed to truth bundles |
| 2 | [TASK-122-01-02](./TASK-122-01-02_Contact_Gap_Alignment_And_Overlap_Correction_Bundle.md) | Build one correction-ready truth bundle from existing measure/assert tools |
| 3 | [TASK-122-01-03](./TASK-122-01-03_Truth_Followup_Delivery_And_Loop_Handoff.md) | Expose truth findings as loop-ready follow-up payloads instead of isolated raw tool results |
