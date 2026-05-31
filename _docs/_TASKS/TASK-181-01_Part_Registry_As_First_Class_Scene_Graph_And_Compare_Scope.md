# TASK-181-01: Part Registry As First-Class Scene Graph And Compare Scope

**Parent:** [TASK-181](./TASK-181_Scene_Graph_Diff_Compare_And_Registry_Scoped_Convergence.md)
**Status:** ✅ Done
**Priority:** 🔴 High
**Follow-on After:** [TASK-173-01](./TASK-173-01_Assembled_Creature_Workset_Persistence_And_Packet_Scope_Arbitration.md), [TASK-171-03](./TASK-171-03_Registry_Backed_Creature_Seam_Authority_And_Opaque_Naming.md)
**Objective:** Promote the guided part registry / `assembled_target_scope` to a typed scene graph that is the canonical compare scope, so registering a part extends the comparison scope and whole-assembly convergence keeps precedence (fixing the `Body + Head` drift). The registered graph — not the name-heuristic clustering in `reference_compare_packets.py` — must own which nodes the staged compare ranges over.

**Repository Touchpoints:** `server/adapters/mcp/areas/reference_compare_packets.py`, `server/adapters/mcp/session_capabilities_registry.py`, `server/adapters/mcp/contracts/reference.py`, `server/adapters/mcp/contracts/vision.py`

**Acceptance Criteria:**
- registering a part via `guided_register_part(...)` adds a node to the canonical compare scope graph, and `build_compare_packets(...)` derives packet scope from that graph rather than from `_is_head_like` / `_is_body_like` name heuristics
- whole-assembly graph convergence keeps precedence: the assembled graph is the default packet scope and cannot be silently collapsed to a `Body + Head`-only cluster unless a later packet contract explicitly narrows it
- the registered graph is carried on `VisionCaptureBundleContract.assembled_target_scope` and surfaced on `ReferenceCompareDiagnosticsContract` additively, without breaking existing `target_objects` / `scope_label` fields
- the graph node identity is the registered object name (opaque), preserving `TASK-171-03` opaque-naming authority; no raw coordinates are stored on graph nodes

## Implementation Notes

- Today `register_guided_part_role_async(...)` (`session_capabilities_registry.py:214-273`)
  appends a `GuidedPartRegistryItem` (`session_capabilities_state.py:58-65`:
  `object_name` / `role` / `role_group` / `status` / `created_in_step`) and then
  calls `_maybe_expand_active_target_scope_dict(...)` (`:182-211`) which widens
  `GuidedFlowStateContract.active_target_scope` (`GuidedFlowStateContract` at
  `contracts/guided_flow.py:59`, `active_target_scope` field at `:66`; its
  `GuidedTargetScopeContract` type is at `:39-46`) and recomputes
  `spatial_scope_fingerprint`. The widened scope already exists;
  the gap is that compare ignores it as authority.
- `build_compare_packets(...)` (`reference_compare_packets.py:1016-1210`) takes
  `assembled_target_scope: SceneAssembledTargetScopeContract`
  (`contracts/scene.py:182-189`) and, for complex tiers, re-derives scope via
  `_scope_clusters_from_target_scope(...)` (`:676-764`) using
  `_semantic_scope_label(...)` (`:603-616`) and the name-hint predicates
  (`:571-600`). This is the drift source: the hardcoded `Body + Head` / `Tail` /
  `Ears` clusters can shrink the registered scope.
- This subtask threads the registered part graph (object_names + roles +
  declared expected relations) into `build_compare_packets(...)` and makes it the
  default packet scope. The name-heuristic clustering becomes a fallback used
  only when no registered graph is present (e.g., non-guided ad-hoc compare),
  preserving `TASK-166` behavior for those paths.
- Reuse the existing `SceneScopeObjectRoleContract` (`contracts/scene.py:175-179`,
  already on `SceneAssembledTargetScopeContract.object_roles`) for node roles so
  no parallel role taxonomy is introduced. Edge identity reuses the fixed
  `SceneRelationKindLiteral` vocabulary (`contracts/scene.py:22`) — the actual
  diff contract lands in TASK-181-02.
