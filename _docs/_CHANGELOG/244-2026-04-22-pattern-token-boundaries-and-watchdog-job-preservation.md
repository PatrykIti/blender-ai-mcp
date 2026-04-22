# 244. Pattern, token-boundary, and watchdog job preservation fixes

Date: 2026-04-22

## Summary

Closed four correctness gaps across the guided/runtime stack:

- explicit goals without an exact workflow match now still allow strong
  pattern-suggested workflow expansion
- guided naming no longer accepts unrelated substring matches such as
  `Heart` -> `ear_pair`
- spatial role inference no longer treats helper-style names such as
  `TruthBodyAnchorHead` as accidental creature anchors/parts
- addon RPC watchdog restarts now preserve background job tracking state

## What Changed

- in `server/router/application/triggerer/workflow_triggerer.py`:
  - restored `pattern.suggested_workflow` priority ahead of heuristic
    suppression for explicit-goal/manual-flow sessions
- in `server/adapters/mcp/guided_naming_policy.py`:
  - changed strong semantic-name matching from raw substring search to
    token-boundary / full-token matching
- in `server/application/services/spatial_graph.py`:
  - changed role-hint inference from raw substring search to token-aware
    matching so helper-style names do not become accidental semantic parts
- in `blender_addon/infrastructure/rpc_server.py`:
  - split server shutdown so watchdog self-heal restarts do not clear
    `background_jobs`
- updated public docs in:
  - `README.md`
  - `_docs/_MCP_SERVER/README.md`
  - `_docs/_ADDON/README.md`
  so operator-facing behavior matches the shipped implementation

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit -q`
  - result on this machine: `3035 passed`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
  - result on this machine: passed
