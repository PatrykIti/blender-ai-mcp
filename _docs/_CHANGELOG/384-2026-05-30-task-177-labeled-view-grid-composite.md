# 384. TASK-177-03 optional labelled multi-view grid composite

Date: 2026-05-30

## Summary

Implemented `TASK-177-03`: a deterministic helper that tiles several capture
views into one labelled montage (IG-VLM style), for the case where a single
annotated image outperforms many separate images (or a tight image budget).

## Changes

- new `server/adapters/mcp/vision/composite.py`: `build_labeled_view_grid(tiles,
  output_path, ...)` lays out `(label, image_path)` tiles in a deterministic grid
  with a per-tile label band; returns None for no tiles and renders an empty
  labelled cell for an unreadable tile instead of aborting.

## Tests

- `tests/unit/adapters/mcp/test_vision_composite.py`: grid dimensions, empty-input
  None, and unreadable-tile survival
- `ruff`/`mypy` clean; full `tests/unit` green

## Follow-on

Wiring the grid into the live capture path behind a config flag (and choosing
when to send the grid vs separate images) is a small additive follow-up; the
deterministic builder is in place.

## Research Basis

IG-VLM (arXiv:2403.18406): a single labelled frame grid can match or beat many
separate frames for some models. Re-measure on `tests/fixtures/vision_eval`.
