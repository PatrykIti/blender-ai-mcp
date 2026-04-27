# 251. Guided explicit-scope binding and startup-subset bootstrap

Date: 2026-04-22

## Summary

Adjusted the latest guided bootstrap/scope heuristics so:

- explicit scope binding no longer rejects valid objects just because their
  names look like placeholders or contain helper tokens
- the empty-scene bootstrap shortcut still applies to startup-scene subsets
  such as `Cube + Camera`, without treating every lone default-named mesh as
  empty

## What Changed

- in `server/adapters/mcp/session_capabilities.py`:
  - explicit non-scene scopes now bind from caller intent, while the default
    root `Collection` placeholder still remains non-bindable when empty
- in `server/adapters/mcp/areas/router.py`:
  - `_scene_has_meaningful_guided_objects()` now keeps the empty-scene
    bootstrap path for startup-scene subsets, but still treats a real lone mesh
    named `Cube` / `Sphere` / etc. as existing geometry
- updated public docs in:
  - `README.md`
  - `_docs/_MCP_SERVER/README.md`
  so the guided bootstrap / explicit-scope story matches the shipped runtime

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit -q`
  - result on this machine: `3065 passed`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
  - result on this machine: passed
