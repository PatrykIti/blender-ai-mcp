# 345. TASK-135 curved-tail profile gates

Date: 2026-05-11

Task: `TASK-135-02`

## Summary

Closed the curved-tail / organic appendage slice for the `TASK-135` creature
family by keeping the behavior on the generic quality-gate substrate and the
existing macro surface.

## Changes

- Derived curved, arched, curled, and bushy tail cues from reference
  understanding into normal `shape_profile` gates such as `tail_profile`.
- Added bounded profile/arc recommendations to `shape_profile` blockers,
  including `macro_adjust_segment_chain_arc(...)`.
- Expanded guided search recovery so active profile/arc/curve blockers can
  recover the existing ordered-chain arc macro.
- Added unit coverage for the derived gate, blocker recommendations, and active
  gate search recovery.
- Added Blender-backed proof that a `TailRoot` segment can remain seated to
  `Body` while `TailMid` and `TailTip` arc through
  `macro_adjust_segment_chain_arc(...)`.
- Updated task, prompt, MCP, vision, tool-summary, and test docs for the
  shipped generic-gate tail-profile path.

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_intake.py::test_shape_profile_gate_recommends_bounded_profile_and_arc_tools tests/unit/adapters/mcp/test_search_surface.py::test_failed_tail_profile_gate_search_surfaces_arc_repair_tool tests/unit/adapters/mcp/test_reference_images.py::test_refresh_reference_understanding_summary_derives_curved_tail_shape_profile_gate -q` (`3 passed`)
- `PYTEST_ADDOPTS='-k macro_adjust_segment_chain_arc' poetry run python scripts/run_e2e_tests.py --skip-build` (`2 passed, 472 deselected`)
- `poetry run ruff check server/adapters/mcp/contracts/quality_gates.py server/adapters/mcp/discovery/search_surface.py server/adapters/mcp/vision/parsing.py server/adapters/mcp/vision/reference_gates.py server/adapters/mcp/areas/reference_understanding.py tests/unit/adapters/mcp/test_quality_gate_intake.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_reference_images.py tests/e2e/tools/macro/test_macro_adjust_segment_chain_arc.py`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
- `git diff --check`
