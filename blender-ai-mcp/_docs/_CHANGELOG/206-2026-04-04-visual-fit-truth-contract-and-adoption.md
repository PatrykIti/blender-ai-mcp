# 206. Visual-fit truth contract and adoption

Date: 2026-04-04

## Summary

Closed `TASK-126` by finishing the product contract, operator-facing wording,
and regression coverage for mesh-aware contact semantics vs bbox fallback
semantics.

## What Changed

- updated MCP adapter docstrings for:
  - `scene_measure_gap(...)`
  - `scene_measure_overlap(...)`
  - `scene_assert_contact(...)`
  so they now describe the current truth path instead of overclaiming bbox-only
  semantics
- aligned router tool metadata descriptions for the same scene truth tools with
  the mesh-surface-first contract
- added one product-level README section plus MCP/Vision doc updates that spell
  out:
  - mesh-surface truth when available
  - bbox fallback semantics when mesh-aware measurement is unavailable
- hybrid truth-followup summaries now explicitly call out the high-risk case
  where bounding boxes touch but real mesh surfaces still have a gap
- macro truth snapshots now carry the same contact-semantics note so operator
  diagnostics and bounded repair flows do not flatten that case into a generic
  contact result
- added focused regression coverage for:
  - hybrid truth-followup wording on bbox-touching but surface-separated pairs
  - macro truth summaries carrying the same note
  - docs coverage for the new product wording
- updated task files and board state to close the remaining TASK-126 slices

## Validation

- `poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/tools/macro/test_macro_align_part_with_contact.py tests/unit/tools/scene/test_scene_measure_tools.py tests/unit/tools/scene/test_scene_assert_tools.py tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `poetry run pytest tests/unit/router/infrastructure/test_mcp_tools_metadata_alignment.py tests/unit/adapters/mcp/test_contract_docs.py -q`
