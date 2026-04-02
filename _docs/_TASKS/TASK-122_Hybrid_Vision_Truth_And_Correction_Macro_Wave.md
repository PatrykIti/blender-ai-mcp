# TASK-122: Hybrid Vision, Truth, and Correction Macro Wave

**Priority:** 🔴 High  
**Category:** Product Reliability / Assembled-Model Correction  
**Estimated Effort:** Large  
**Dependencies:** TASK-117, TASK-120, TASK-121, TASK-121-08  
**Status:** 🚧 In Progress

**Progress Update:** The truth-contract subtree (`TASK-122-01`) and the creature-correction macro subtree (`TASK-122-02`) are now complete, and the first two hybrid-loop leaves (`TASK-122-03-01` and `TASK-122-03-02`) are also done. Stage compare and iterate responses now expose structured assembled-target truth handoff plus ranked `correction_candidates`, and the iterate loop now derives its loop-facing `correction_focus` from those ranked candidates when available. The umbrella remains in progress while the remaining hybrid-loop leaves wire that integration into final disposition policy and eval.

## Objective

Extend the current reference-guided vision loop into a practical correction
system for assembled multi-part models such as creatures, where visible
comparison alone is not enough.

The target is a hybrid loop:

1. vision interprets silhouette/proportion/reference mismatch
2. truth tools verify actual contact/gap/alignment/overlap state
3. bounded macro tools apply the most useful corrective edits
4. loop disposition becomes driven by both visual and geometric evidence

## Business Problem

The current system is good at:

- silhouette mismatch
- proportion drift
- reference-guided next-step hints

But it is still weak at:

- proving that parts actually touch
- detecting when parts float or intersect in 3D
- converting those findings into stable bounded corrective actions

That is why creature-style builds can still reach a limit:

- vision can say "the ear looks wrong"
- truth tools can say "there is a gap"
- but the system still lacks an integrated correction layer that can act on
  those facts cleanly and repeatedly

## Business Outcome

If this wave is done correctly, the repo gains:

- correction loops that combine image-based interpretation with geometric truth
- better reliability on assembled multi-part models
- fewer false "looks fine" states when parts are floating or intersecting
- bounded correction macros that turn mismatch findings into practical edits
- a more credible path from "AI notices the issue" to "AI fixes the issue"

## Scope

This umbrella covers:

- truth/spatial correction bundles for assembled parts
- macro tools for attachment, contact repair, symmetry pairing, supported-pair placement, proportion repair, ordered segment-chain shaping, and intersection cleanup
- a hybrid loop contract that merges vision and truth signals
- real assembled-creature evaluation and prompting guidance

This umbrella does **not** make vision the truth source.
It also does **not** introduce free-form unconstrained "fix everything" mega tools.

## Acceptance Criteria

- the repo can detect both visible mismatch and actual spatial failure
- the loop can recommend or apply bounded corrective actions for assembled parts
- multi-part creature-style models are materially easier to correct than with vision-only guidance
- the resulting system remains bounded, deterministic where possible, and consistent with the existing truth-layer boundary

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/`
- `server/adapters/mcp/vision/`
- `server/application/tool_handlers/`
- `server/domain/tools/`
- `blender_addon/application/handlers/`
- `tests/unit/`
- `tests/e2e/`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`
- `_docs/_ADDON/README.md`

## Completion Update Requirements

- every completed descendant under `TASK-122` must add a new `_docs/_CHANGELOG/*` entry and update `_docs/_CHANGELOG/README.md`
- update the relevant `_docs/` area docs for the touched truth, macro, or loop behavior
- add or update focused unit coverage, and add/update E2E coverage when Blender/runtime behavior changes
- keep `_docs/_TASKS/README.md` and the relevant task statuses aligned when promoted board state changes

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-122-01](./TASK-122-01_Spatial_Correction_Truth_Bundles_For_Assembled_Models.md) | Turn measure/assert tools into correction-oriented truth bundles for assembled parts |
| 2 | [TASK-122-02](./TASK-122-02_Creature_Correction_Macro_Tool_Wave.md) | Add bounded macro tools for the most common assembled-creature corrections |
| 3 | [TASK-122-03](./TASK-122-03_Hybrid_Vision_Truth_Correction_Loop.md) | Merge vision, truth, and macro outputs into one practical correction loop |
