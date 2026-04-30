# 278. TASK-158 vision and creature boundary alignment plan

Date: 2026-05-01
Version: -

## Summary

- added `TASK-158` as a docs-only follow-on after `TASK-157` to align the
  remaining Vision/reference-understanding and creature-reconstruction planning
  docs with the gate/verifier boundary
- captured the remaining out-of-scope drift from the `TASK-157` audit:
  draft public-surface names in the long-form Vision plan, noncanonical
  `mesh_edit`/`material_finish`/`mesh_shade_flat`/`macro_low_poly_*` wording,
  and `TASK-135` wording that could grant reference/perception evidence
  pass/fail authority
- updated the task board so `TASK-158` is tracked as a promoted follow-on in
  the Vision & Hybrid Loop lane and linked from the strategic Vision roadmap
  owner list
- defined validation grep commands for public-tool drift, noncanonical family
  drift, and truth-boundary drift
- expanded `TASK-158` into three executable child slices with line-level repair
  inventory, canonical no-op anchors, live contract source-of-truth notes, and
  board/changelog closeout rules

## Validation

- `git diff --check`
  - result on this machine for the task-creation and task-expansion docs
    patch: passed
- `rg -n "TASK-158|TASK-158-01|TASK-158-02|TASK-158-03|Vision And Creature Gate Boundary|vision and creature boundary" _docs/_TASKS/README.md _docs/_CHANGELOG/README.md _docs/_CHANGELOG/278-2026-05-01-task-158-vision-creature-boundary-alignment-plan.md _docs/_TASKS/TASK-158*.md`
  - result on this machine: passed; task, child slices, board, and changelog
    index are linked
- targeted grep for `reference_understand`,
  `router_apply_reference_strategy`, `server/adapters/mcp/router`,
  `mesh_edit`, `material_finish`, `mesh_shade_flat`, `macro_low_poly`,
  `reference evidence`, and true-error wording
  - result on this machine: captured in `TASK-158` as the required future
    implementation validation
