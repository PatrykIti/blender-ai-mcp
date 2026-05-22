# 359. TASK-172 optional vision runtime planning drift repair

Date: 2026-05-22

## Summary

Repaired planning drift in the `TASK-172` optional-vision runtime family so the
task hierarchy matches current repo seams, `AGENTS.md` task-spec rules, and the
repo's vision-planning docs for SAM-family segmentation versus later
GroundingDINO / OWL-ViT / OWLv2 grounding.

The repair pass:

- added the missing umbrella relationship section that clarifies `TASK-140-06`
  as the capability-aware substrate owner and `TASK-163` / `TASK-166` /
  `TASK-171` as the reused consumer lanes
- rewrote the umbrella objective, outcome, non-goals, execution structure,
  test matrix, and acceptance criteria so packet-local SAM-family masks/crops
  come before later text-conditioned localization seeding
- clarified that first-wave heavy grounding is compare/iterate-only, while RU
  refresh may only merge already-available optional support artifacts on the
  current seams
- reasserted `reference_compare_packets.py` as the durable compare-time owner
  for localized packet support while keeping `vision/reference_support.py`
  scoped to RU-only optional support merging unless shared helpers are
  extracted explicitly first
- narrowed `TASK-172-03` from "localization as segmentation" to internal
  localization candidates plus support-safe public projection, and aligned the
  model wording with GroundingDINO / OWL-ViT / OWLv2 terminology
- renamed `TASK-172-04` around packet-local SAM-family masks/crops plus derived
  anchors instead of implying SAM-native landmark output
- reframed `TASK-172-05` as a post-integration shared-reuse decision for the
  first in-process adapter family instead of a hidden prerequisite platform
  slice
- retargeted `TASK-172-06` away from unrelated transport/benchmark lanes and
  documented that `scripts/vision_harness.py` must first be expanded into an
  explicit staged-compare/localized-support harness role, or replaced with a
  dedicated compare-harness helper, before it can own that validation surface
- fixed the board-level `Superseded` count drift and refreshed the promoted
  `TASK-172` row summary to match the repaired sequencing

## Validation

- docs/task drift hygiene:
  - `git diff --check`
  - result: passed
- targeted planning-consistency audit:
  - `rg -n "TASK-172|GroundingDINO|OWL-ViT|OWLv2|SAM|SAM2|TTL|unload|localized perception|prerequisite diagnostics" _docs/_TASKS/README.md _docs/_TASKS/TASK-172*.md`
  - result: passed
- board-stat verification:
  - `awk 'BEGIN{section=\"\"} /^## /{section=$0} /^\\| \\[TASK-/{if(section ~ /To Do/) todo++; else if(section ~ /In Progress/) prog++; else if(section ~ /Done/) done++; else if(section ~ /Superseded/) sup++} END{print \"todo=\" todo \" in_progress=\" prog \" done=\" done \" superseded=\" sup}' _docs/_TASKS/README.md`
  - result: `todo=4 in_progress=3 done=102 superseded=162`
