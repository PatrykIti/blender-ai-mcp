# TASK-157-03-01: Gate-Driven Visibility, Search, And Recovery Policy

**Status:** ✅ Done
**Priority:** 🔴 High
**Parent:** [TASK-157-03](./TASK-157-03_Guided_Flow_Gate_Runtime_Integration.md)
**Category:** Guided Runtime / Visibility Policy
**Estimated Effort:** Medium

## Objective

Make unresolved gates open the narrow bounded tool surface needed for the next
repair, without encouraging the LLM to reset goals, guess hidden tools, or use
the broad catalog, and without forcing a full spatial refresh loop after every
safe mutation inside one still-open build stage.

## Completion Summary

Completed on 2026-05-01.

- Extended the existing guided visibility policy with optional
  session-scoped `gate_plan` input instead of creating a new catalog or
  discovery flow.
- Active `attachment_seam` and `support_contact` blockers expose only bounded
  relation/measure/assert and macro repair tools.
- `shape_profile`, proportion, refinement, and opening gates wait behind
  unresolved required seam/support blockers before exposing refinement tools.
- `search_tools(...)` now recognizes active gate recovery queries and returns
  bounded verifier/repair tools for blocker resolution instead of recommending
  `router_set_goal` as a reset path.
- Static build-step visibility still respects existing guided cadence:
  spatial refresh gates remain bounded to spatial-context tools, and gate tools
  are added as a narrow overlay.
- `symmetry_pair` blockers now reuse that same overlay to expose
  `scene_relation_graph`, `scene_assert_symmetry`, and
  `macro_place_symmetry_pair` without widening the catalog.
- Evidence-sensitive narrowing from future `reference_understanding`,
  segmentation, or classification payloads remains follow-on work under
  `TASK-158` and downstream domain consumers; the shipped slice stops at
  blocker-driven overlays and gate-recovery search shortcuts.

