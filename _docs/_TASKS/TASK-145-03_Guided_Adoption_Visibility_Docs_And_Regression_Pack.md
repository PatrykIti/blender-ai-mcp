# TASK-145-03: Guided Adoption, Visibility, Docs, and Regression Pack

**Parent:** [TASK-145](./TASK-145_Spatial_Repair_Planner_And_Sculpt_Handoff_Context.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Depends On:** [TASK-145-01](./TASK-145-01_Repair_Planner_Payload_And_Family_Selection_Policy.md), [TASK-145-02](./TASK-145-02_Sculpt_Handoff_Context_And_Precondition_Model.md)

## Objective

Ship planner-first operating guidance for `llm-guided` without reopening the
large-catalog problem. This means:

- shaping delivery on the public surface
- teaching prompt/docs consumers how to read planner output first
- locking the contract down with focused regression coverage

## Business Problem

The current repo already has the platform pieces needed for adoption:

- `visibility_policy.py`
- `guided_mode.py`
- `prompt_catalog.py`
- shaped prompt docs and search/discovery tests

But planner-first usage is still incomplete:

- prompt guidance is not yet consistently planner-first
- route/handoff ordering differs between docs
- search/visibility rules do not yet have a clear home for any future
  planner-context surface
- regression coverage is strong for the current loop, but not yet organized
  around the planner / sculpt-handoff contract that TASK-145 wants to harden

## Technical Direction

Use the current FastMCP-guided shaping stack instead of inventing a separate
adoption path:

- visibility and discovery remain platform-owned
- planner / sculpt policy remains deterministic and typed
- docs and prompts teach the compact planner story before lower-level edits
- regression coverage protects compact delivery and recommendation-only sculpt
  behavior

## Repository Touchpoints

- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/guided_mode.py`
- `server/adapters/mcp/platform/capability_manifest.py`
- `server/adapters/mcp/prompts/prompt_catalog.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_prompt_catalog.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/vision/test_reference_guided_creature_comparison.py`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_VISION/README.md`
- `_docs/_VISION/CROSS_DOMAIN_REFINEMENT_ROUTING_EVAL.md`

## Acceptance Criteria

- planner / sculpt-handoff delivery on `llm-guided` remains small and
  intentional
- prompt and docs guidance consistently teaches planner-first interpretation
  before broader free-form edits
- search / visibility / prompt selection rules do not leak a broad new planner
  or sculpt family onto bootstrap by default
- regression coverage protects the compact delivery model and sculpt
  recommendation boundaries

## Docs To Update

- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`
- `_docs/_VISION/CROSS_DOMAIN_REFINEMENT_ROUTING_EVAL.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_prompt_catalog.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/vision/test_reference_guided_creature_comparison.py`

## Changelog Impact

- add a `_docs/_CHANGELOG/*.md` entry when planner-first guided adoption ships

## Status / Board Update

- planning-only execution-tree split: keep `_docs/_TASKS/README.md` unchanged
  in this branch
- when this subtask is implemented and closed later, update parent/child
  statuses and the task board in the same allowed branch

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-145-03-01](./TASK-145-03-01_Planner_And_Sculpt_Delivery_On_LLM_Guided.md) | Decide how compact planner and sculpt-context artifacts are surfaced or discovered on `llm-guided` without widening bootstrap |
| 2 | [TASK-145-03-02](./TASK-145-03-02_Planner_First_Prompting_And_Documentation.md) | Update prompts/docs so operators read planner output before dropping to lower-level tools |
| 3 | [TASK-145-03-03](./TASK-145-03-03_Regression_Pack_For_Planner_And_Sculpt_Handoff.md) | Protect the new planner / sculpt-handoff contract with focused unit, discovery, prompt, and e2e coverage |
