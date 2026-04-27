# TASK-145-02-03: Bounded Sculpt Metadata and Recommendation Policy

**Parent:** [TASK-145-02](./TASK-145-02_Sculpt_Handoff_Context_And_Precondition_Model.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Depends On:** [TASK-145-02-01](./TASK-145-02-01_Sculpt_Handoff_Contract_And_Local_Target_Semantics.md), [TASK-145-02-02](./TASK-145-02-02_View_Relation_And_Proportion_Preconditions_For_Sculpt.md)

## Objective

Align sculpt handoff with the real sculpt capability surface so the guided
runtime recommends only the intended deterministic subset and does not reopen
brush/setup or broad whole-mesh sculpt paths by accident.

## Repository Touchpoints

- `server/adapters/mcp/areas/sculpt.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/router/infrastructure/tools_metadata/sculpt/`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_search_surface.py`

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

## Changelog Impact

- include in the parent TASK-145 changelog entry when shipped

## Status / Board Update

- no board change in this planning-only branch
