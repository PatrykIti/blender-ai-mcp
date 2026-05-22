# 360. TASK-172 planning audit follow-on drift repair

Date: 2026-05-22

## Summary

Ran a second evidence-based audit of the `TASK-172` optional-vision runtime
family against:

- `AGENTS.md` task-spec requirements
- the current vision/reference code seams and test owners in the repo
- the already-shipped segmentation/classifier substrate work
- primary-source model documentation for GroundingDINO, OWL-ViT / OWLv2, and
  SAM 2 terminology

The repair pass fixed the remaining planning drift by:

- anchoring the umbrella explicitly to the shipped `TASK-128-03`
  part-segmentation seam and `TASK-164` reference-classifier seam instead of
  treating those substrates as implicit context
- adding the real guided/status projection owners
  (`reference_feedback.py`, `router.py`) to the umbrella and
  `TASK-172-01` / `TASK-172-02` touchpoint and proof lanes, so optional
  capability diagnostics stay aligned across RU refresh, compact feedback, and
  `router_get_status(...)`
- tightening `TASK-172-02` around the existing feedback/status carriers and
  making its dependency on `TASK-172-01` explicit
- splitting the previously oversized `TASK-172-03` localization slice into:
  - `TASK-172-03-01` for runtime/config/provider boundary work
  - `TASK-172-03-02` for compare-time projection and transport work
- tightening downstream sequencing so:
  - `TASK-172-04` depends on the activation-policy leaf
  - `TASK-172-05` waits for the compare-time localization projection leaf
  - `TASK-172-06` waits for the concrete compare-time localization and
    segmentation leaves instead of the broader umbrella wording
- updating the promoted `TASK-172` board note so the visible board state
  matches the repaired hierarchy and execution order

## Validation

- docs/task drift hygiene:
  - `git diff --check`
  - result: passed
- targeted planning-consistency audit:
  - `rg -n "TASK-172|TASK-128-03|TASK-164|TASK-172-03-01|TASK-172-03-02|Depends On|reference_feedback|router_get_status" _docs/_TASKS/README.md _docs/_TASKS/TASK-172*.md _docs/_CHANGELOG/360-2026-05-22-task-172-planning-audit-follow-on-drift-repair.md`
  - result: passed
- board-stat verification:
  - `awk 'BEGIN{section=""} /^## /{section=$0} /^\| \[TASK-/{if(section ~ /To Do/) todo++; else if(section ~ /In Progress/) prog++; else if(section ~ /Done/) done++; else if(section ~ /Superseded/) sup++} END{print "todo=" todo " in_progress=" prog " done=" done " superseded=" sup}' _docs/_TASKS/README.md`
  - result: `todo=4 in_progress=3 done=102 superseded=162`
