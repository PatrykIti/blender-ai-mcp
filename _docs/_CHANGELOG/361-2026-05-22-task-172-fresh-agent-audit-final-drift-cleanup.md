# 361. TASK-172 fresh-agent audit final drift cleanup

Date: 2026-05-22

## Summary

Ran one more clean-room drift audit for `TASK-172` using fresh agent sessions
plus a local re-check after `5cfab902`.

That extra pass found and repaired the remaining issues:

- marked `_docs/Vision-extension-proposal.md` as historical background instead
  of a live planning source, because its old `TASK-171A` monolith and public
  `vision_capability_registry(...)` framing is superseded by `TASK-172`
- normalized `TASK-172-04` wording from informal `SAM2` references to the
  official `SAM 2` naming
- repaired `TASK-172-03-01` so its touchpoints and validation lane match the
  current `generic_sidecar` optional-provider seam (`vision/runtime.py`,
  `vision/reference_support.py`, `reference_compare_packets.py`,
  `test_reference_images.py`, `test_reference_compare_packets.py`) instead of
  incorrectly pointing at the main VLM backend factory tests

## Validation

- docs/task drift hygiene:
  - `git diff --check`
  - result: passed
- focused residual-drift grep:
  - `rg -n "Historical note|superseded|vision_capability_registry|SAM 2|SAM2|SAM-vs-SAM|generic_sidecar|test_reference_images.py|test_reference_compare_packets.py" _docs/Vision-extension-proposal.md _docs/_TASKS/TASK-172-03-01_Localization_Runtime_Config_And_Provider_Boundary.md _docs/_TASKS/TASK-172-04_SAM_Or_SAM2_Local_Mask_And_Landmark_Support.md`
  - result: passed
