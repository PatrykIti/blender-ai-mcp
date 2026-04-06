# TASK-142: Creature Part Seating and Organic Attachment Semantics

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Category:** Product Reliability / Organic Part Placement
**Follow-on After:** [TASK-128](./TASK-128_Reference_Guided_Creature_Build_Surface_And_Perception_Reliability.md)

## Objective

Improve the guided creature correction path so attached organic parts are
repaired toward believable seating/contact instead of only removing overlap and
leaving visible gaps.

## Business Problem

The first real squirrel run after `TASK-128` showed that the current bounded
macro/correction path is still too overlap-centric for creature parts that are
supposed to emerge from or sit on another organic form.

Observed failure shapes:

- ears touch the head and visually grow out of it, but the system still treats
  that as generic overlap cleanup instead of an attachment/base-seating problem
- eyes end up floating with a measurable gap after `macro_cleanup_part_intersections`
- snout and nose are pushed off the head/body with a measurable gap even though
  they should remain seated/attached
- the current operator/reporting story can call these outcomes “success” after
  overlap goes to zero, even when the resulting attachment semantics are
  visibly wrong for creature work

This is not the same as the `TASK-141` prompt/schema problem. Even with a
perfect caller, the current bounded correction semantics still optimize the
wrong geometric outcome for several creature-part relationships.

## Scope

This follow-on covers:

- clarifying which creature-part relations are:
  - overlap cleanup only
  - attachment/seating/contact repair
- improving bounded repair guidance for:
  - `Ear_* -> Head`
  - `Eye_* -> Head`
  - `Snout -> Head`
  - `Nose -> Snout` or `Nose -> Head` depending on intended low-poly topology
- tightening success criteria so “overlap removed” is not enough when the
  intended result is seated contact
- aligning `truth_followup`, `correction_candidates`, and macro selection with
  those semantics
- adding regression coverage around organic attachment instead of only generic
  disjoint/overlap resolution

This follow-on does **not** cover:

- prompt/client schema drift under [TASK-141](./TASK-141_Guided_Creature_Run_Contract_And_Schema_Drift_Hardening.md)
- anatomy-aware creature reconstruction under [TASK-135](./TASK-135_Anatomy_Aware_Reference_Guided_Low_Poly_Creature_Reconstruction.md)
- general hard-surface contact semantics already covered by earlier truth-layer
  work

## Acceptance Criteria

- the repo distinguishes “remove overlap” from “seat/attach this organic part”
  on the creature-guided path
- eyes, snout, and similar attached creature parts no longer default to a
  correction path that leaves a visible measurable gap and still reports
  success
- `truth_followup` / `correction_candidates` can communicate that attachment
  semantics are still wrong even when raw overlap is zero
- bounded next-step guidance favors the right repair family for organic seating
  cases instead of reusing generic overlap cleanup by default
- focused regressions protect the concrete squirrel-style failure shapes seen in
  the first real post-`TASK-128` run

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/contracts/scene.py`
- `server/adapters/mcp/vision/reporting.py`
- `server/router/infrastructure/tools_metadata/scene/`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/tools/macro/test_macro_cleanup_part_intersections.py`
- `tests/e2e/vision/test_reference_stage_silhouette_contract.py`
- `_docs/_VISION/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_TASKS/README.md`

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/tools/macro/test_macro_cleanup_part_intersections.py`
- `tests/e2e/vision/test_reference_stage_silhouette_contract.py`

## Changelog Impact

- add a dedicated `_docs/_CHANGELOG/*` entry when this follow-on ships

## Status / Board Update

- promote this as a board-level follow-on from the first real `TASK-128`
  squirrel run
- keep it separate from `TASK-141` because this is geometric/semantic repair
  behavior, not prompt/schema drift
