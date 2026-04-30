# TASK-158-01: Long-Form Vision Plan Surface And Alias Cleanup

**Status:** ⏳ To Do
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

## Line-Level Targets

| Range | Required Work |
|-------|---------------|
| `_docs/blender-ai-mcp-vision-reference-understanding-plan.md:25-45` | Add upfront note for historical/draft naming |
| `:230-249` | Annotate diagram references to `mesh_edit` as aliases for current `modeling_mesh` or historical strategy labels |
| `:279-316` | Reframe `reference_understand(...)` example through current reference/guided-state seams |
| `:430-466` | Annotate `mesh_edit`, `material_finish`, `mesh_shade_flat`, and `macro_low_poly_finish` |
| `:511-518` | Replace or annotate noncanonical allowed families |
| `:641-688` | Fix allowlists that present aliases/future names as runtime vocabulary |
| `:744-815` | Reframe `reference_understand(...)`, `router_apply_reference_strategy(...)`, `mesh_edit`, and `material_finish` |
| `:948-968` | Mark low-poly macro examples as future candidates |
| `:1006-1012` | Mark finish/low-poly macro examples as future candidates |
| `:1155-1161` | Annotate remaining `mesh_edit` / `material_finish` JSON examples as aliases or future stage hints |
| `:1973-1989` | Classification-only row: concept-level `reference_understanding` hits are allowed when they do not imply a current public tool or verifier authority |
| `:2098-2183` | Replace obsolete owner-path sketches with current seams or historical notes |
| `:2306-2316` | Reframe `reference_understand(...)` success criteria as draft shorthand routed through current seams |
| `:2438-2459` | Reframe `reference_understand` MCP task as draft unless future public-tool review promotes it |
| `:2468-2476` | Replace obsolete `server/adapters/mcp/router/...` implementation paths with current owner seams or historical notes |
| `:2518-2525` | Mark remaining low-poly macro list as future optional candidates |
| `:2588-2595` | Reframe final `reference_understand(...)` summary as draft shorthand, not a shipped public tool |

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

## Tests / Validation

- `git diff --check`
- `rg -n "reference_understand|router_apply_reference_strategy|server/adapters/mcp/router" _docs/blender-ai-mcp-vision-reference-understanding-plan.md`
  - every remaining hit must be historical/draft or explicitly mapped to
    current seams
- `rg -n "mesh_edit|material_finish|mesh_shade_flat|macro_low_poly" _docs/blender-ai-mcp-vision-reference-understanding-plan.md _docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
  - every remaining hit must be alias/future/noncanonical wording

## Docs To Update

- `_docs/blender-ai-mcp-vision-reference-understanding-plan.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md` only if a cross-link is
  needed

## Changelog Impact

- Record completion in a new `_docs/_CHANGELOG/279-...task-158-...completion.md`
  entry when this slice ships, and refresh `_docs/_CHANGELOG/README.md`.
  Changelog 278 remains the creation/plan entry.

## Acceptance Criteria

- The long-form plan no longer instructs implementers to add a public
  `router_apply_reference_strategy` tool.
- The long-form plan no longer presents `reference_understand(...)` as a
  shipped public surface.
- Noncanonical family/tool names are clearly aliases or future candidates.