## Validation

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_search_surface.py::test_failed_attachment_gate_search_surfaces_bounded_repair_tools tests/unit/adapters/mcp/test_search_surface.py::test_active_gate_recovery_search_does_not_recommend_goal_reset tests/unit/adapters/mcp/test_visibility_policy.py::test_gate_blocker_visibility_exposes_bounded_attachment_repair_tools tests/unit/adapters/mcp/test_visibility_policy.py::test_shape_profile_gate_waits_behind_unresolved_seam_gate -v`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_quality_gate_contracts.py tests/unit/adapters/mcp/test_quality_gate_verifier.py tests/unit/adapters/mcp/test_quality_gate_intake.py -v`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --files README.md _docs/AVAILABLE_TOOLS_SUMMARY.md _docs/_CHANGELOG/README.md _docs/_CHANGELOG/281-2026-05-01-task-157-gate-driven-visibility-search.md _docs/_MCP_SERVER/README.md _docs/_PROMPTS/README.md _docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md _docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md _docs/_TASKS/README.md _docs/_TASKS/TASK-157-03-01_Gate_Driven_Visibility_Search_And_Recovery_Policy.md _docs/_TASKS/TASK-157-03_Guided_Flow_Gate_Runtime_Integration.md _docs/_TASKS/TASK-157_Goal_Derived_Quality_Gates_And_Deterministic_Verification.md _docs/_TESTS/README.md server/adapters/mcp/discovery/search_surface.py server/adapters/mcp/guided_mode.py server/adapters/mcp/session_capabilities.py server/adapters/mcp/transforms/visibility_policy.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_visibility_policy.py`

## Repository Touchpoints

| Path / Module | Expected Change |
|---------------|-----------------|
| `server/adapters/mcp/transforms/visibility_policy.py` | Gate-to-tool-family visibility rules |
| `server/adapters/mcp/discovery/search_surface.py` | Gate-aware search and call-path diagnostics |
| `server/adapters/mcp/discovery/search_documents.py` | Gate-oriented search documents |
| `server/adapters/mcp/session_capabilities.py` | Stale-but-continuable versus refresh-required state transitions |
| `server/router/infrastructure/tools_metadata/` | Gate-oriented search hints using existing `keywords`, `sample_prompts`, `related_tools`, and `patterns`; introduce a new `gate_families` field only with schema/loader/search tests |
| `tests/unit/adapters/mcp/test_search_surface.py` | Search/tool exposure tests |
| `tests/unit/adapters/mcp/test_visibility_policy.py` | Gate-driven visibility tests |
| `tests/unit/adapters/mcp/test_guided_flow_state_contract.py` | Spatial refresh cadence state tests |

## Technical Requirements

- `attachment_seam` gates expose:
  - `scene_relation_graph`
  - `macro_attach_part_to_surface`
  - `macro_align_part_with_contact`
- `support_contact` gates expose current support/contact verification and
  repair tools:
  - `scene_relation_graph`
  - `scene_measure_gap`
  - `scene_assert_contact`
  - `macro_place_supported_pair`
  - `macro_attach_part_to_surface` or `macro_align_part_with_contact` when the
    support failure is also a seating/contact repair
- `shape_profile` gates expose mesh/modeling refinement tools only after
  required seam/contact gates are not failed.
- `reference_understanding` and CLIP-style classification evidence may select
  a domain profile, construction strategy, or candidate gate family, but must
  not expose broad tools by themselves.
- Optional `part_segmentation` evidence may narrow a target region for an
  already active gate, but cannot bypass the gate's verifier prerequisites.
- Recovery guidance should say "verify or repair active gate" instead of
  "reset router goal".
- `router_set_goal` must not be recommended as a deadlock escape when active
  unresolved gates exist.
- A mutating tool may mark spatial state stale without hiding the remaining
  tools for the current allowed role batch.
- Visibility should narrow to spatial/verification tools only when stale facts
  are about to be consumed by:
  - a stage transition
  - a gate transition
  - a pair-dependent seam/support repair
  - final completion
- Search and recovery messages must distinguish:
  - "continue current batch, refresh at checkpoint"
  - from "refresh now before this gate can advance".

## Runtime / Security Contract Notes

- Visibility level: this slice changes guided visibility/search policy only; it
  must not create a parallel catalog, discovery endpoint, or public
  `router_apply_reference_strategy` style handoff.
- Read-only vs mutating behavior: visibility and search are read-only policy
  outputs. Repair tools remain mutating only when the client explicitly calls
  existing macro/modeling/mesh tools.
- Family vocabulary: use current `GuidedFlowFamilyLiteral` values for guided
  visibility (`spatial_context`, `reference_context`, `primary_masses`,
  `secondary_parts`, `attachment_alignment`, `checkpoint_iterate`,
  `inspect_validate`, `finish`, `utility`). Planner-facing `modeling_mesh` remains a
  `ReferencePlannerFamilyLiteral` and must be translated to concrete
  mesh/modeling tool names or current guided families before visibility rules
  are materialized.
- Transport assumptions: Streamable HTTP and stdio must receive the same
  gate-driven tool names for the same session state; do not rely on detached
  refresh writes after a tool response has returned.
- Provider/evidence boundary: `reference_understanding`, segmentation, and
  classification evidence can narrow or prioritize policy, but cannot unlock
  broad tools or mark gates passed by themselves.
- Metadata compatibility: the first slice should use current router metadata
  fields (`keywords`, `sample_prompts`, `related_tools`, and `patterns`) for
  gate-oriented search hints. If a dedicated `gate_families` field is added,
  update `_schema.json`, `ToolMetadata`, metadata loader, search document
  generation, and alignment tests in the same implementation slice.

## Spatial Refresh Cadence Rules

The guided surface should steer the LLM toward checkpoint-based evidence, not
mutation-by-mutation thrashing.

Recommended cadence for creature-style work:

1. Create the current stage's allowed roles as a batch.
2. Run the spatial triad with explicit scope.
3. Run the reference/vision checkpoint for that stage.
4. Repair only the failed gates or pair seams.
5. Re-check the repaired local pair or the broader stage scope, depending on
   what the next gate consumes.

Example creature stage policy:

| Stage | Continue Without Full Refresh | Require Refresh Before |
|-------|-------------------------------|------------------------|
| Primary masses | Creating/scaling `Body`, `Head`, `Tail` while they remain in the same primary-mass gate | Advancing to seam repair or secondary details |
| Seam repair | Running the selected attachment macro for `Head -> Body` or `Tail -> Body` | Leaving the repair gate or using the seam verdict as passed evidence |
| Secondary details | Creating `Snout`, ears, eyes, and legs in the same allowed role batch | Advancing to refinement or final review |
| Refinement | Bounded mesh/profile edits inside the active profile gate | Final completion |

Visibility policy should therefore use the combination of:

- `current_step`
- active unresolved gate
- stale gate versions
- whether the next action consumes spatial truth

instead of keying only on `spatial_state_stale`.

## Pseudocode

```python
def visibility_for_gate(gate):
    match gate.gate_type:
        case "attachment_seam":
            return {"spatial_context", "attachment_alignment", "inspect_validate"}
        case "support_contact":
            return {
                "spatial_context",
                "secondary_parts",
                "attachment_alignment",
                "inspect_validate",
            }
        case "shape_profile" if prerequisites_passed(gate):
            return {"secondary_parts", "inspect_validate"}
        case "opening_or_cut":
            return {"secondary_parts", "inspect_validate"}
        case _:
            return {"reference_context", "inspect_validate"}


