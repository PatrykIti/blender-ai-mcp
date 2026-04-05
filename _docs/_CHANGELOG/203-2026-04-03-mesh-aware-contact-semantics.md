# 203. Mesh-aware contact semantics

Date: 2026-04-03

## Summary

Started `TASK-126` by replacing bbox-only contact/gap truth with a mesh-aware
surface path for mesh-object pairs.

## What Changed

- `scene_measure_gap(...)` now prefers a mesh-surface gap path for `MESH`
  pairs and reports:
  - `measurement_basis`
  - `bbox_gap`
  - `bbox_axis_gap`
  - `bbox_relation`
  - `nearest_points`
- `scene_measure_overlap(...)` now distinguishes:
  - actual mesh overlap / contact / disjoint semantics
  - from coarse bbox touching diagnostics
- `scene_assert_contact(...)` now consumes the mesh-aware path for mesh pairs
  and exposes the measurement basis in assertion details
- added unit coverage for the canonical failure mode:
  - bbox-touching
  - visibly gapped mesh surfaces
  - assertion must fail
- added an E2E regression for a small-sphere-on-large-sphere case where bbox
  touching should no longer be treated as real contact

## Why

The old truth layer could report `touching` or pass `scene_assert_contact(...)`
when curved primitives still showed a visible viewport gap. That broke trust in
macro verification and hybrid-loop truth output. The new mesh-aware path is the
first step toward making truth semantics match visible fit instead of bbox math
alone.
