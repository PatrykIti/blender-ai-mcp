# 266. Guided visibility and stage capture focus

Date: 2026-04-27

## Summary

Closed guided runtime follow-ups where stale spatial-state updates and
recoverable iterate transitions could leave clients on an old visible tool
surface, and where collection/object-set stage captures could use an unfocused
viewport when no explicit primary target was supplied.

## What Changed

- in `server/adapters/mcp/session_capabilities.py`:
  - reapplied FastMCP visibility immediately after
    `mark_guided_spatial_state_stale(...)` persists
    `spatial_refresh_required` and the refresh-only family gate
- in `server/adapters/mcp/areas/reference.py`:
  - focused collection and multi-object stage captures on the assembled target
    scope's primary target when `target_object` is omitted
  - reapplied guided visibility when an error-stage iterate transition advances
    to `inspect_validate` or `finish_or_stop`
- in unit tests:
  - covered dirty-state visibility refresh after `scene_duplicate_object`
  - covered collection/object-set capture focus fallback
  - covered error iterate transitions for both inspect and stop surfaces

## Documentation

- updated `README.md` guided runtime notes
- updated `_docs/_MCP_SERVER/README.md` guided flow and stage-compare notes
- verified trailing-whitespace validation for
  `_docs/Spacial-intelligence-upgrades-for-blender-ai-mcp.md`

## Validation

- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run trailing-whitespace --files _docs/Spacial-intelligence-upgrades-for-blender-ai-mcp.md`
  - result on this machine: passed
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py::test_mark_guided_spatial_state_stale_reapplies_visibility tests/unit/adapters/mcp/test_reference_images.py::test_reference_compare_stage_checkpoint_can_expand_collection_scope tests/unit/adapters/mcp/test_reference_images.py::test_reference_compare_stage_checkpoint_can_track_explicit_object_set_scope tests/unit/adapters/mcp/test_reference_images.py::test_reference_iterate_stage_checkpoint_falls_back_to_truth_handoff_when_vision_compare_errors tests/unit/adapters/mcp/test_reference_images.py::test_reference_iterate_stage_checkpoint_reapplies_visibility_on_error_stop -q`
  - result on this machine: `5 passed`
- `poetry run ruff check server/adapters/mcp/session_capabilities.py server/adapters/mcp/areas/reference.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_reference_images.py`
  - result on this machine: passed
- `poetry run mypy server/adapters/mcp/session_capabilities.py server/adapters/mcp/areas/reference.py`
  - result on this machine: passed
- `git diff --check`
  - result on this machine: passed
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --files README.md _docs/_MCP_SERVER/README.md _docs/_CHANGELOG/README.md _docs/_CHANGELOG/266-2026-04-27-guided-visibility-and-stage-capture-focus.md _docs/Spacial-intelligence-upgrades-for-blender-ai-mcp.md server/adapters/mcp/session_capabilities.py server/adapters/mcp/areas/reference.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_reference_images.py`
  - result on this machine: passed
- `PYTHONPATH=. poetry run pytest tests/unit -q`
  - result on this machine: `3113 passed`
