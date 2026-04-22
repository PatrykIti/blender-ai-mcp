# 246. Guided failed-mutation guards and non-empty blockout detection

Date: 2026-04-22

## Summary

Fixed two guided-session control issues:

- failed plain-string mutation results no longer mutate guided session state
- scenes containing only default-named primitive blockout meshes now count as
  non-empty for guided bootstrap decisions

## What Changed

- in `server/adapters/mcp/router_helper.py`:
  - changed string success detection for guided mutation hooks from a permissive
    “not error/failed” fallback to explicit success-shape checks for the
    mutating tools that can re-arm spatial state or rewrite guided registry
- in `server/adapters/mcp/areas/router.py`:
  - changed `_scene_has_meaningful_guided_objects()` so ordinary mesh objects
    named `Cube`, `Sphere`, `Cone`, etc. still count as an existing rough
    blockout for the empty-scene bootstrap decision
- updated public docs in:
  - `README.md`
  - `_docs/_MCP_SERVER/README.md`
  so the guided bootstrap and failed-mutation behavior matches runtime reality

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit -q`
  - result on this machine: `3043 passed`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
  - result on this machine: passed
