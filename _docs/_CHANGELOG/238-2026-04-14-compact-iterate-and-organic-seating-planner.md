# 238. Compact iterate and organic seating planner

Date: 2026-04-14

## Summary

Completed the first implementation slices for TASK-145-01-04 and
TASK-145-01-05:

- compact iterate responses now slim the nested debug `compare_result`
- intersecting rounded organic segment seams now prefer surface seating over
  bbox side-push contact repair

## What Changed

- added `debug_payload_omitted` to `ReferenceIterateStageCheckpointResponseContract`
- in compact iterate responses, the nested `compare_result` now omits duplicated
  heavy debug fields such as full truth bundle, truth follow-up, full candidate
  evidence, full silhouette metrics, action hints, and captures
- top-level iterate response fields still carry the actionable summaries used by
  the LLM: loop disposition, correction focus, candidates, truth follow-up,
  budget control, route, and handoff
- adjusted truth follow-up macro candidate selection so intersecting organic
  segment attachments (`head_body`, `tail_body`, `limb_body`) prefer
  `macro_attach_part_to_surface`
- improved `macro_attach_part_to_surface` with a bounded nearest-point
  mesh-surface nudge after bbox seating, closing small mesh gaps that remain
  after rounded parts reach coarse bbox contact
- fixed surface-side inference so a part currently on the negative side of an
  anchor receives `surface_side="negative"` in generated attach macro hints
- updated MCP/prompt docs for compact debug split and rounded organic seating
  repair behavior

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
  - result on this machine: `56 passed`
- `PYTHONPATH=. poetry run pytest tests/unit/tools/macro/test_macro_attach_part_to_surface.py -q`
  - result on this machine: `5 passed`
