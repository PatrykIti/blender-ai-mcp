# 262. Guided incomplete-build iterate hold

Date: 2026-04-26

## Summary

Closed a guided iteration state-transition regression where a no-action stage
compare could move an incomplete guided build to `finish_or_stop` while
required roles were still missing.

## What Changed

- in `server/adapters/mcp/areas/reference.py`:
  - keep `reference_iterate_stage_checkpoint(...)` on
    `loop_disposition="continue_build"` whenever the active guided build step
    still has required `missing_roles`
  - clear the stop reason for that forced hold so the response does not mix a
    build-continuation disposition with stop guidance
  - emit the guided-governor hold message for incomplete builds even when the
    compare result has no `correction_focus` or `action_hints`
- in focused unit tests:
  - covered a no-action compare result during an incomplete
    `place_secondary_parts` step
  - asserted that the persisted guided flow stays on the current build step and
    does not mark the unfinished role slice complete

## Documentation

- updated `README.md` guided iterate notes
- updated `_docs/_MCP_SERVER/README.md` guided flow contract notes

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q -k "holds_incomplete_build_on_no_action_compare or holds_build_when_role_group_is_incomplete"`
  - result on this machine: `2 passed, 59 deselected`
- `poetry run ruff check server/adapters/mcp/areas/reference.py tests/unit/adapters/mcp/test_reference_images.py`
  - result on this machine: passed
- `poetry run mypy server/adapters/mcp/areas/reference.py`
  - result on this machine: passed
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --files README.md _docs/_MCP_SERVER/README.md _docs/_CHANGELOG/README.md _docs/_CHANGELOG/262-2026-04-26-guided-incomplete-build-iterate-hold.md server/adapters/mcp/areas/reference.py tests/unit/adapters/mcp/test_reference_images.py`
  - result on this machine: passed
- `PYTHONPATH=. poetry run pytest tests/unit -q`
  - result on this machine: `3098 passed`