def should_require_spatial_refresh(state, next_action_name, active_gate):
    if next_action_name in {"advance_gate", "complete_stage", "final_completion"}:
        return state.spatial_state_stale
    if active_gate.requires_pair_truth and next_action_name in {
        "verify_active_pair_gate",
        "repair_active_pair_gate",
    }:
        return pair_gate_is_stale(state, active_gate.target_pair)
    return False


def refine_visibility_from_evidence(gate, evidence_refs, visible_families):
    if has_reference_understanding_only(evidence_refs):
        return visible_families | {"reference_context"}
    if has_part_segmentation_target(gate, evidence_refs):
        return narrow_to_gate_target(visible_families, gate.target_region)
    if has_classification_scores_only(evidence_refs):
        return visible_families
    return visible_families
```

## Tests To Add/Update

- Active seam gate makes attachment macros visible.
- Active shape-profile gate does not expose mesh tools while seam gates fail.
- Safe same-stage mutations keep current role-batch tools visible even when
  `spatial_state_stale=true`.
- Gate/stage transitions with stale spatial evidence expose refresh/checkpoint
  tools and hide unrelated broad mutation tools.
- Pair-dependent next actions expose local pair verification/repair tools.
- Search for "fix floating tail gap" returns seam repair tools.
- Search for "continue current stage" or equivalent recovery guidance does not
  recommend the full spatial triad when the current batch can continue safely.
- Search for "reset goal" does not become the recommended recovery for active
  gate blockers.
- Reference-understanding-only evidence does not expose broad sculpt or broad
  catalog tools.
- Segmentation-derived target hints narrow an already active gate target
  without marking the gate passed.

## E2E Tests

- Blender-backed guided visibility/regression proof remains owned by
  [TASK-157-04](./TASK-157-04_Cross_Domain_E2E_Gate_Regression_Harness.md).
- This closed slice keeps unit/runtime-policy proof on the existing visibility,
  search, and guided-iterate surfaces.

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`

## Changelog Impact

- Add a `_docs/_CHANGELOG/*` entry when gate-driven visibility/search behavior
  ships or when public guided visibility semantics materially change.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py -v`
- The grep below is a drift sentinel. Hits for `mesh_edit`,
  `material_finish`, `mesh_shade_flat`, or `macro_low_poly_*` must remain
  non-canonical aliases/future proposals unless a dedicated contract adds them.
- `rg -n -P "macro_attachment|macro_profile|macro_cutout(?!_recess)|inspect_assert|mesh_edit|material_finish|mesh_shade_flat|macro_low_poly" _docs/_TASKS/TASK-157*.md _docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md server/adapters/mcp server/router/infrastructure/tools_metadata`

## Acceptance Criteria

- Gate blockers drive small, relevant visibility changes.
- Clients receive recovery guidance tied to gate verification/repair.
- Broad catalog exposure is not required to resolve common gate failures.
- Spatial refresh is cadence-aware: stale state does not automatically become a
  hard block until the next action needs fresh spatial evidence.
