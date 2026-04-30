# TASK-145-02-03: Bounded Sculpt Metadata and Recommendation Policy

**Parent:** [TASK-145-02](./TASK-145-02_Sculpt_Handoff_Context_And_Precondition_Model.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Depends On:** [TASK-145-02-01](./TASK-145-02-01_Sculpt_Handoff_Contract_And_Local_Target_Semantics.md), [TASK-145-02-02](./TASK-145-02-02_View_Relation_And_Proportion_Preconditions_For_Sculpt.md)

## Objective

Align sculpt handoff with the real sculpt capability surface so the guided
runtime recommends only the intended deterministic subset and does not reopen
brush/setup or broad whole-mesh sculpt paths by accident.

## Implementation Notes

- Update the real recommendation owners, not only metadata:
  - `ReferenceRefinementHandoffContract`
  - `_SCULPT_RECOMMENDED_TOOLS`
  - `_build_refinement_handoff(...)`
- Metadata/search wording must describe the same bounded deterministic subset
  that the handoff can actually recommend.
- If a sculpt tool is visible in search but never recommended by the bounded
  handoff, document why it is excluded from planner-driven handoff.
- Progressive unlock, if implemented later, must be handoff-state driven and
  limited to the same deterministic subset.

## Repository Touchpoints

- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/areas/sculpt.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/router/infrastructure/tools_metadata/sculpt/`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_reference_images.py`

## Acceptance Criteria

- sculpt recommendation policy is explicit about which sculpt tools are
  eligible for planner-driven handoff
- metadata/search wording reflects local deterministic region work, not broad
  "just sculpt it" behavior
- `llm-guided` does not auto-expose the whole sculpt capability by default
- if progressive unlock is later allowed, it is limited to the same bounded
  deterministic subset

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_PROMPTS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_reference_images.py`

## Validation Category

- Targeted unit lane:
  `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_guided_mode.py tests/unit/adapters/mcp/test_search_surface.py -q`

## Changelog Impact

- include in the parent TASK-145 changelog entry when shipped

## Status / Board Update

- no board-count change is needed while TASK-145 remains the promoted open
  board item
