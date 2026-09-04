# TASK-122-02-02: `macro_align_part_with_contact`

**Parent:** [TASK-122-02](./TASK-122-02_Creature_Correction_Macro_Tool_Wave.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** Added `macro_align_part_with_contact` as a bounded repair macro for already-related pairs. The first MVP reads pair truth through `gap` / `alignment` / `overlap` / `assert_contact`, infers a repair axis when possible, preserves the current side by default, enforces `max_nudge`, and surfaces the macro as a recommended candidate from `truth_followup` without auto-applying it in the loop.

## Objective

Add a bounded repair macro for already-related parts that almost fit, but still
have small gap/contact/alignment errors that should be corrected with a
minimal nudge instead of a fresh placement from scratch.

## Business Problem

The repo now has two useful bounded placement macros:

- `macro_relative_layout` for general relative bbox placement
- `macro_attach_part_to_surface` for initial seating of one part onto a target
  surface/body

But that still leaves a practical correction gap:

- a part is already in roughly the right place
- the model has visible progress worth preserving
- truth tools say it still floats, drifts, or misaligns
- a full re-placement is too blunt and risks disturbing the existing pose,
  contact side, or nearby proportions

This is common on assembled creature-style work:

- an ear is already on the correct side of the head, but still floats a little
- a horn touches the skull, but drifts tangentially after later edits
- a limb is nearly grounded, but needs one small repair nudge instead of a full
  re-seat

## Business Outcome

If this task is done correctly, the repo gains:

- one bounded repair tool for "almost correct" part relationships
- smaller, safer corrective moves than full re-placement macros
- better preservation of the existing contact side, pose, and nearby progress
- a cleaner `truth -> action -> verify` loop for assembled-part correction

## Scope

This task should add a repair-oriented macro that:

1. reads the current pair state through truth tools
2. infers the most likely normal axis / side / tangential drift
3. applies one bounded minimal nudge toward contact or the requested gap
4. returns before/after truth summary plus deterministic verification hints

The first release should stay bounded:

- bbox / axis-aligned repair only
- pairwise only, not multi-part global optimization
- exposed as a recommended option from truth-followup / loop guidance
- not auto-applied by the loop by default

This task should **not** become:

- a third generic placement alias
- unconstrained mesh snapping
- free-form "fix the relationship however you want" behavior
- automatic loop execution without explicit later gating work

## Repository Touchpoints

- `server/domain/tools/`
- `server/application/tool_handlers/`
- `blender_addon/application/handlers/`
- `blender_addon/__init__.py`
- `server/adapters/mcp/areas/`
- `server/adapters/mcp/dispatcher.py`
- `server/infrastructure/di.py`
- `server/router/infrastructure/tools_metadata/`
- `tests/unit/`
- `tests/e2e/`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_ADDON/README.md`

## Acceptance Criteria

- the macro can repair an already-related pair using a minimal bounded nudge
  rather than full re-placement
- the macro can target `contact` or an explicit small gap while preserving the
  current side when that side is clear
- the macro returns before/after truth summary, bounded movement details, and
  deterministic verification hints
- the tool is ready to be surfaced as a recommended macro candidate from
  truth-followup or later loop policy, but is not auto-applied by default

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_ROUTER/README.md` when router-aware metadata or guided usage changes

## Tests To Add/Update

- `tests/unit/` for contract and handler coverage
- `tests/e2e/` when geometry, alignment, contact, or cleanup behavior changes in Blender

## Changelog Impact

- add a `_docs/_CHANGELOG/*.md` entry when this leaf changes macro behavior, contracts, metadata, or public docs

## Status / Board Update

- this leaf is closed; the parent macro wave remains in progress for the remaining creature-correction macros

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-122-02-02-01](./TASK-122-02-02-01_Repair_Macro_Contract_Inference_And_Candidate_Exposure.md) | Define the technical MVP for truth-driven minimal-nudge repair and how it plugs into the existing correction flow |
