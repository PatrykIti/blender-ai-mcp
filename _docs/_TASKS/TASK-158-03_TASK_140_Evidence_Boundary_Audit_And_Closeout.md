# TASK-158-03: TASK-140 Evidence Boundary Audit And TASK-158 Closeout

**Status:** ✅ Done
**Priority:** 🔴 High
**Parent:** [TASK-158](./TASK-158_Vision_And_Creature_Gate_Boundary_Doc_Alignment.md)
**Category:** Guided Runtime / Evidence Boundary Closeout
**Estimated Effort:** Small

## Objective

Use existing `TASK-140` and roadmap wording as canonical anchors for
provider/profile evidence separation, patch only contradictory `TASK-140*`
wording if found, and close both `TASK-158` scopes with board/changelog,
runtime validation, and docs validation state in sync.

## Repository Touchpoints

| Path / Module | Expected Change |
|---------------|-----------------|
| `_docs/_TASKS/TASK-140_Expand_External_Vision_Contract_Profiles_Across_Qwen_Anthropic_OpenAI_And_NVIDIA.md` | Canonical anchor; patch only contradictory wording outside the existing boundary note |
| `_docs/_TASKS/TASK-140-05-03_Evidence_Taxonomy_Promotion_Criteria_And_Operator_Reporting.md` | Canonical anchor for support evidence reporting |
| `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md` | Canonical anchor for advisory perception and verifier-owned truth |
| `_docs/_TASKS/TASK-158_Vision_And_Creature_Gate_Boundary_Doc_Alignment.md` | Completion summary and status update |
| `_docs/_TASKS/TASK-158-04_Reference_Understanding_Internal_Contract_And_Guided_Handoff.md` | Implementation closeout for bounded reference-understanding handoff |
| `_docs/_TASKS/TASK-158-05_Optional_Perception_Adapter_Readiness_And_Eval_Harness.md` | Implementation closeout for default-off optional perception readiness |
| `_docs/_TASKS/README.md` | Board status/count update |
| `_docs/_CHANGELOG/` | Completion changelog update |

## Canonical No-Op Anchors

Do not rewrite these unless a later audit proves they contradict the boundary.
Use the phrase anchors below instead of brittle line snapshots.

| File / Anchor | Why It Is Canonical |
|---------------|---------------------|
| `_docs/_TASKS/TASK-140_Expand_External_Vision_Contract_Profiles_Across_Qwen_Anthropic_OpenAI_And_NVIDIA.md` phrase `It is not quality-gate verifier evidence by itself.` | States provider/profile evidence is not quality-gate verifier evidence by itself |
| `_docs/_TASKS/TASK-140-05-03_Evidence_Taxonomy_Promotion_Criteria_And_Operator_Reporting.md` phrase `vision_contract_profile can produce structured compare/iterate payloads` | Frames evidence taxonomy as provider/profile reporting |
| `_docs/_TASKS/TASK-140-05-03_Evidence_Taxonomy_Promotion_Criteria_And_Operator_Reporting.md` phrase `must remain distinct from deterministic quality-gate verifier evidence` | Keeps promoted support evidence separate from quality-gate verifier evidence |
| `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md` phrase `vision_contract_profile remains prompt/schema/parser routing metadata` | States provider/profile diagnostics remain routing metadata, not verifier truth |
| `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md` phrase `the first reference-understanding public surface remains undecided` | Forbids treating draft reference-understanding surfaces as already-promoted public tools |
| `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md` alias/future-tool mapping around `translate draft families into current GuidedFlowFamilyLiteral values` | Defines canonical alias/future-tool mapping for `mesh_edit`, `material_finish`, and low-poly macro names |
| `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md` optional later adapter section around `CLIP/SigLIP`, `SAM`, and `GroundingDINO/OWL-ViT` | Keeps heavy perception adapters optional and later |
| `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md` owner-map section around `current contract and owner map` / `server/router/` owners | Routes implementation through current reference/guided-state seams and real owners, not a non-existent MCP router package |

