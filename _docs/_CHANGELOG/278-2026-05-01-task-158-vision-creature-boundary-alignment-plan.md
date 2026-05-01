# 278. TASK-158 reference understanding follow-up and boundary alignment plan

Date: 2026-05-01
Version: -

## Summary

- added `TASK-158` as a two-scope follow-up to the open `TASK-157` substrate:
  Scope A aligns the remaining Vision/reference-understanding and
  creature-reconstruction planning docs with the gate/verifier boundary, and
  Scope B implements bounded reference-understanding plus default-off optional
  perception readiness after `TASK-157`
- captured the remaining out-of-scope drift from the `TASK-157` audit:
  draft public-surface names in the long-form Vision plan, noncanonical
  `mesh_edit`/`material_finish`/`mesh_shade_flat`/`macro_low_poly_*` wording,
  and `TASK-135` wording that could grant reference/perception evidence
  pass/fail authority
- updated the task board so `TASK-158` is tracked as a promoted
  reference-understanding follow-up in the Vision & Hybrid Loop lane and linked
  from the strategic Vision roadmap owner list
- defined validation grep commands for public-tool drift, noncanonical family
  drift, and truth-boundary drift
- expanded `TASK-158` into documentation and implementation child slices with
  line-level repair inventory, canonical no-op anchors, live contract
  source-of-truth notes, post-`TASK-157` implementation guidance, and
  board/changelog closeout rules
- refined the plan after a final multi-agent audit with the repo-level
  responsibility-boundary anchor, additional roadmap no-op anchors, eval-pack
  classification rows, corrected board statistics, and one shared completion
  changelog rule for the child slices
- added follow-up audit coverage for `macro_create_part` historical shorthand
  and SAM/CLIP/SigLIP optional-adapter clusters so they cannot be mistaken for
  current canonical tools or `TASK-158`/MVP runtime requirements
- corrected the task framing so `TASK-158` is not documentation-only: it keeps
  the docs alignment scope and adds implementation slices for bounded
  reference-understanding handoff and default-off optional perception readiness

## Validation

- `git diff --check`
  - result on this machine for the task-creation and task-expansion docs
    patch: passed
- `rg -n "TASK-158|TASK-158-01|TASK-158-02|TASK-158-03|TASK-158-04|TASK-158-05|Reference Understanding Follow-Up|Vision And Creature Gate Boundary|vision and creature boundary" _docs/_TASKS/README.md _docs/_CHANGELOG/README.md _docs/_CHANGELOG/278-2026-05-01-task-158-vision-creature-boundary-alignment-plan.md _docs/_TASKS/TASK-158*.md`
  - result on this machine: passed; task, child slices, board, and changelog
    index are linked
- targeted grep for `reference_understand`,
  `router_apply_reference_strategy`, `server/adapters/mcp/router`,
  `mesh_edit`, `material_finish`, `mesh_shade_flat`, `macro_low_poly`,
  `macro_create_part`, SAM/CLIP/SigLIP optional-adapter wording,
  `reference evidence`, and true-error wording
  - result on this machine: captured in `TASK-158` as the required future
    implementation validation
