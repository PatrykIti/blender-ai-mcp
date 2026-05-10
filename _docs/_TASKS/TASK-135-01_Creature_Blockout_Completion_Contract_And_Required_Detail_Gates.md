# TASK-135-01: Creature Blockout Completion Contract And Required Detail Gates

**Status:** ✅ Done
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
| `server/adapters/mcp/contracts/reference.py` | Reuse the existing checkpoint gate-summary and completion-blocker fields for creature-specific blocker semantics |
| `server/adapters/mcp/contracts/quality_gates.py` | Reuse generic gate status and blocker contracts from `TASK-157` |
| `server/adapters/mcp/areas/reference.py` | Refuse final completion when required creature gates are missing/failed/stale on the staged checkpoint surface |
| `server/adapters/mcp/areas/reference_feedback.py` | Keep `reference_orchestrator_feedback` aligned with the same blocker, next-action, and loop-disposition semantics exposed to clients |
| `server/adapters/mcp/areas/reference_truth.py` | Keep required creature seams and completion blockers aligned with staged truth/follow-up payloads |
| `server/adapters/mcp/transforms/quality_gate_verifier.py` | Enforce verifier-owned completion and seam pass/fail semantics |
| `server/adapters/mcp/session_capabilities.py` | Keep the public session-capability facade stable while creature gate state routes through the split modules below |
| `server/adapters/mcp/session_capabilities_flow.py` | Keep the existing creature guided-role vocabulary and pair cardinality aligned when gate-only detail blockers reference the same semantic body parts |
| `server/adapters/mcp/session_capabilities_registry.py` | Keep part-registration and flow-advance behavior aligned with any creature gate summary that depends on the current guided role model |
| `server/adapters/mcp/session_capabilities_state.py` | Persist creature required visual roles, role counts, and stale gate versions |
| `server/adapters/mcp/session_capabilities_runtime_glue.py` | Project updated gate status and stale marking back into session state and visibility |
| `server/application/services/spatial_graph.py` | Map required creature seams to attachment/support gate evidence |
| `server/adapters/mcp/discovery/search_surface.py` | Bias missing-detail and seam blockers toward bounded repair/build tools on the live search surface |
| `server/router/infrastructure/tools_metadata/` | Add creature completion and visual-detail search hints |
| `tests/unit/adapters/mcp/` | Add contract, checkpoint, visibility, guided state, and gate-verifier tests, especially `test_quality_gate_verifier.py` for completion-blocking seam behavior |
| `tests/unit/tools/scene/` | Add only upstream spatial-graph or macro-evidence coverage when relation evidence generation itself changes |
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
- Keep the live owner split explicit:
  - existing creature guided-flow cardinality stays owned by
    `server/adapters/mcp/session_capabilities_flow.py` and
    `server/adapters/mcp/session_capabilities_registry.py`
  - `eye_pair` remains gate-only in this slice unless a separate follow-on
    explicitly promotes it into the guided role vocabulary
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

## Runtime / Security Contract Notes

- Visibility level: extend the existing public staged reference/checkpoint
  surfaces and current public repair/build tools; do not add a creature-only
  completion surface.
- Read-only vs mutating behavior: checkpoint payload fields, gate blockers, and
  completion summaries are read-only server/session-state outputs. Existing
  modeling, mesh, scene, and macro repairs remain the only mutating Blender
  paths and must mark attachment or final-completion evidence stale after a
  scene change.
- Mode and selection impact: attach or cleanup repairs that clear completion
  blockers must preserve or explicitly restore expected object/edit mode and
  active selection through the current guided runtime helpers.
- Session and auth assumptions: creature completion blockers stay scoped to the
  active stdio or Streamable HTTP session, with local Blender RPC as the only
  trusted mutating backend.
- Parameter validation and compatibility: gate blockers, required-role labels,
  and any new checkpoint fields use strict typed contracts with reject-unknown
  behavior. Any compatibility shim for older payloads must stay explicit in the
  owning contract layer.
