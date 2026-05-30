# 377. TASK-174 roster-format E2E regression fix

Date: 2026-05-30

## Summary

Reverted the flat image-roster line to its lean baseline format (`- role: label`)
after the full Blender E2E suite caught a reproducible regression: the roster
unification from changelog 368 changed the roster the local MLX models see, and
two live-model regression tests degraded (the 2B model exceeded its noise budget,
and the 4B model returned a reference description instead of a comparison
summary). The high-value change — interleaving the richer identity caption
directly before each image in the external request payload — is unaffected and
preserved.

## Changes

- `server/adapters/mcp/vision/prompting.py`: `format_image_roster_line` now
  returns `- {role}: {label}` again. `format_image_caption` (the bracketed
  `[image: ... | role=... | view=...]` identity string) is unchanged and is still
  interleaved before each image in the external backend payload
  (`backends.py _build_request_payload`). The roster and the interleaved caption
  are intentionally decoupled because small local (MLX) models are sensitive to
  the more verbose roster wording.

## Validation

- The two failing live-model E2E tests
  (`tests/e2e/vision/test_real_view_variant_model_comparison.py` and
  `tests/e2e/vision/test_reference_guided_creature_comparison.py`) failed
  consistently with the bracketed roster and both PASS again after the revert.
- Unit prompting/backend tests updated to assert the lean roster while keeping the
  external interleaved-caption parity assertions; full `tests/unit` green.

## Note

This supersedes the "roster and interleaved captions share one format" detail of
changelog 368 / TASK-174-02; the interleaved-caption grounding (the primary
TASK-174 benefit) is retained. Lesson recorded: prompt-shape changes that reach
local models must be validated against the live-model E2E lane, not just unit
tests.
