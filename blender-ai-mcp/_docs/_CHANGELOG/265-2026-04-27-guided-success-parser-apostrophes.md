# 265. Guided success parser apostrophes

Date: 2026-04-27

## Summary

Closed a guided post-processing regression where quoted success-string parsing
could mishandle object names that contain apostrophes, causing successful
mutations to skip stale-state marking or guided registry synchronization.

## What Changed

- in `server/adapters/mcp/router_helper.py`:
  - made create, transform, join, and rename success patterns capture quoted
    object names greedily so embedded apostrophes are treated as part of the
    name
  - kept failure strings outside the success parser so failed mutations still
    do not re-arm guided spatial state
- in focused unit tests:
  - covered `modeling_create_primitive`, `modeling_transform_object`,
    `scene_rename_object`, and `modeling_join_objects` success detection for
    names such as `O'Brien_Block`
  - covered the routed rename path with an apostrophe-containing name and a
    collision suffix so guided registry sync keeps the full object name

## Documentation

- updated `README.md` guided runtime notes
- updated `_docs/_MCP_SERVER/README.md` guided flow contract notes

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_context_bridge.py -q -k "apostrophes_inside_object_names or apostrophe_name_with_collision_suffix"`
  - result on this machine: `5 passed, 33 deselected`
- `poetry run ruff check server/adapters/mcp/router_helper.py tests/unit/adapters/mcp/test_context_bridge.py`
  - result on this machine: passed
- `poetry run mypy server/adapters/mcp/router_helper.py`
  - result on this machine: passed
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --files README.md _docs/_MCP_SERVER/README.md _docs/_CHANGELOG/README.md _docs/_CHANGELOG/265-2026-04-27-guided-success-parser-apostrophes.md server/adapters/mcp/router_helper.py tests/unit/adapters/mcp/test_context_bridge.py`
  - result on this machine: passed
- `PYTHONPATH=. poetry run pytest tests/unit -q`
  - result on this machine: `3111 passed`
