# TASK-166-03: Deterministic CV And Optional PyTorch Perceiver Sidecars

**Parent:** [TASK-166](./TASK-166_Hierarchical_Reference_Compare_Perceived_Evidence_And_Budget_Control.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High
**Objective:** Feed compact image evidence into compare packets through always-on lightweight CV and optional heavier PyTorch-based perception adapters.

## Repository Touchpoints

- `server/adapters/mcp/vision/reference_support.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/reference.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `_docs/_VISION/README.md`

## Implementation Notes

- Always-on lightweight CV should pre-chew low-level image facts.
- Optional PyTorch sidecars should enrich packets when they materially improve
  compare quality, but remain support-only.

## Current Flow Integration

- Always-on CV should feed packet-level evidence slots on the staged compare
  family before the LLM compare question is assembled.
- Optional PyTorch sidecars should extend the existing `reference_support.py`
  seam instead of creating a second parallel perception stack.
- Packet compare should consume these pre-chewed facts so the LLM is asked
  narrower questions rather than raw broad image interpretation.
- Compare-time evidence should extend the staged compare contracts without
  overloading RU-only fields or duplicating `silhouette_analysis` /
  `part_segmentation` as a parallel evidence channel.

## Acceptance Criteria

- packet evidence no longer depends only on raw LLM perception
- optional heavy adapters stay advisory-only and explicitly bounded
- support evidence lands in the existing staged compare family rather than in a
  second planner/evidence flow

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- targeted unit coverage for compare-time support-evidence shaping in
  `reference_support.py`
- selected integration/runtime proof when compare-time packet evidence changes
  the staged public payload

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`

## Changelog Impact

- include in the umbrella `_docs/_CHANGELOG/` entry when compare-time support
  evidence ships

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
