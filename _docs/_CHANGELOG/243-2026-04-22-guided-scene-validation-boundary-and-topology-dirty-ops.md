# 243. Guided scene validation boundary and topology dirty ops

Date: 2026-04-22

## Summary

Tightened the guided-session consistency boundary in two places:

- destructive topology-changing modeling ops now re-arm guided spatial checks
- public guided part registration keeps hard Blender-scene validation, while
  internal session helpers stay usable in pure server-side/test paths

## What Changed

- in `server/adapters/mcp/session_capabilities.py`:
  - added `modeling_join_objects` and `modeling_separate_object` to the
    guided spatial-dirty tool set
  - split guided object-name handling into:
    - one pure normalization helper for internal session-state updates
    - one explicit Blender-scene validation helper for public registration and
      rename synchronization
- in `server/adapters/mcp/areas/router.py`:
  - `guided_register_part(...)` now performs the public existing-object
    validation before mutating guided session state
  - invalid guided roles are still rejected before scene validation so
    domain/overlay errors are not masked by transport failures
- updated operator docs so README and MCP docs now state that:
  - join/separate re-arm guided spatial checks
  - public `guided_register_part(...)` fails clearly when Blender scene
    validation is unavailable instead of registering an unverified object name

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit -q`
  - result on this machine: `3032 passed`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
  - result on this machine: passed
