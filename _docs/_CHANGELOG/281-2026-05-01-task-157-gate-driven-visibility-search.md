# TASK-157 gate-driven visibility and search

Date: 2026-05-01

## Summary

- Extended existing guided visibility rules with optional `active_gate_plan`
  blocker input.
- Failed seam/support gates now expose bounded relation, measure/assert, and
  macro repair tools without opening the broad catalog.
- Shape/profile/refinement gates wait behind unresolved required seam/support
  blockers before exposing refinement tools.
- `search_tools(...)` now recognizes active gate recovery queries and returns
  bounded gate verifier/repair tools instead of recommending goal reset.
- Documented the visibility/search boundary in MCP, prompt, router boundary,
  test, task, and changelog docs.

## Validation

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_search_surface.py::test_failed_attachment_gate_search_surfaces_bounded_repair_tools tests/unit/adapters/mcp/test_search_surface.py::test_active_gate_recovery_search_does_not_recommend_goal_reset tests/unit/adapters/mcp/test_visibility_policy.py::test_gate_blocker_visibility_exposes_bounded_attachment_repair_tools tests/unit/adapters/mcp/test_visibility_policy.py::test_shape_profile_gate_waits_behind_unresolved_seam_gate -v`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_quality_gate_contracts.py tests/unit/adapters/mcp/test_quality_gate_verifier.py tests/unit/adapters/mcp/test_quality_gate_intake.py -v`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --files README.md _docs/AVAILABLE_TOOLS_SUMMARY.md _docs/_CHANGELOG/README.md _docs/_CHANGELOG/281-2026-05-01-task-157-gate-driven-visibility-search.md _docs/_MCP_SERVER/README.md _docs/_PROMPTS/README.md _docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md _docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md _docs/_TASKS/README.md _docs/_TASKS/TASK-157-03-01_Gate_Driven_Visibility_Search_And_Recovery_Policy.md _docs/_TASKS/TASK-157-03_Guided_Flow_Gate_Runtime_Integration.md _docs/_TASKS/TASK-157_Goal_Derived_Quality_Gates_And_Deterministic_Verification.md _docs/_TESTS/README.md server/adapters/mcp/discovery/search_surface.py server/adapters/mcp/guided_mode.py server/adapters/mcp/session_capabilities.py server/adapters/mcp/transforms/visibility_policy.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_visibility_policy.py`