- Side effects, recovery, and logging: keep gate pass/fail authority on the
  existing `TASK-157` verifier path. `reference_understanding_summary` stays
  support-only. `reference_orchestrator_feedback` remains a client-facing read
  model that must stay aligned with blocker, planner-family, next-action, and
  `loop_disposition` semantics, but it still cannot mark gates passed by itself.
  If evidence is stale or a seam still floats, fail closed to blockers or
  `inspect_validate` instead of prose completion, and keep provider keys or
  local paths out of logs.

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

- `README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_PROMPTS/MANUAL_TOOLS_NO_ROUTER.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_VISION/README.md`
- relevant `_docs/_VISION/*` creature and refinement docs enforced by
  `test_public_surface_docs.py` when completion or blocker wording changes
- `_docs/_CHANGELOG/README.md`
- `_docs/_TESTS/README.md`

## Changelog Impact

- Add a `_docs/_CHANGELOG/*` entry when this completion gate ships.

## Validation Commands

- `git diff --check`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_verifier.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
- `poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_goal_derived_gate_creature_completion.py tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py -q`
- `Outside sandbox before closeout: PYTHONPATH=. poetry run pytest ./tests/unit`
- `Outside sandbox for Blender-backed runtime proof: poetry run python scripts/run_e2e_tests.py`

## Status / Board Update

- `TASK-135-01` is closed as the first direct child under `TASK-135`.
- The parent `TASK-135` remains open for the curved tail / appendage build path
  and the later low-poly refinement stage.
- `_docs/_TASKS/README.md` board wording did not change because the promoted
  umbrella row remains open.

## Completion Summary

- 2026-05-10: Creature domain gate templates now require the visual roles that
  define a minimally acceptable quadruped blockout: body, head, tail, snout,
  ears, eyes, forelegs, and hindlegs.
- `eye_pair` remains gate-only in this slice; existing guided flow role
  vocabulary still owns ears and limb pairs.
- Staged checkpoint truth now materializes required creature seams into
  `reference_checkpoint` gate proposals, so `floating_gap` on required seams
  blocks final completion on the same `active_gate_plan` / top-level gate
  summary surface as other `TASK-157` gates.
- Prompt, MCP, vision, tool-summary, test, and changelog docs now describe the
  stricter creature completion contract.

## Validation Results

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_quality_gate_intake.py -q`
  - passed, `13 passed`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py::test_reference_compare_stage_checkpoint_materializes_creature_completion_gates_from_truth tests/unit/adapters/mcp/test_reference_images.py::test_reference_compare_stage_checkpoint_projects_gate_state_from_checkpoint_truth_without_prior_relation_call -q`
  - passed, `2 passed`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
  - passed, `117 passed`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_public_surface_docs.py -q`
  - passed, `12 passed`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_search_surface.py -q`
  - passed, `77 passed`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
  - passed, `10 passed`
- `poetry run ruff check server/adapters/mcp/contracts/quality_gates.py server/adapters/mcp/areas/reference.py tests/unit/adapters/mcp/test_quality_gate_intake.py tests/unit/adapters/mcp/test_quality_gate_verifier.py tests/unit/adapters/mcp/test_reference_images.py tests/e2e/vision/test_goal_derived_gate_creature_completion.py`
  - passed
- `PYTHONPATH=. poetry run pytest ./tests/unit`
  - passed outside sandbox, `3313 passed`
- `PYTEST_ADDOPTS='-k creature_gate_repair_macro_clears_tail_seam_blocker' poetry run python scripts/run_e2e_tests.py --skip-build`
  - passed outside sandbox, `1 passed, 470 deselected`
- `poetry run python -u scripts/run_e2e_tests.py`
  - passed outside sandbox, `468 passed, 3 skipped`
- `git diff --check`
  - passed

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
