# TASK-184: Vision 3D Understanding Audit Corrections

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Category:** Vision / 3D Understanding Reliability / Audit Follow-Up
**Estimated Effort:** Extra Large
**Follow-on After:** [TASK-143](./TASK-143_Guided_Spatial_Scope_And_Relation_Graphs.md), [TASK-149](./TASK-149_Guided_Default_Spatial_Graph_And_View_Diagnostics_For_All_Goal_Oriented_Sessions.md), [TASK-179](./TASK-179_Blender_Depth_Normal_And_Object_ID_Auxiliary_Passes.md), [TASK-180](./TASK-180_Set_Of_Mark_Object_Bound_Visual_Marks.md), [TASK-181](./TASK-181_Scene_Graph_Diff_Compare_And_Registry_Scoped_Convergence.md), [TASK-183](./TASK-183_Capability_Enriched_Vision_Schema_And_Deterministic_Cross_Check.md)
**Related:** [TASK-140-06](./TASK-140-06_OpenRouter_Model_Capability_Aware_Vision_Runtime.md), [TASK-172](./TASK-172_Optional_Vision_Capability_Runtime_And_Localized_Perception.md), [TASK-178](./TASK-178_Structured_Per_Finding_Compare_Schema.md), [TASK-186](./TASK-186_Semantic_Part_Decomposition_And_Registry_Materialization.md)

## Objective

Convert the June 2026 Vision 3D understanding audit into actionable follow-up
work without reopening the completed `TASK-174` through `TASK-183` Vision Output
Quality wave.

This task fixes the gaps that were not actually covered by the completed base
tasks:

- Set-of-Mark overlays are globally gated but not gated by per-model mark
  reasoning capability.
- live mark anchors are mask-centroid based instead of projection-first, even
  though Blender already exposes camera projection diagnostics.
- deterministic spatial graphs cover contact/gap/overlap/alignment/attachment/
  support/symmetry, but not framed directional predicates such as world/camera
  left, right, front, or behind.
- object-ID mask evidence is object-level `pass_index` evidence and must not be
  described as Cryptomatte, semantic part segmentation, or pixel-to-face proof.
- relative depth auxiliary captions do not yet state the concrete encoding
  direction.
- the evaluation harness lacks a geometry-derived per-axis scorecard for the
  specific perception axes this audit cares about.

## Business Outcome

After this family lands, the vision loop should make fewer capability
assumptions, attach marks to objects with deterministic camera-aware placement,
report directional spatial facts with explicit frames, and evaluate VLM 3D
understanding failures by axis rather than as one blended confidence number.

The core boundary remains unchanged: vision is advisory, while Blender
inspection/assertion and deterministic render evidence remain the authority for
scene truth.

## Non-Goals

- do not make marks, VLM findings, semantic similarity, or auxiliary images gate
  authority
- do not claim object-ID masks provide semantic parts, face IDs, or pixel-to-face
  lift
- do not make Cryptomatte or heavyweight perception sidecars default-on
- do not expose unframed `left/right/front/behind` predicates without a named
  reference frame
- do not implement generative-3D seed import or semantic part decomposition in
  this task family; those are tracked by `TASK-185` and `TASK-186`

## Execution Structure

| Order | Task | Purpose |
|------|------|---------|
| 1 | [TASK-184-01](./TASK-184-01_Per_Model_Set_Of_Mark_Overlay_Gating.md) | Gate Set-of-Mark overlays by explicit model/runtime capability in addition to the global operator flag |
| 2 | [TASK-184-02](./TASK-184-02_Projection_Based_Set_Of_Mark_Anchors.md) | Prefer Blender camera projection diagnostics for mark anchors, with current mask-centroid placement as fallback |
| 3 | [TASK-184-03](./TASK-184-03_Directional_Spatial_Predicates_From_OBBs.md) | Add deterministic frame-tagged directional predicates to spatial graph contracts and builders |
| 4 | [TASK-184-04](./TASK-184-04_Object_ID_Mask_Contract_Hardening.md) | Harden object-ID mask docs/tests around pass-index limits and optional Cryptomatte feasibility |
| 5 | [TASK-184-05](./TASK-184-05_Depth_Auxiliary_Caption_Encoding_Legend.md) | State the actual relative-depth encoding in auxiliary captions and tests |
| 6 | [TASK-184-06](./TASK-184-06_Per_Axis_Advisory_Reliability_Scorecard.md) | Add a default-off per-axis scorecard for object identity, mark correspondence, depth ordering, and spatial relations |
| 7 | [TASK-184-07](./TASK-184-07_Implementation_Docs_Board_And_Closeout_Proof.md) | Keep board rows, historical task notes, docs, changelog, and validation proof synchronized as the family lands |