## Implementation Notes

- Run the `TASK-158` validation grep after `TASK-158-01` and `TASK-158-02`.
- Run the focused runtime/unit validation from `TASK-158-04` and `TASK-158-05`
  after implementation slices complete.
- Classify remaining `TASK-140*` hits as canonical/no-op or contradictory.
- Patch only contradictory wording that blurs provider/profile evidence with
  quality-gate verifier evidence.
- If the audit concludes that `TASK-140*` stays untouched, record that explicit
  no-op outcome in this leaf and in the `TASK-158` parent completion summary
  instead of silently skipping the check.
- Close all `TASK-158-*` child files in the same branch when the parent closes,
  or mark any intentionally skipped child as superseded with reason.
- Update `_docs/_TASKS/README.md` counts and row placement when closing the
  promoted task.
- Do not close `TASK-158` until this leaf, the parent, and any still-referenced
  child docs all agree on status and follow-on handling.

## Runtime / Security Contract Notes

- This closeout must not change provider routing, `vision_contract_profile`
  values, MCP metadata, guided visibility, or runtime verifier code by itself.
  Runtime changes belong in `TASK-158-04` or `TASK-158-05` before closeout.
- Stdio and Streamable HTTP behavior must remain unchanged.
- No provider call, sidecar activation, model download, or new evidence
  collection is part of this task.
- Documentation examples must not include raw provider payloads, keys, local
  private paths, or unredacted debug transcripts.
- `TASK-140` provider/profile evidence remains support/provenance evidence; it
  must not become quality-gate pass/fail truth.

## Tests / Validation

- `git diff --check`
- `rg -n "quality-gate verifier evidence|provider/profile support evidence|vision_contract_profile" _docs/_TASKS/TASK-140*.md _docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
  - classify every hit as canonical/no-op or patch contradiction
- `rg -n "reference_understand|router_apply_reference_strategy|server/adapters/mcp/router|mesh_edit|material_finish|mesh_shade_flat|macro_low_poly|macro_create_part|SAM|CLIP|SigLIP|GroundingDINO|OWL-ViT|scene/spatial/mesh/reference evidence|true attachment errors|true cleanup/intersection errors|reference evidence requires" _docs/blender-ai-mcp-vision-reference-understanding-plan.md _docs/_TASKS/TASK-135*.md _docs/_TASKS/TASK-140*.md _docs/_TASKS/TASK-157*.md _docs/_TASKS/TASK-158*.md _docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
  - expected result after completion: no unclassified drift
- Confirm `_docs/_TASKS/README.md`, `_docs/_CHANGELOG/README.md`, and the
  completion changelog entry are synchronized.
- Confirm `TASK-158-04` and `TASK-158-05` focused validations are recorded
  before parent close. If either implementation slice is deferred, do not close
  `TASK-158` unless the deferred scope is converted into a standalone
  board-level follow-on marked `Follow-on After`, the parent acceptance
  criteria name that follow-on, and `_docs/_TASKS/README.md` tracks it as open.

## Docs To Update

- `_docs/_TASKS/TASK-158_Vision_And_Creature_Gate_Boundary_Doc_Alignment.md`
- `_docs/_TASKS/TASK-158-01_Long_Form_Vision_Plan_Surface_And_Alias_Cleanup.md`
- `_docs/_TASKS/TASK-158-02_Creature_Gate_Truth_Boundary_Alignment.md`
- `_docs/_TASKS/TASK-158-03_TASK_140_Evidence_Boundary_Audit_And_Closeout.md`
- `_docs/_TASKS/TASK-158-04_Reference_Understanding_Internal_Contract_And_Guided_Handoff.md`
- `_docs/_TASKS/TASK-158-05_Optional_Perception_Adapter_Readiness_And_Eval_Harness.md`
- `_docs/_TASKS/README.md`
- `_docs/_CHANGELOG/`

