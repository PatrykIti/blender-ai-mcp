# TASK-158-03: TASK-140 Evidence Boundary Audit And Closeout

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-158](./TASK-158_Vision_And_Creature_Gate_Boundary_Doc_Alignment.md)
**Category:** Documentation / Evidence Boundary Closeout
**Estimated Effort:** Small

## Objective

Use existing `TASK-140` and roadmap wording as canonical anchors for
provider/profile evidence separation, patch only contradictory `TASK-140*`
wording if found, and close `TASK-158` with board/changelog/validation state in
sync.

## Repository Touchpoints

| Path / Module | Expected Change |
|---------------|-----------------|
| `_docs/_TASKS/TASK-140_Expand_External_Vision_Contract_Profiles_Across_Qwen_Anthropic_OpenAI_And_NVIDIA.md` | Canonical anchor; patch only contradictory wording outside the existing boundary note |
| `_docs/_TASKS/TASK-140-05-03_Evidence_Taxonomy_Promotion_Criteria_And_Operator_Reporting.md` | Canonical anchor for support evidence reporting |
| `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md` | Canonical anchor for advisory perception and verifier-owned truth |
| `_docs/_TASKS/TASK-158_Vision_And_Creature_Gate_Boundary_Doc_Alignment.md` | Completion summary and status update |
| `_docs/_TASKS/README.md` | Board status/count update |
| `_docs/_CHANGELOG/` | Completion changelog update |

## Canonical No-Op Anchors

Do not rewrite these unless a later audit proves they contradict the boundary:

| File / Range | Why It Is Canonical |
|--------------|---------------------|
| `_docs/_TASKS/TASK-140_Expand_External_Vision_Contract_Profiles_Across_Qwen_Anthropic_OpenAI_And_NVIDIA.md:66-72` | States provider/profile evidence is not quality-gate verifier evidence by itself |
| `_docs/_TASKS/TASK-140-05-03_Evidence_Taxonomy_Promotion_Criteria_And_Operator_Reporting.md:14-18` | Frames evidence taxonomy as provider/profile reporting |
| `_docs/_TASKS/TASK-140-05-03_Evidence_Taxonomy_Promotion_Criteria_And_Operator_Reporting.md:30-32` | Keeps promoted support evidence separate from quality-gate verifier evidence |
| `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md:73-76` | States perception can support/propose but not own verifier truth |
| `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md:100-108` | Leaves the first reference-understanding public surface undecided and forbids a public `router_apply_reference_strategy` tool |
| `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md:176-188` | Defines alias/future-tool mapping for `mesh_edit`, `material_finish`, and low-poly macro names |
| `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md:273-277` | Keeps low-poly macro names out of first implementation |
| `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md:290-296` | Routes implementation through current reference/guided-state seams or real `server/router/` owners, not a non-existent MCP router package |
| `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md:348-355` | Leaves public-surface and `material_finish` canonical-family promotion decisions open for later review |

## Implementation Notes

- Run the `TASK-158` validation grep after `TASK-158-01` and `TASK-158-02`.
- Classify remaining `TASK-140*` hits as canonical/no-op or contradictory.
- Patch only contradictory wording that blurs provider/profile evidence with
  quality-gate verifier evidence.
- Close all `TASK-158-*` child files in the same branch when the parent closes,
  or mark any intentionally skipped child as superseded with reason.
- Update `_docs/_TASKS/README.md` counts and row placement when closing the
  promoted task.

## Runtime / Security Contract Notes

- This is a docs-only closeout/audit. It must not change provider routing,
  `vision_contract_profile` values, MCP metadata, guided visibility, or runtime
  verifier code.
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
- `rg -n "reference_understand|router_apply_reference_strategy|server/adapters/mcp/router|mesh_edit|material_finish|mesh_shade_flat|macro_low_poly|scene/spatial/mesh/reference evidence|true attachment errors|true cleanup/intersection errors|reference evidence requires" _docs/blender-ai-mcp-vision-reference-understanding-plan.md _docs/_TASKS/TASK-135*.md _docs/_TASKS/TASK-140*.md _docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
  - expected result after completion: no unclassified drift
- Confirm `_docs/_TASKS/README.md`, `_docs/_CHANGELOG/README.md`, and the
  completion changelog entry are synchronized.

## Docs To Update

- `_docs/_TASKS/TASK-158_Vision_And_Creature_Gate_Boundary_Doc_Alignment.md`
- `_docs/_TASKS/TASK-158-01_Long_Form_Vision_Plan_Surface_And_Alias_Cleanup.md`
- `_docs/_TASKS/TASK-158-02_Creature_Gate_Truth_Boundary_Alignment.md`
- `_docs/_TASKS/TASK-158-03_TASK_140_Evidence_Boundary_Audit_And_Closeout.md`
- `_docs/_TASKS/README.md`
- `_docs/_CHANGELOG/`

## Changelog Impact

- Add a new `_docs/_CHANGELOG/279-...task-158-...completion.md` entry with the
  final grep results.
- Refresh `_docs/_CHANGELOG/README.md`.
- Leave changelog 278 as the creation/plan entry.

## Acceptance Criteria

- `TASK-140` evidence remains clearly provider/profile support evidence.
- No `TASK-140*` wording tells implementers to use provider/profile confidence
  as quality-gate pass/fail truth.
- `TASK-158` parent, children, board, and changelog are synchronized at close.
