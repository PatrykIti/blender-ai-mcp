# TASK-158: Vision And Creature Gate Boundary Doc Alignment

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Category:** Documentation / Vision Boundary Alignment
**Estimated Effort:** Medium
**Follow-on After:** [TASK-157](./TASK-157_Goal_Derived_Quality_Gates_And_Deterministic_Verification.md)
**Related:** [TASK-135](./TASK-135_Anatomy_Aware_Reference_Guided_Low_Poly_Creature_Reconstruction.md), [TASK-135-03](./TASK-135-03_Low_Poly_Form_Refinement_Mesh_Window_And_Profile_Macros.md), [TASK-140](./TASK-140_Expand_External_Vision_Contract_Profiles_Across_Qwen_Anthropic_OpenAI_And_NVIDIA.md)

## Objective

Align the remaining Vision/reference-understanding and creature-reconstruction
planning docs with the `TASK-157` boundary:

- Vision and perception may propose gates, relation findings, strategy hints,
  and bounded support/provenance evidence.
- Scene, spatial, mesh, assertion, and quality-gate verifier outputs own
  deterministic pass/fail truth.
- `TASK-140` provider/profile evidence remains model-capability and provenance
  evidence, not quality-gate verifier evidence.
- Draft tool and planner names from the long-form Vision plan must not read as
  current canonical families, public MCP tools, or shipped router surfaces.

This is a docs-only alignment task. It should not change runtime code,
metadata, tool exposure, or tests beyond documentation validation commands.

## Business Problem

`TASK-157` now states the correct generic quality-gate contract, but older
Vision and creature planning docs still contain historical wording that can
mislead implementers:

- the long-form Vision plan uses draft names such as `reference_understand(...)`
  and `router_apply_reference_strategy(...)` as if they were planned public
  runtime surfaces
- the same plan lists `mesh_edit`, `material_finish`, `mesh_shade_flat`, and
  `macro_low_poly_*` in places that read like current canonical vocabulary
- `TASK-135` still says `reference evidence` can decide whether a gate passed
- `TASK-135` Vision Mode wording can read as if perception defines true
  attachment or cleanup errors instead of proposing relation findings for the
  verifier
- `TASK-135-03` still uses `reference evidence requires them` for
  shape-profile child gates, which should now point to normalized gate evidence
  and verifier-backed support

Leaving these drifts in place raises the chance that a future implementation
will add a second router strategy flow, treat perception as truth, or introduce
noncanonical tool families before the existing seams are extended.

## Business Outcome

After this task, the Vision and creature planning docs should give one
consistent implementation story:

- `TASK-157` is the generic gate/verifier substrate
- `TASK-135` and `TASK-135-03` are domain consumers of that substrate
- `TASK-140` extends model-family capability and support/provenance evidence
  without becoming a quality-gate verifier
- the long-form Vision plan is clearly marked as historical strategy material
  where it still uses pre-contract names
- future implementers know which names are aliases or candidates and which
  seams are current implementation targets

## Non-Goals

This task deliberately does not:

- implement `TASK-157`, `TASK-135`, `TASK-135-03`, or `TASK-140`
- add public MCP tools such as `reference_understand` or
  `router_apply_reference_strategy`
- add canonical families named `mesh_edit`, `material_finish`,
  `mesh_shade_flat`, or `macro_low_poly_*`
- ship SAM, CLIP/SigLIP, Grounding DINO, or other heavy perception adapters
- rewrite the full long-form Vision plan from scratch
- change root `CHANGELOG.md`

## Drift Inventory

| Area | Current Drift | Required Alignment |
|------|---------------|--------------------|
| `_docs/blender-ai-mcp-vision-reference-understanding-plan.md` | `reference_understand(...)` and `router_apply_reference_strategy(...)` read as planned public/runtime surfaces | Mark as historical/draft strategy names or rewrite to current reference/guided-state seams; no public router strategy tool |
| `_docs/blender-ai-mcp-vision-reference-understanding-plan.md` | `server/adapters/mcp/router/...` appears as a planned location | Replace or annotate as obsolete path sketch; current router/guided/reference owners must be named from live repo seams |
| `_docs/blender-ai-mcp-vision-reference-understanding-plan.md` | `mesh_edit`, `material_finish`, `mesh_shade_flat`, and `macro_low_poly_*` appear in allowed vocab/task examples | Map `mesh_edit` to current `modeling_mesh`, model `material_finish` as a stage/action hint or future family, and keep low-poly macro names explicitly future/noncanonical until shipped |
| `TASK-135` | `scene/spatial/mesh/reference evidence` decides whether a gate passed | Replace with scene/spatial/mesh/assertion/verifier truth; reference/perception may seed proposals or bounded support only |
| `TASK-135` | Vision Mode defines true attachment and cleanup errors | Vision may propose relation findings; verifier/spatial/assertion policy decides true errors and pass/fail |
| `TASK-135-03` | `reference evidence requires them` for `shape_profile` child gates | Use normalized gate evidence and verifier-backed support refs; perception remains advisory |
| `TASK-140` boundary references | Provider/profile support could be confused with quality-gate evidence if cross-linked loosely | Keep TASK-140 evidence scoped to provider capability, routing/provenance, and bounded support, not final gate verification |

## Repository Touchpoints

