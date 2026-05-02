# TASK-158-01: Long-Form Vision Plan Surface And Alias Cleanup

**Status:** ✅ Done
**Priority:** 🔴 High
**Parent:** [TASK-158](./TASK-158_Vision_And_Creature_Gate_Boundary_Doc_Alignment.md)
**Category:** Documentation / Vision Plan Alignment
**Estimated Effort:** Medium

## Objective

Rewrite or annotate the long-form Vision/reference-understanding plan so draft
public surface names, obsolete router paths, and noncanonical tool/family names
cannot be mistaken for current implementation targets.

## Repository Touchpoints

| Path / Module | Expected Change |
|---------------|-----------------|
| `_docs/blender-ai-mcp-vision-reference-understanding-plan.md` | Add upfront historical/draft note and local annotations for stale examples |
| `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md` | Use as the normative bridge; update only if a cross-link is needed |
| `server/adapters/mcp/contracts/reference.py` | Live source for `ReferencePlannerFamilyLiteral`; read-only reference |
| `server/adapters/mcp/contracts/guided_flow.py` | Live source for `GuidedFlowFamilyLiteral`; read-only reference |

## Implementation Notes

- Do not delete the long-form plan wholesale. Keep useful strategy material, but
  mark stale names as historical sketches, aliases, or future candidates.
- `reference_understand(...)` and `router_apply_reference_strategy(...)` must
  not read as current public MCP tools.
- Obsolete path sketches such as `server/adapters/mcp/router/...` must be
  replaced with current owner seams or explicitly labeled historical.
- `mesh_edit` maps to current `modeling_mesh`.
- `material_finish` is a stage/action hint or future family until a dedicated
  contract promotes it.
- `mesh_shade_flat` and `macro_low_poly_*` names are future optional candidates
  until metadata, adapters, handlers, tests, and docs ship them as real tools.
- `macro_create_part` is historical shorthand. Map it to current
  `modeling_create_primitive(...)` with guided role/group auto-registration for
  new objects, or `guided_register_part(...)` for existing objects.
- SAM, CLIP/SigLIP, segmentation sidecars, Grounding DINO, and similar heavy
  perception adapters are historical/future optional sketches here. TASK-158
  must not activate sidecars, trigger downloads, call providers, or make them
  MVP dependencies.

## Runtime / Security Contract Notes

- This is a docs-only cleanup. It must not add a public MCP tool, router
  strategy endpoint, metadata field, guided visibility rule, or runtime handoff.
- Stdio and Streamable HTTP behavior must remain unchanged.
- No provider call, sidecar activation, model download, or external
  reference-understanding run is part of this task.
- Documentation examples must not include raw provider payloads, keys, local
  private paths, or unredacted debug transcripts.
- The cleanup must preserve verifier-owned gate truth: Vision and perception
  can remain advisory/proposal/support only.

## Anchor-Based Targets

Exact line numbers in the long-form plan have already drifted. Use the current
heading and grep anchors below instead of frozen ranges.

| Anchor | Required Work |
|--------|---------------|
| Top-of-file draft note and early bullets containing `reference_understand(...)`, `router_apply_reference_strategy(...)`, `mesh_edit`, `material_finish`, and `macro_create_part` | Keep the historical/draft framing explicit before the detailed plan begins |
| Section `## 5. Nowy moduł: reference_understanding` plus the first `reference_understand(...)` / `"action": "reference_understand"` example | Reframe the draft surface through current reference/guided-state seams |
| JSON arrays and `allowed` clusters containing `mesh_edit` or `material_finish` | Replace or annotate noncanonical allowed families so only current seams read as canonical |
| `macro_create_part` tool-list hits | Map historical shorthand to `modeling_create_primitive(...)` or `guided_register_part(...)` |
| `mesh_shade_flat` and `macro_low_poly_*` example clusters | Mark low-poly macro names as future candidates until shipped |
| Optional-adapter narrative around `bez SAM/CLIP jako twardej zależności w MVP`, `SAM / Segment Anything`, `CLIP / OpenCLIP`, and `SigLIP` | Keep heavy adapters explicitly optional, default-off, and out of MVP runtime scope |
| Owner-path block containing `contracts/reference_understanding.py`, `vision/reference_understanding*.py`, `server/adapters/mcp/router/reference_strategy.py`, and `server/adapters/mcp/areas/reference_understanding.py` | Replace obsolete owner-path sketches with current contract/reference/guided/router seams or mark them historical |
| Draft public-surface block `TASK 2 — Add reference_understand MCP surface` | Keep the MCP surface idea historical/draft unless a later public-tool review promotes it |
| Optional adapter task blocks `Add optional CLIP/SigLIP classifier`, `Add SAM sidecar`, and `Add GroundingDINO/OWL-ViT style part localization if needed` | Keep these as follow-on optional adapter sketches requiring their own contract/runtime task if later promoted |
| Final summary cluster around `reference_understand(...) prompt + parser`, `optional CLIP/SigLIP classifier`, and `optional SAM sidecar` | Align the summary with current seams and deferred-adapter posture |

