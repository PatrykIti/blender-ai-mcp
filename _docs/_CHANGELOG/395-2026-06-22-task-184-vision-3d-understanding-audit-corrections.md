# 395. TASK-184 Vision 3D understanding audit corrections

Date: 2026-06-22

Closed the TASK-184 audit follow-up family.

## Changed

- Added explicit `visual_mark_overlays_supported` model capability gating for
  Set-of-Mark overlays and lean mark-free schemas when no usable marks exist.
- Switched live mark placement to projection-first anchors with explicit
  fallback/skip metadata.
- Added additive `direction_world` relation-graph metadata for world-frame
  axis/sign/margin direction facts.
- Hardened Object Index / `pass_index` contracts around object-level
  visible-surface evidence, grayscale-band decoding, quantization risk,
  fragmentation, and Cryptomatte deferral.
- Added `encoding=near_bright_far_dark` to relative-depth auxiliary captions.
- Added the default-off `--emit-reliability-scorecard` vision harness flag for
  per-axis advisory evaluation telemetry.

## Validation

- Focused TASK-184 unit lanes passed.
- `ruff check` passed on touched Python files.
- `mypy` passed on the touched vision capability/model metadata files.
- Final full unit/E2E/pre-commit validation is recorded in the TASK-184
  closeout notes.
