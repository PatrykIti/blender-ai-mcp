# TASK-166-03-02: Optional PyTorch Perceiver Adapters

**Parent:** [TASK-166-03](./TASK-166-03_Deterministic_CV_And_Optional_PyTorch_Perceiver_Sidecars.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High
**Objective:** Define the optional PyTorch-based perception adapters that can enrich compare packets when lightweight CV is not enough.

## Repository Touchpoints

- `server/adapters/mcp/vision/reference_support.py`
- `server/infrastructure/config.py`
- `_docs/_VISION/README.md`

## Implementation Notes

- Candidate adapters:
  - SigLIP2 / CLIP / DINOv2 for style or coarse similarity signals
  - SAM2-style segmentation for packet-level masks
  - GroundingDINO / OWL-ViT style part proposals for text-conditioned part cues
- Keep them default-off unless one adapter graduates into a clearly justified
  default support path.

## Acceptance Criteria

- optional heavy adapters are scoped as support-only enrichers
- the task family names clear upgrade criteria before anything becomes default-on