- This is the SceneVerse (arXiv:2401.09340) "graph is the scope" idea and the
  SceneCraft (arXiv:2403.01248) scene-graph-blueprint posture applied to the
  build state: the registry IS the blueprint, and compare ranges over it.
- Keep Clean Architecture direction: the registry/scope promotion lives in the
  adapter layer (`session_capabilities_registry.py`,
  `reference_compare_packets.py`); contracts stay declarative pydantic models.

## Pseudocode

```python
# session_capabilities_registry.py — after register_guided_part_role appends a node
def _registered_part_graph_scope(part_registry, active_target_scope):
    # nodes = registered objects (opaque names) + their roles
    object_names = [item["object_name"] for item in part_registry]
    object_roles = [
        {"object_name": item["object_name"], "role": item["role"]}
        for item in part_registry
    ]
    # the registered graph is the canonical compare scope; whole assembly wins
    return SceneAssembledTargetScopeContract(
        scope_kind="object_set" if len(object_names) > 1 else "single_object",
        primary_target=active_target_scope.primary_target or (object_names[0] if object_names else None),
        object_names=object_names,
        object_count=len(object_names),
        object_roles=object_roles,
    )


# reference_compare_packets.py — build_compare_packets
def _scope_clusters(assembled_target_scope, registered_graph, focus_pairs, prefer_target_scope_clusters):
    if registered_graph is not None and registered_graph.object_count >= 1:
        # graph IS the scope: assembled-graph packet has precedence over name clusters
        return _scope_clusters_from_registered_graph(registered_graph)
    # legacy fallback only when no registered graph exists (ad-hoc compare)
    return _scope_clusters_from_target_scope(assembled_target_scope)
```

## Runtime / Security Contract Notes

- the registered graph is build/runtime state owned by the server; promoting it
  to compare scope does not grant vision any authority. Vision output measured
  against this graph stays advisory (`VisionBoundaryPolicyContract`,
  `sampling/result_types.py:115-123`): `not_truth_source`,
  `requires_deterministic_checks_for_correctness`, no gate completion, no tool
  unlock.
- node identity is the opaque registered object name; do not store or emit raw
  coordinates on graph nodes (raw coordinates hurt LLM spatial reasoning per
  3DGraphLLM arXiv:2412.18450; coordinates remain on-demand only).
- scope promotion must be reversible and main-thread-safe: it only reshapes the
  already-persisted session scope; it must not mutate Blender scene state, so no
  `capture_scene_state` / `restore_scene_state` bracket is required here, but the
  proof lane (TASK-181-04) still exercises the guided session end to end.
- preserve `spatial_refresh_required` / fingerprint behavior in
  `_maybe_expand_active_target_scope_dict(...)`; do not weaken the refresh gate to
  make scope promotion easier.

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_compare_packets.py` — assert
  `build_compare_packets(...)` ranges over the registered graph nodes and keeps a
  whole-assembly packet when a registered graph is present; assert the
  name-heuristic clustering is used only as the no-registry fallback
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py` — assert
  registering a part extends the canonical compare scope and that whole-assembly
  precedence is retained (no silent collapse to `Body + Head`)

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`

## Changelog Impact

- add/update the historical `_docs/_CHANGELOG/*` entry when this slice lands

## Status / Board Update

- board tracking remains on umbrella `TASK-181`
- no separate promoted board-row change is expected for this subtask unless it
  later becomes a standalone follow-on
- 2026-05-31: completed. Guided part registry state can now be projected into a
  `SceneAssembledTargetScopeContract`, staged compare uses that registered graph
  as the compare scope before focus-pair/name heuristics, and diagnostics expose
  `registered_compare_scope` / packet `scope_source` for auditability.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py` (guided registry + compare scope is exercised end to end)
- 2026-05-31 focused validation:
  `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_compare_packets.py::test_build_compare_packets_prefers_registered_part_graph_over_name_focus_clusters tests/unit/adapters/mcp/test_guided_flow_state_contract.py::test_guided_registry_compare_scope_projects_stable_registered_part_graph -q` -> passed in the focused registry lane
  targeted MCP lane ending in 180 passed

## Validation Category

- registry-as-compare-scope graph promotion proof