## Repository Touchpoints

| Path / Module | Expected Ownership | Why It Is In Scope |
|---------------|--------------------|--------------------|
| `server/adapters/mcp/vision/config.py`, `server/adapters/mcp/vision/model_profiles/`, `server/adapters/mcp/areas/reference.py` | model/runtime capability and overlay emission policy | Set-of-Mark overlays need model-aware gating, not only a global flag |
| `server/adapters/mcp/vision/marks.py`, `server/adapters/mcp/vision/capture_runtime.py`, `blender_addon/application/handlers/scene_viewport_mixin.py` | live mark anchor selection and projection diagnostics | mark placement should reuse deterministic camera projection before image-mask fallback |
| `server/application/services/spatial_graph.py`, `server/adapters/mcp/areas/scene_spatial_graph.py`, `server/adapters/mcp/contracts/scene.py` | relation graph builder, routing owner, and typed relation contract | directional predicates belong in the deterministic spatial graph truth layer and the public relation-graph route must carry them |
| `server/adapters/mcp/vision/silhouette.py`, `server/adapters/mcp/areas/reference_silhouette.py`, `server/adapters/mcp/contracts/reference.py` | object-ID evidence, auxiliary evidence projection, and scorecard payloads | object-level masks and per-axis reliability need typed evidence surfaces |
| `tests/unit/adapters/mcp/`, `tests/unit/tools/scene/`, `tests/e2e/tools/scene/`, `tests/e2e/vision/` | contract, policy, and Blender-backed proof | the family changes both server contracts and real capture/render behavior |
| `_docs/_TASKS/README.md`, `_docs/_VISION/README.md`, `_docs/_MCP_SERVER/README.md`, `_docs/AVAILABLE_TOOLS_SUMMARY.md` | public documentation and task board | docs must stop implying completed base tasks already cover these corrections |

## Test Matrix

| Slice | Primary Validation Lane | Why |
|------|--------------------------|-----|
| model-aware mark gating | unit tests for vision runtime config, model profile resolution, staged compare payload selection | proves unknown/weak models do not receive mark-heavy schemas or overlay captures by accident |
| projection-based mark anchors | Blender-backed E2E plus unit fallback tests | proves projected, off-frame, behind-view, and unavailable cases are explicit |
| directional predicates | spatial graph service unit tests and scene contract parity tests | proves direction facts are deterministic and frame-tagged |
| object-ID hardening | unit tests for high-count/pass-index limits and mask artifact metadata | prevents object-ID evidence from being treated as semantic part or face evidence |
| depth caption encoding | unit tests for caption builders and payload parity | prevents near/far interpretation drift |
| per-axis scorecard | fixture/harness tests behind explicit enablement | proves scorecard values are advisory and axis-specific |

## Acceptance Criteria

- Set-of-Mark overlay emission requires both the operator/config flag and an
  explicit model/runtime capability indicating mark reasoning support.
- live mark overlays use projection-first anchors with explicit fallback and
  failure states.
- relation graph responses can report deterministic directional predicates with
  `reference_frame` metadata and ambiguity thresholds.
- object-ID docs/contracts/tests describe the current object-level pass-index
  evidence accurately and record any Cryptomatte path as optional/future.
- relative-depth auxiliary captions state the actual encoding direction:
  `near_bright_far_dark`.
- a default-off scorecard can report per-axis advisory reliability without
  becoming gate authority.

## Docs To Update

- `_docs/_TASKS/README.md`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- completed parent task files only as historical follow-on notes, without
  reopening their status

## Changelog Impact

- add a `_docs/_CHANGELOG/*` entry when the first implementation slice lands
- add a closeout changelog when `TASK-184-07` closes the family

## Validation Commands

- `git diff --check`
- `rg -n "near_dark_far_bright|object-ID.*face|pixel.*face|Cryptomatte.*shipped|SAM3|TASK-183.*Structural" _TMP* _docs server tests`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/tools/scene/test_spatial_graph_service.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py` after the projection/Blender-facing slices land
