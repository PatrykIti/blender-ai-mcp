# 248. Guided pair semantics and post-nudge capture refresh

Date: 2026-04-22

## Summary

Fixed two correctness gaps in the guided spatial/macro reporting layer:

- support/symmetry semantics are now preserved on duplicate relation-pair keys
  instead of being dropped behind a generic primary-target edge
- `macro_attach_part_to_surface(...)` now refreshes capture artifacts after the
  extra mesh-surface nudge so returned images reflect the final pose

## What Changed

- in `server/application/services/spatial_graph.py`:
  - merged support/symmetry annotations onto existing planned pair keys instead
    of dropping them when a generic pair already exists
  - refined `failing_pairs` scoring so healthy support/symmetry pairs do not
    fail just because contact/alignment checks are not attachment-like
- in `server/application/tool_handlers/macro_handler.py`:
  - refreshed `capture_bundle.captures_after` and truth summary after the
    mesh-surface nudge branch inside `macro_attach_part_to_surface(...)`
- added regression coverage in:
  - `tests/unit/tools/scene/test_spatial_graph_service.py`
  - `tests/unit/tools/macro/test_macro_attach_part_to_surface.py`
- updated public docs in:
  - `README.md`
  - `_docs/_MCP_SERVER/README.md`
  so guided operators see the shipped support/symmetry and capture-bundle
  behavior

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit -q`
  - result on this machine: `3051 passed`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
  - result on this machine: passed