## Changelog Impact

- Add a new `_docs/_CHANGELOG/<next-number>-...task-158-...completion.md` entry
  with the final grep results, implementation summary, and focused validation
  commands.
- Refresh `_docs/_CHANGELOG/README.md`.
- Leave changelog 278 as the creation/plan entry.

## Status / Board Update

- Closeout is same-branch work: update this leaf, the `TASK-158` parent,
  any direct child statuses, `_docs/_TASKS/README.md`, and the completion
  changelog together.
- Do not leave a direct `TASK-158` child open under a closed parent. If
  `TASK-158-04` or `TASK-158-05` is deferred, create a standalone
  `Follow-on After` task, close or supersede the stale child docs
  administratively with an explicit reason, and keep the board tracking the
  follow-on instead of the closed parent.
- If the `TASK-140*` audit remains a pure no-op, say that explicitly in this
  leaf's completion summary so the canonical anchors remain an intentional
  closeout result.

## Acceptance Criteria

- `TASK-140` evidence remains clearly provider/profile support evidence.
- No `TASK-140*` wording tells implementers to use provider/profile confidence
  as quality-gate pass/fail truth.
- `TASK-158-04` and `TASK-158-05` are implemented before the parent closes; if
  either slice is deferred, the deferred scope is converted into a standalone
  board-level follow-on marked `Follow-on After`, the parent acceptance
  criteria name that follow-on, and `_docs/_TASKS/README.md` tracks it as open.
- `TASK-158` closeout records whether `TASK-140*` stayed canonical no-op or
  required a wording patch; it does not leave the audit result implicit.
- `TASK-158` parent, children, board, and changelog are synchronized at close.

## Completion Summary

- completed on 2026-05-03 after confirming that the `TASK-140*` boundary
  anchors remain a canonical no-op for this wave: no wording patch was needed
  in `TASK-140` or `TASK-140-05-03`
- closed the remaining `TASK-158` umbrella work by synchronizing:
  - `TASK-158` parent status
  - `TASK-158-01` / `TASK-158-02` / `TASK-158-04` / `TASK-158-05`
  - `_docs/_TASKS/README.md`
  - `_docs/_CHANGELOG/README.md`
  - the final `TASK-158` completion changelog entry
- final drift classification is explicit:
  - `TASK-140*` hits are canonical provider/profile evidence anchors
  - long-form plan hits for `reference_understand(...)`,
    `router_apply_reference_strategy(...)`, `mesh_edit`,
    `material_finish`, `mesh_shade_flat`, `macro_low_poly_*`,
    `macro_create_part`, `SAM`, `CLIP`, `SigLIP`, `GroundingDINO`, and
    `OWL-ViT` remain in historical sketch / future-optional sections only
  - `TASK-135*` no longer contain the targeted truth-boundary drift phrases
- runtime validation for the implemented Scope B slices was already recorded in
  the `TASK-158-04*`, `TASK-158-05`, and changelog closeout entries; this leaf
  adds the final board/docs audit on top of those runtime proofs
- validated with:
  `git diff --check`
  and
  `rg -n "quality-gate verifier evidence|provider/profile support evidence|vision_contract_profile" _docs/_TASKS/TASK-140*.md _docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
  and
  `rg -n "reference_understand|router_apply_reference_strategy|server/adapters/mcp/router|mesh_edit|material_finish|mesh_shade_flat|macro_low_poly|macro_create_part|SAM|CLIP|SigLIP|GroundingDINO|OWL-ViT|scene/spatial/mesh/reference evidence|true attachment errors|true cleanup/intersection errors|reference evidence requires" _docs/blender-ai-mcp-vision-reference-understanding-plan.md _docs/_TASKS/TASK-135*.md _docs/_TASKS/TASK-140*.md _docs/_TASKS/TASK-157*.md _docs/_TASKS/TASK-158*.md _docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
