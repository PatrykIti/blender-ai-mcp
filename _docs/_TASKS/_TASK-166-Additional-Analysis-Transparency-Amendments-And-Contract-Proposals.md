# TASK-166 Transparency Amendments And Contract Proposals

**Type:** Analysis / Amendment proposal for [TASK-166](./TASK-166_Hierarchical_Reference_Compare_Perceived_Evidence_And_Budget_Control.md)
**Review State:** Archived after merge into the canonical `TASK-166*` family on 2026-05-08
**Audience:** task-writing agent + maintainers of `_docs/_TASKS/TASK-166*`
**Goal:** Tighten TASK-166 so vision-module feedback becomes transparent **on the public contract**, not only inside the engine.

## Review Outcome

- The canonical implementation/planning target is now the `TASK-166*` family,
  not this standalone note.
- Accepted merge points:
  - additive packet provenance/conflict visibility on the existing staged
    compare / iterate contracts
  - explicit extraction/ranking pass status and skip/failure semantics
  - additive per-run budget diagnostics
  - packet transparency feeding the existing compact
    `reference_orchestrator_feedback` owner seam
- Adjusted during merge:
  - authority wording in the canonical task docs stays aligned with the repo's
    existing boundary and gate vocabulary instead of introducing a second
    competing authority taxonomy as the canonical enum source
  - `compare_diagnostics` extends rather than duplicates
    `silhouette_analysis`, `part_segmentation`, `planner_detail`, and
    `budget_control`
- Rejected as-is:
  - any path that bypasses the existing staged compare contracts or creates a
    second planner/evidence flow for clients

The remaining sections below are preserved as historical proposal text for
review context. Where they differ from the merged `TASK-166*` docs, the task
family is canonical.

Do not implement the following from the historical draft below:

- the superseded alternative authority taxonomy from the early draft
- the superseded attach-time trigger story that normalized strategy on a
  different post-attach seam
- the older compare-time owner assumption that concentrated packet CV / sidecar
  execution primarily in `vision/reference_support.py`
- the idea that new packet evidence should supersede existing staged candidate
  vocabulary such as `source_signals`, `vision_evidence`, or `truth_evidence`

---

## Archived Problem Summary

The original draft correctly identified three broad concerns before the merge:

- packeted compare would need additive public transparency, not only cleaner
  internal execution
- packet provenance/conflict reporting should become an explicit contract
  concern instead of staying as implementation folklore
- the compare flow needed a clearer runtime trigger map so attach-time RU
  support and compare-time packet support were not blurred together

The detailed contract sketches that previously followed here were removed after
merge because they preserved superseded vocabulary, owner mappings, and
surfacing rules that no longer match the canonical `TASK-166*` family.

Use the merged task docs for all current implementation guidance:

- [TASK-166](./TASK-166_Hierarchical_Reference_Compare_Perceived_Evidence_And_Budget_Control.md)
- [TASK-166-03](./TASK-166-03_Deterministic_CV_And_Optional_PyTorch_Perceiver_Sidecars.md)
- [TASK-166-06](./TASK-166-06_Public_Contract_Transparency_For_Hierarchical_Compare.md)
