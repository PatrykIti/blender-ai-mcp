# TASK-135-01: Creature Blockout Completion Contract And Required Detail Gates

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-135](./TASK-135_Anatomy_Aware_Reference_Guided_Low_Poly_Creature_Reconstruction.md)
**Category:** Reconstruction / Guided Creature Quality
**Estimated Effort:** Medium
**Depends On:** [TASK-157](./TASK-157_Goal_Derived_Quality_Gates_And_Deterministic_Verification.md)

## Objective

Define and enforce a stronger guided creature completion contract so a
reference-guided low-poly creature session cannot finish just because objects
exist, intersections were pushed apart, or broad silhouette roughly resembles
the target.

The first quality bar is based on the latest squirrel run evidence:

- the model had no eyes
- most creature parts were separate primitive blobs
- several parts visually floated instead of seating into the body/head
- the assistant treated a residual sphere-surface floating gap as expected
  blockout state
- "no intersections" was incorrectly reported as equivalent to assembled
  success

## Business Problem

The current guided path can complete a creature blockout that is technically
valid at the tool-call level but visibly weak:

- required body-part roles can be present while required visual details are
  absent
- `macro_cleanup_part_intersections` can improve overlap while leaving
  disconnected seams
- bbox-touching can be mistaken for organic attachment
- final summaries can rationalize `floating_gap` as acceptable even for
  required creature seams

That makes the product feel unreliable even when the server does not hang and
all tool calls return structured results.

## Repository Touchpoints

| Path / Module | Expected Change |
|---------------|-----------------|
| `server/adapters/mcp/contracts/reference.py` | Add creature completion blockers and gate summary fields to checkpoint payloads |
| `server/adapters/mcp/contracts/quality_gates.py` | Reuse generic gate status and blocker contracts from `TASK-157` |
| `server/adapters/mcp/areas/reference.py` | Refuse final completion when required creature gates are missing/failed/stale |
| `server/adapters/mcp/session_capabilities.py` | Persist creature required visual roles, role counts, and stale gate versions |
| `server/application/services/spatial_graph.py` | Map required creature seams to attachment/support gate evidence |
| `server/router/infrastructure/tools_metadata/` | Add creature completion and visual-detail search hints |
| `tests/unit/adapters/mcp/` | Add contract, checkpoint, visibility, and guided state tests |
| `tests/unit/tools/scene/` | Add seam verifier and macro evidence tests |
| `tests/e2e/vision/` | Add primitive-only squirrel completion-blocking E2E |
| `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md` | Document required visual roles and no-floating-gap completion rule |
| `_docs/_MCP_SERVER/README.md` | Document creature completion gate semantics |

## Implementation Notes

- Add a creature blockout completion gate that checks required visual roles in
  addition to the current structural roles.
- For common quadruped mammal targets, treat at least these as required or
  explicitly waived:
  - `body_core`
  - `head_mass`
  - `tail_mass`
  - `snout_mass`
  - `ear_pair`
  - `eye_pair`
  - `foreleg_pair`
  - `hindleg_pair`
- Keep role cardinality explicit for paired details such as eyes, ears,
  forelegs, and hindlegs.
- Do not allow final completion when required seams still report
  `floating_gap`, especially:
  - head/body
  - tail/body
  - limb/body
  - eye/head
  - snout/head unless the verdict is an acceptable embedded attachment
- Preserve the existing distinction that slight `intersecting` can be
  acceptable for embedded organic seams, but overlap cleanup alone is not a
  success criterion.
- Update model-facing summaries and prompt assets so they cannot phrase
  "floating gap is expected at blockout stage" as a valid final result for
  required creature seams.
- Keep the implementation generic-gate compatible:
  - required visual roles map to `required_part`
  - creature seams map to `attachment_seam` or `support_contact`
  - final blockout quality maps to `final_completion`
  - optional target-specific details may be waived only through explicit gate
    policy, not through assistant prose

## Pseudocode

```python
required_roles = role_policy.required_visual_roles(domain_profile="creature")
missing_roles = required_roles - completed_roles

if missing_roles:
    return continue_build(
        next_actions=["create_missing_detail_parts"],
        missing_roles=sorted(missing_roles),
    )

for seam in required_creature_seams:
    if seam.attachment_verdict == "floating_gap":
        return inspect_validate(
            correction_focus=[seam],
            reason="required creature seam is still detached",
        )

if only_intersection_cleanup_was_done and any_required_seam_not_seated:
    return inspect_validate(reason="overlap cleanup did not prove attachment")

return maybe_complete()
```

## Tests To Add/Update

| Layer | Tests |
|-------|-------|
| Unit contracts | Required visual roles serialize into gate blockers |
| Unit reference loop | `reference_iterate_stage_checkpoint(...)` refuses completion when `eye_pair` is missing |
| Unit seam truth | `floating_gap` on tail/body, head/body, or limb/body fails required gate |
| Unit cleanup regression | Intersection cleanup does not pass a gate without a passing attachment verdict |
| Unit visibility | Missing `eye_pair` exposes bounded primitive/detail creation path, not broad finish tools |
| E2E vision | Primitive-only squirrel without eyes and seated seams cannot pass final completion |
| E2E macro | Attach/align macro repair followed by relation re-check clears the relevant blocker |

## Docs To Update

- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TESTS/README.md`

## Changelog Impact

- Add a `_docs/_CHANGELOG/*` entry when this completion gate ships.

## Acceptance Criteria

- The guided creature loop reports missing visual roles before final completion.
- Required creature seams must be `seated_contact` or an explicitly acceptable
  embedded attachment before the blockout can be called complete.
- A low-poly squirrel-like target cannot finish without eyes unless the target
  profile explicitly waives them.
- The final response contract distinguishes "intersections cleaned" from
  "parts are attached/seated".
- Prompt and docs guidance no longer permit rationalizing required floating
  gaps as expected final blockout state.
