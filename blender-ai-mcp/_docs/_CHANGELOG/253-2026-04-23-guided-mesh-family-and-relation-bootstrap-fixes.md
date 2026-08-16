# 253. Guided mesh family and relation/bootstrap fixes

Date: 2026-04-23

## Summary

Fixed three guided-flow correctness gaps:

- visible mesh edit tools now resolve to a guided family instead of bypassing
  family-based execution policy and spatial dirty-state rearming
- mixed creature relation scopes keep non-seam fallback pairs instead of
  dropping unclassified objects when required creature seams exist
- single default-named mesh scenes such as `Cube + Camera + Light` now count
  as existing geometry to inspect, not as empty-scene bootstrap input

## What Changed

- in `server/adapters/mcp/transforms/visibility_policy.py`:
  - classified `mesh_extrude_region`, `mesh_loop_cut`, `mesh_bevel`,
    `mesh_symmetrize`, `mesh_merge_by_distance`, and `mesh_dissolve` as
    `secondary_parts` for guided policy checks
- in `server/application/services/spatial_graph.py`:
  - added primary-target fallback relation pairs for objects that are not
    already covered by required creature seams
- in `server/adapters/mcp/areas/router.py`:
  - simplified non-empty scene detection so any non-helper scene object counts
    as meaningful geometry, regardless of default primitive-style names
- updated public docs in:
  - `README.md`
  - `_docs/_MCP_SERVER/README.md`
  so the guided mesh-edit, relation-graph, and bootstrap behavior matches the
  shipped runtime

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit -q`
  - result on this machine: `3076 passed`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
  - result on this machine: passed