| Path / Module | Expected Ownership | Why It Is In Scope |
|---------------|--------------------|--------------------|
| `_docs/blender-ai-mcp-vision-reference-understanding-plan.md` | Historical strategy doc cleanup | Remove or annotate stale public-tool, router-path, and noncanonical family wording |
| `_docs/_TASKS/TASK-135_Anatomy_Aware_Reference_Guided_Low_Poly_Creature_Reconstruction.md` | Domain consumer contract | Make creature reconstruction consume `TASK-157` verifier truth without granting perception pass/fail authority |
| `_docs/_TASKS/TASK-135-03_Low_Poly_Form_Refinement_Mesh_Window_And_Profile_Macros.md` | Mesh refinement consumer contract | Make shape-profile/refinement gates rely on normalized verifier-backed evidence |
| `_docs/_TASKS/TASK-140*.md` | Evidence boundary audit only | Confirm provider/profile evidence stays separate from quality-gate verifier evidence; patch wording only if drift exists |
| `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md` | Cross-link only if needed | Add a pointer only if the long-form plan cleanup needs a normative bridge |
| `_docs/_TASKS/README.md` | Board | Track this follow-on as a promoted docs-alignment task |
| `_docs/_CHANGELOG/` | Historical tracking | Record the task creation and later completion when the docs are aligned |

## Implementation Notes

- Keep this as a documentation repair pass. Do not invent new runtime APIs to
  make the old plan true.
- In the long-form Vision plan, prefer a short upfront note plus local
  annotations near stale examples instead of deleting useful historical
  analysis wholesale.
- When stale names are kept for continuity, label them explicitly:
  - historical sketch
  - strategy alias
  - future optional family
  - not a current public MCP tool
  - not a current canonical planner family
- Update `TASK-135` language so the creature domain supplies templates,
  relation semantics, defaults, and target policy, while `TASK-157` verifier
  state owns completion truth.
- Update `TASK-135` Vision Mode so relation labels and mismatch descriptions
  are advisory findings until verifier/spatial/assertion policy binds them to a
  gate status.
- Update `TASK-135-03` so refinement gates cite normalized gate evidence,
  `evidence_refs`, and verifier-supported perception support instead of
  free-standing reference evidence.
- If `TASK-140` wording is touched, keep the distinction explicit:
  provider/profile evidence can explain model capability, routing choice,
  confidence, and support provenance; it does not replace quality-gate verifier
  evidence.

## Rewrite Pattern

Use this pattern when converting older wording:

```text
Before:
reference evidence decides whether the gate passed

After:
scene/spatial/mesh/assertion verifier evidence decides whether the gate passed;
reference and perception outputs may seed proposals or attach bounded support
refs when the verifier strategy accepts them.
```

```text
Before:
router_apply_reference_strategy(...) chooses the build path

After:
existing reference/guided-state seams normalize the strategy into current
guided flow state and visibility/search hints; no public router strategy tool
is introduced by this docs cleanup.
```

```text
Before:
allowed families include mesh_edit and material_finish

After:
`mesh_edit` is a strategy alias for current `modeling_mesh`; `material_finish`
is a stage/action hint or future family until implemented and documented as a
canonical surface.
```

## Tests / Validation

This is a docs-only task. Validation should prove that the repaired docs no
longer contradict the `TASK-157` boundary.

| Layer | Validation |
|-------|------------|
| Whitespace / markdown patch hygiene | `git diff --check` |
| Public-tool drift | `rg -n "reference_understand|router_apply_reference_strategy|server/adapters/mcp/router" _docs/blender-ai-mcp-vision-reference-understanding-plan.md` and manually classify every remaining hit as historical/draft or rewrite it |
| Noncanonical family drift | `rg -n "mesh_edit|material_finish|mesh_shade_flat|macro_low_poly" _docs/blender-ai-mcp-vision-reference-understanding-plan.md _docs/_TASKS/TASK-135*.md _docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md` and verify no hit presents the name as a current canonical family/tool |
| Truth-boundary drift | `rg -n "reference evidence|true attachment errors|true cleanup/intersection errors|decides whether the gate passed|quality-gate verifier evidence" _docs/_TASKS/TASK-135*.md _docs/_TASKS/TASK-140*.md _docs/blender-ai-mcp-vision-reference-understanding-plan.md` and verify authority remains with scene/spatial/mesh/assertion/verifier evidence |
| Board / changelog | Confirm `_docs/_TASKS/README.md` and `_docs/_CHANGELOG/README.md` stay in sync with added or completed task docs |

## Docs To Update

- `_docs/blender-ai-mcp-vision-reference-understanding-plan.md`
- `_docs/_TASKS/TASK-135_Anatomy_Aware_Reference_Guided_Low_Poly_Creature_Reconstruction.md`
- `_docs/_TASKS/TASK-135-03_Low_Poly_Form_Refinement_Mesh_Window_And_Profile_Macros.md`
- `_docs/_TASKS/TASK-140*.md` only if the audit finds concrete wording drift
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md` only if a cross-link or
  normative note is needed
- `_docs/_TASKS/README.md`
- `_docs/_CHANGELOG/`

## Changelog Impact

- Add a changelog entry when this task is created.
- Refresh or add a new changelog entry when the alignment pass is completed,
  including the validation grep results.

## Acceptance Criteria

- The long-form Vision plan no longer reads as if `reference_understand(...)`
  or `router_apply_reference_strategy(...)` are current public MCP/runtime
  surfaces.
- The long-form Vision plan no longer presents `mesh_edit`,
  `material_finish`, `mesh_shade_flat`, or `macro_low_poly_*` as current
  canonical families/tools.
- `TASK-135` and `TASK-135-03` state that Vision/perception/reference evidence
  is advisory/proposal/support context unless a server-owned verifier maps it
  into bounded evidence refs.
- Scene/spatial/mesh/assertion/verifier evidence remains the only authority for
  gate pass/fail and final completion.
- `TASK-140` provider/profile evidence remains separate from quality-gate
  verifier evidence.
- `_docs/_TASKS/README.md` tracks this task as a board-level follow-on.
- Validation commands from this task are run and recorded in the completion
  summary.
