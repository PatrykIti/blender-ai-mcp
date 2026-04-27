# 247. Guided startup bootstrap and quoted-name registration

Date: 2026-04-22

## Summary

Fixed two guided-session correctness issues:

- Blender's stock startup scene now still takes the empty-scene bootstrap path
  even though it contains the default `Cube`
- guided-role convenience registration now preserves object names containing
  apostrophes

## What Changed

- in `server/adapters/mcp/areas/router.py`:
  - refined `_scene_has_meaningful_guided_objects()` so one lone default
    placeholder primitive still counts as an empty startup scene, while a
    multi-object placeholder blockout counts as a real non-empty blockout
- in `server/adapters/mcp/areas/modeling.py`:
  - changed guided create/transform success parsing so names such as
    `King's Crown` survive convenience registration intact
- updated public docs in:
  - `README.md`
  - `_docs/_MCP_SERVER/README.md`
  so the bootstrap and quoted-name behavior matches the shipped runtime

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit -q`
  - result on this machine: `3047 passed`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
  - result on this machine: passed
