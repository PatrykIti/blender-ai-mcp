# TASK-126: Mesh-Aware Contact Semantics and Visual Fit Reliability

**Priority:** 🔴 High  
**Category:** Truth Layer / Scene Verification  
**Estimated Effort:** Large  
**Dependencies:** TASK-116, TASK-117, TASK-122  
**Status:** 🚧 In Progress

**Progress Summary:** The first implementation slice is now in place:
mesh-object pairs no longer rely only on bbox-touching for
`scene_measure_gap(...)`, `scene_measure_overlap(...)`, and
`scene_assert_contact(...)`. The truth layer now prefers a bounded mesh-surface
gap/contact path for `MESH` pairs and falls back to bbox semantics only when a
mesh-aware path is unavailable. Unit and E2E regression coverage were added
for the canonical "bbox-touching but visibly gapped" case.

## Objective

Fix the current mismatch where scene truth tools can report contact/touching
even when the viewport still shows a visible gap between curved or rounded
meshes.

The product needs one explicit, trustworthy contact model for:

- truth tools
- macro verification
- hybrid compare/iterate loops
- operator-facing diagnostics

## Business Problem

The current first-wave truth layer is heavily bounding-box oriented.

That is useful for coarse assembly checks, but it creates a serious product
problem on curved primitives and smooth meshes:

- `scene_measure_overlap(...)` can report `touching`
- `scene_assert_contact(...)` can pass
- hybrid truth bundles can mark a pair as fixed

while the viewport still shows a visible gap or obviously wrong visual fit.

This is not a small cosmetic disagreement.
It makes the product look self-contradictory:

- operators see a gap
- the truth layer says contact passed
- the loop may stop or move on

That breaks trust in the verification layer itself.

## Business Outcome

If this task is done correctly, the repo gains:

- explicit semantics for coarse bbox contact vs actual mesh/surface contact
- more truthful contact/gap verification for curved or rounded forms
- macro and hybrid-loop validation that no longer claims visual fit too early
- clearer operator diagnostics when a pair is only bbox-touching, not truly
  surface-touching

## Scope

This umbrella covers:

- auditing the current bbox-oriented contact semantics
- defining the product contract for bbox contact vs mesh/surface contact
- adding a more truthful mesh-aware contact/gap path where needed
- updating macro/hybrid-loop consumers to use the right semantics
- regression coverage and docs for the new truth behavior

This umbrella does **not** cover:

- arbitrary high-cost mesh booleans or remeshing as part of measurement
- replacing all first-wave scene truth tools at once
- solving every topology-quality problem in the same wave
- changing unrelated router intent/discovery behavior

## Success Criteria

- the repo explicitly distinguishes bbox-touching from actual visual/mesh fit
- `scene_assert_contact(...)` and downstream consumers stop passing obviously
  gapped curved pairs as if they were visually correct contact
- macro verification and hybrid loops use semantics that align with what the
  operator sees in the viewport
- docs and tests explain the new truth contract clearly

## Repository Touchpoints

- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/contracts/scene.py`
- `server/adapters/mcp/areas/reference.py`
- `server/application/tool_handlers/scene_handler.py`
- `server/application/tool_handlers/macro_handler.py`
- `blender_addon/application/handlers/scene_handler.py`
- `tests/unit/tools/scene/`
- `tests/unit/tools/macro/`
- `tests/unit/adapters/mcp/`
- `tests/e2e/tools/scene/`
- `tests/e2e/vision/`
- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`
- `_docs/_TASKS/README.md`

## Completion Update Requirements

- add a `_docs/_CHANGELOG/*` entry and update `_docs/_CHANGELOG/README.md`
- update the truth/assertion docs and any hybrid-loop docs that describe
  contact validation
- add or update focused unit coverage first, then E2E coverage where runtime
  mesh behavior matters
- keep `_docs/_TASKS/README.md` and all child task statuses in sync

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-126-01](./TASK-126-01_Contact_Semantics_Audit_And_Product_Contract.md) | Define the product contract for bbox-touching vs mesh/surface contact and identify where current wording/behavior drifts |
| 2 | [TASK-126-02](./TASK-126-02_Mesh_Aware_Contact_And_Gap_Measurement_Path.md) | Add a more truthful mesh-aware contact/gap path for curved/rounded object pairs |
| 3 | [TASK-126-03](./TASK-126-03_Macro_And_Hybrid_Loop_Adoption_Of_True_Contact_Semantics.md) | Make macro verification and hybrid truth bundles consume the right contact semantics |
| 4 | [TASK-126-04](./TASK-126-04_Regression_Pack_And_Docs_For_Visual_Fit_Truth.md) | Lock the new semantics in with docs, payload tests, and visual-fit regressions |