## Rewrite Pattern

```text
Draft name `reference_understand(...)` remains historical planning shorthand.
The current implementation target is an existing reference/guided-state seam
that can carry bounded reference-understanding summaries after a public/runtime
contract review.
```

```text
`mesh_edit` is an alias for current `modeling_mesh`; `material_finish` is a
stage/action hint or future family; `mesh_shade_flat` and `macro_low_poly_*`
are future candidates until shipped as canonical tools.
```

```text
`macro_create_part` is historical shorthand. Use current
`modeling_create_primitive(...)` with guided role/group auto-registration for
new objects, or `guided_register_part(...)` for existing objects.
```

```text
SAM, CLIP/SigLIP, and segmentation sidecars are future optional adapter
sketches. They must not become TASK-158 or MVP runtime requirements.
```

## Tests / Validation

- `git diff --check`
- `rg -n "reference_understand|router_apply_reference_strategy|server/adapters/mcp/router" _docs/blender-ai-mcp-vision-reference-understanding-plan.md`
  - every remaining hit must be historical/draft or explicitly mapped to
    current seams
- `rg -n "mesh_edit|material_finish|mesh_shade_flat|macro_low_poly|macro_create_part" _docs/blender-ai-mcp-vision-reference-understanding-plan.md _docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
  - every remaining hit must be alias/future/noncanonical wording
- `rg -n "SAM|CLIP|SigLIP|GroundingDINO|OWL-ViT" _docs/blender-ai-mcp-vision-reference-understanding-plan.md _docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
  - every remaining hit must be future optional, default-off, or out of MVP
    scope

## Docs To Update

- `_docs/blender-ai-mcp-vision-reference-understanding-plan.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md` only if a cross-link is
  needed

## Changelog Impact

- If this leaf closes independently, add a scoped `_docs/_CHANGELOG/*` entry in
  the same branch and update `_docs/_CHANGELOG/README.md`.
- If multiple `TASK-158` leaves land together in one wave, one shared
  completion entry may cover them, but it must name this leaf explicitly and
  record its validation in the summary.
- Changelog 278 remains the creation/plan entry.

## Status / Board Update

- This leaf stays under `TASK-158`; do not create a separate board row in
  `_docs/_TASKS/README.md`.
- When this slice closes, record the repaired anchor groups and grep
  classifications in the `TASK-158` parent completion summary, not frozen line
  ranges.
- Do not leave this leaf open if the `TASK-158` parent closes. Either close it
  with the parent or convert any deferred remaining scope into a standalone
  `Follow-on After` task tracked on `_docs/_TASKS/README.md`, then close or
  mark this leaf administratively superseded with an explicit reason in the
  same branch.

## Acceptance Criteria

- The long-form plan no longer instructs implementers to add a public
  `router_apply_reference_strategy` tool.
- The long-form plan no longer presents `reference_understand(...)` as a
  shipped public surface.
- Noncanonical family/tool names are clearly aliases or future candidates.
- Heavy perception adapter names are clearly future optional and outside
  TASK-158/MVP runtime activation.

## Completion Summary

- completed on 2026-05-03 by finishing the long-form plan cleanup on
  `_docs/blender-ai-mcp-vision-reference-understanding-plan.md`
- the plan now keeps `reference_understand(...)` and
  `router_apply_reference_strategy(...)` as historical/draft language rather
  than current public runtime contract
- `macro_create_part` was remapped to current create/register seams, while
  `mesh_shade_flat` and `macro_low_poly_*` remain explicitly future candidates
- the owner map and task sketch sections now point to current shared owners
  first (`reference.py`, `vision/prompting.py`, `vision/parsing.py`,
  `vision/backends.py`) and treat dedicated `reference_understanding*` modules
  as optional future splits only
- validated with:
  `git diff --check`
  and
  `rg -n "reference_understand|router_apply_reference_strategy|server/adapters/mcp/router|mesh_edit|material_finish|mesh_shade_flat|macro_low_poly|macro_create_part|SAM|CLIP|SigLIP|GroundingDINO|OWL-ViT" _docs/blender-ai-mcp-vision-reference-understanding-plan.md`
