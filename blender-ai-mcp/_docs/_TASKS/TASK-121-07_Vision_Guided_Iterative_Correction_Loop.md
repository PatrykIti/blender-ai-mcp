# TASK-121-07: Vision-Guided Iterative Correction Loop

**Parent:** [TASK-121](./TASK-121_Goal_Aware_Vision_Assist_And_Reference_Context.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** The first bounded checkpoint comparison surfaces now exist:
`reference_compare_checkpoint(...)` compares an existing checkpoint image
against the active goal plus attached references,
`reference_compare_current_view(...)` adds a practical single-view
capture-then-compare path for staged manual work, and
`reference_compare_stage_checkpoint(...)` now adds a deterministic multi-view
stage checkpoint path using the shared `compact` / `rich` preset system. The
checkpoint result now also exposes a tighter correction-oriented output shape
via `correction_focus`, plus more bounded mismatch/correction semantics for
reference-guided compare modes. Real squirrel/reference eval coverage and
prompt guidance are now in repo as the first practical reference-driven
creature package.

---

## Objective

Move from one-shot macro-attached visual summaries toward a practical
reference-guided correction loop that can support real iterative modeling work
such as low-poly creature builds.

---

## Business Problem

The current vision layer is strong enough to:

- attach bounded visual interpretation to macro reports
- compare deterministic before/after captures
- consume goal-scoped reference images

But it still does not provide a first-class iterative correction loop during
manual or staged work.

In real usage this creates a product gap:

- the model can build a staged squirrel
- the system can capture checkpoints
- the system can attach references
- but the model still has to improvise the next correction step instead of
  receiving a clean, bounded "checkpoint vs reference" interpretation during
  the build loop

That means the repo is still closer to:

- "vision-assisted summary after a build step"

than to:

- "vision-guided iterative correction toward the reference"

---

## Product Direction

Add a bounded checkpoint-comparison path for reference-guided work.

Target behavior:

1. model completes one stage or checkpoint
2. system captures deterministic views for that checkpoint
3. vision compares checkpoint vs reference and current goal
4. output returns:
   - shape mismatches
   - proportion mismatches
   - bounded next corrections
   - deterministic follow-up checks when needed
5. model uses that output for the next correction step

This must stay:

- request-bound
- bounded
- non-truth
- non-policy

---

## Leaf Breakdown

| Leaf | Purpose |
|------|---------|
| [TASK-121-07-01](./TASK-121-07-01_Checkpoint_Comparison_Contract_And_Surface.md) | Define one bounded checkpoint-vs-reference comparison contract and how it is exposed |
| [TASK-121-07-02](./TASK-121-07-02_Manual_Stage_Checkpoint_Capture_Path.md) | Add one practical checkpoint capture path for staged/manual guided builds |
| [TASK-121-07-03](./TASK-121-07-03_Reference_Guided_Correction_Output_Model.md) | Shape/proportion/correction semantics for iterative creature/reference work |
| [TASK-121-07-04](./TASK-121-07-04_Real_Reference_Driven_Creature_Eval_And_Prompting.md) | Real squirrel/reference eval loop and prompt guidance for iterative correction |

---

## Acceptance Criteria

- the repo has one bounded vision-guided correction loop for staged work
- reference-guided manual builds can request checkpoint comparison without
  abusing ad hoc one-off viewport screenshots
- the result contract stays interpretation-only and correction-oriented
- real reference-driven modeling scenarios can be evaluated against the loop
