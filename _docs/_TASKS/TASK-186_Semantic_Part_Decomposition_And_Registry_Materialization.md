# TASK-186: Semantic Part Decomposition And Registry Materialization

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Category:** Reconstruction / Mesh Understanding / Part Registry
**Estimated Effort:** Extra Large
**Follow-on After:** [TASK-150](./TASK-150_Server_Driven_Guided_Flow_State_Step_Gating_And_Domain_Profiles.md), [TASK-172](./TASK-172_Optional_Vision_Capability_Runtime_And_Localized_Perception.md), [TASK-179](./TASK-179_Blender_Depth_Normal_And_Object_ID_Auxiliary_Passes.md), [TASK-181](./TASK-181_Scene_Graph_Diff_Compare_And_Registry_Scoped_Convergence.md)
**Related:** [TASK-184](./TASK-184_Vision_3D_Understanding_Audit_Corrections.md), [TASK-185](./TASK-185_Optional_Generative_3D_Seed_Asset_Intake.md)

## Objective

Add an explicit, deterministic-first lane for turning one imported, scanned, or
generated mesh into named semantic parts that can be materialized as Blender
objects or face groups and registered with the guided part registry.

## Business Problem

Existing segmentation and object-ID work covers reference-image sidecars,
render-side object masks, and explicit guided part registration. It does not
cover the end-to-end flow:

one mesh -> semantic part hypotheses -> image-mask/mesh-polygon lift -> materialized
part objects or groups -> the existing guided part registry state and
`guided_register_part(...)` path -> deterministic inspection and correction.

Without this task, future docs risk implying the current object-ID sidecar can
do per-pixel mesh-polygon semantic part decomposition. It cannot.

## Business Outcome

After this family lands, the system can take a single complex asset and create a
bounded, inspectable part structure that the existing guided/reference loop can
reason about without confusing advisory segmentation with verified geometry.

## Non-Goals

- do not claim pass-index masks provide mesh-polygon IDs
- do not let a sidecar label become registry truth without deterministic
  materialization and operator-visible provenance
- do not require one specific model family before the provider boundary task
  chooses a concrete strategy
- do not make generated/scanned asset decomposition a default guided step

## Execution Structure

| Order | Task | Purpose |
|------|------|---------|
| 1 | [TASK-186-01](./TASK-186-01_Decomposition_Strategy_And_Provider_Boundary.md) | Select and bound the decomposition strategy/provider surface |
| 2 | [TASK-186-02](./TASK-186-02_Mask_To_Mesh_Face_Lift_And_Part_Materialization.md) | Define mask/segment-to-face lift and materialized part output |
| 3 | [TASK-186-03](./TASK-186-03_Part_Naming_And_Guided_Register_Part_Integration.md) | Normalize part names and register materialized parts with guided state |
| 4 | [TASK-186-04](./TASK-186-04_Generative_Sculpt_Scan_E2E_Proof.md) | Prove the full path on fixture assets before live provider claims |

## Repository Touchpoints

| Path / Module | Expected Ownership | Why It Is In Scope |
|---------------|--------------------|--------------------|
| `server/adapters/mcp/contracts/`, `server/application/tool_handlers/` | typed decomposition contracts and server handlers | the flow needs strict payloads and reject-unknown behavior |
| `blender_addon/application/handlers/` | mesh face/group/object materialization | decomposition results must become inspectable Blender state |
| `server/adapters/mcp/areas/router.py`, `server/adapters/mcp/session_capabilities_registry.py`, `server/adapters/mcp/session_capabilities_state.py` | `guided_register_part(...)`, `register_guided_part_role(_async)`, and `guided_part_registry` state | materialized parts must join the existing guided registry instead of a parallel registry module |
| `tests/unit/`, `tests/e2e/` | contract and Blender-backed proof | both payload safety and real mesh mutation need coverage |

## Test Matrix

| Slice | Primary Validation Lane | Why |
|------|--------------------------|-----|
| provider/decomposition boundary | unit tests for disabled, unavailable, unsupported-provider, and reject-unknown payload states | the first wave must fail closed before any sidecar output is trusted |
| face/group materialization | Blender-backed E2E fixture for face groups or separated objects plus a negative empty/ambiguous case | materialization mutates real mesh state and must be inspectable |
| guided registry integration | unit tests around `guided_register_part(...)` / `register_guided_part_role(_async)` and E2E guided transport if the public surface changes | decomposed parts must use the existing registry state and role validation |
| docs/regression fixtures | `git diff --check`, consistency grep, and fixture provenance checks | prevents pass-index/polygon-ID and registry-path drift from returning |

## Runtime / Security Contract Notes

- decomposition is mutating only when materializing parts; pure analysis should
  be read-only
- sidecar/model evidence is advisory until materialized and verified
- payloads must preserve provenance: provider, source asset, face/group/object
  IDs, confidence, and operator-visible uncertainty
- unknown fields should be rejected where contracts are strict

## Acceptance Criteria

- the repo has a typed part decomposition contract that does not overload
  object-ID evidence
- materialized parts can be inspected, named, and registered through the existing
  guided registry seam
- E2E proof covers at least one fixture mesh and one negative/ambiguous case

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_ADDON/README.md`
- `_docs/_TASKS/README.md`
- `_docs/_VISION/README.md` if reference-side masks seed any part hypotheses

## Changelog Impact

- add `_docs/_CHANGELOG/*` entries as implementation slices land

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py` after Blender materialization lands
