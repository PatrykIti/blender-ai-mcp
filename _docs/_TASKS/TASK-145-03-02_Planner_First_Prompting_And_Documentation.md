# TASK-145-03-02: Planner-First Prompting and Documentation

**Parent:** [TASK-145-03](./TASK-145-03_Guided_Adoption_Visibility_Docs_And_Regression_Pack.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Depends On:** [TASK-145-03-01](./TASK-145-03-01_Planner_And_Sculpt_Delivery_On_LLM_Guided.md)

## Objective

Update the guided documentation layer so the operator learns a consistent
planner-first read order:

- planner summary / family decision first
- sculpt blockers and handoff context next
- lower-level correction hints and raw vision prose after that

## Implementation Notes

- Prompt/docs wording should match the shipped compact stage response fields.
  Do not document hidden tools or future-only planner surfaces as default
  behavior.
- Correct existing spatial-helper wording drift while updating planner-first
  docs: `scene_scope_graph`, `scene_relation_graph`, and
  `scene_view_diagnostics` are current read-only `llm-guided` spatial support
  tools, so docs must not describe them as kept off guided bootstrap by default.
- The read order should explicitly preserve the responsibility boundary:
  deterministic evidence and planner policy first, vision prose as advisory
  context, and low-level tools only after the bounded family/handoff decision.
- If TASK-157 gate wording is mentioned, keep it as a downstream quality-gate
  consumer. TASK-145 prompt text should not claim gate pass/fail authority.

## Pseudocode

```text
Read planner_summary.selected_family and blockers.
If blockers exist, inspect the named evidence/tool before editing.
If sculpt_handoff is blocked, use the recommended macro/modeling/inspect path.
Use vision prose only to explain or prioritize, not to override truth evidence.
```

## Repository Touchpoints

- `server/adapters/mcp/prompts/prompt_catalog.py`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`
- `_docs/_VISION/CROSS_DOMAIN_REFINEMENT_ROUTING_EVAL.md`
- `tests/unit/adapters/mcp/test_prompt_catalog.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Validation Category

- Prompt/docs tests should assert planner-first ordering and absence of hidden
  non-default tool instructions.
- Targeted command:
  `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_prompt_catalog.py tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- Docs/preflight:
  `git diff --check`

## Acceptance Criteria

- prompt/docs ordering consistently tells the model to inspect planner outputs
  before dropping into free-form edits
- guided docs explain that sculpt remains bounded and preconditioned rather
  than a default fallback
- documentation stays aligned with the actual shaped public surface and does
  not instruct hidden or non-default tools
- public docs and inventory agree that current spatial helper tools are visible
  read-only support tools on `llm-guided`, not future or hidden planner surfaces

## Docs To Update

- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`
- `_docs/_VISION/CROSS_DOMAIN_REFINEMENT_ROUTING_EVAL.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_prompt_catalog.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Changelog Impact

- include in the parent TASK-145 changelog entry when shipped

## Status / Board Update

- no board-count change is needed while TASK-145 remains the promoted open
  board item
