# TASK-181-04: Scene-Graph Scope-Drift Regression Proof Lane

**Parent:** [TASK-181](./TASK-181_Scene_Graph_Diff_Compare_And_Registry_Scoped_Convergence.md)
**Status:** ⏳ To Do
**Follow-on After:** [TASK-181-01](./TASK-181-01_Part_Registry_As_First_Class_Scene_Graph_And_Compare_Scope.md), [TASK-181-02](./TASK-181-02_Graph_Vs_Graph_Diff_Contract_And_Relation_Vocabulary.md), [TASK-181-03](./TASK-181-03_K_Nearest_Relation_Triplet_Prompt_Serialization.md), [TASK-173-04](./TASK-173-04_Existing_Squirrel_Proof_Lane_Extension_And_Runtime_Evidence_Surfacing.md)
**Priority:** 🔴 High
**Objective:** Extend the existing squirrel proof lane to prove that, with the registered part graph as compare scope, the staged compare no longer drifts to a `Body + Head`-only scope, whole-assembly graph convergence keeps precedence, and a deliberately missing or over-scaled part is reported as a typed node/edge graph diff. Re-measure compare-quality direction on repo-owned golden fixtures rather than trusting external benchmark numbers.

**Repository Touchpoints:** `tests/e2e/vision/test_reference_guided_squirrel_quality_regression.py`, `scripts/vision_harness.py`, `tests/fixtures/vision_eval/`

**Acceptance Criteria:**
- the squirrel regression proves that, after registering body/head/tail/ears, the staged compare scope set ranges over the whole registered graph and is not collapsed to `{"Body + Head"}` (strengthening the existing `{packet.scope_label ...}` assertions)
- a new case proves a deliberately missing expected part is reported as a `missing` graph node diff and a deliberately over-scaled part is reported as a `proportion_out_of_bounds` edge diff (per TASK-181-02)
- the proof lane (or the harness golden run) asserts no raw coordinate tokens are emitted in the serialized packet prompt (per TASK-181-03)
- the lane re-measures compare-quality direction on `tests/fixtures/vision_eval` golden scenarios and records that external SceneVerse / 3DGraphLLM / Text-Scene / SceneCraft / ConceptGraphs numbers are NOT the acceptance bar

## Implementation Notes

- The existing lane is `tests/e2e/vision/test_reference_guided_squirrel_quality_regression.py`.
  It already builds a good squirrel (`_build_good_squirrel_with_local_ear_focus`
  at `:130`), seeds secondary state with an `active_target_scope` of
  `scope_kind="object_set"` / `primary_target=body_name`
  (`_seed_squirrel_secondary_state` at `:209-`), stubs vision via
  `_fake_run_vision_assist` (`:331`), and asserts the compare scope label set —
  `assert {packet.scope_label for packet in result.compare_diagnostics.packets}
  == {"Body + Head", "Tail"}` (`:383`) and the per-request
  `packet_scope` set (`:386`). This subtask updates those assertions so the
  registered-graph scope is the assertion target, proving precedence rather than
  the old name-cluster behavior.
- Add a case that registers the full part graph (body, head, tail, ears) through
  the guided registry path (`register_guided_part_role`,
  `session_capabilities_registry.py:276`) and asserts
  `build_compare_packets(...)` keeps a whole-assembly graph packet — i.e. the
  scope set covers all registered nodes and is not silently reduced to
  `{"Body + Head"}`.
- Add a missing-part / over-scaled-part case: omit one expected node from the
  built scene (or oversize one) while the expected graph from reference
  understanding still declares it, then assert the synthesized
  `compare_diagnostics` carries a `missing` node diff / `proportion_out_of_bounds`
  edge diff from TASK-181-02. Keep the deterministic squirrel quality metrics
  (`_squirrel_quality_metrics` at `:151`) as the authority oracle; the graph diff
  is advisory and is asserted as advisory.
- `scripts/vision_harness.py` already resolves golden scenarios
  (`_resolve_golden` at `:101`, `build_parser` at `:640`, `--golden-json` /
  `--references-json` / `--target-view` flags). Extend the harness output so a
  golden run records (a) the serialized `SCENE_GRAPH:` triplet block, (b) the
  node/edge graph diff, and (c) a no-raw-coordinate assertion, so the harness can
  re-measure on `tests/fixtures/vision_eval` (existing `squirrel_*` directories
  such as `squirrel_head_to_body`, `squirrel_face_to_body`).
- This lane is the RE-MEASUREMENT gate from the umbrella: the cited benchmarks
  are indoor-scan / synthetic, not Blender-vs-reference, so the proof lane must
  re-measure the actual compare-quality direction on repo fixtures before any
  promotion.

## Pseudocode

```python
def test_registered_graph_scope_keeps_whole_assembly_precedence(...):
    register_full_squirrel_graph(ctx, body, head, tail, ears)
    result = reference_compare_stage_checkpoint(...)
    scope_labels = {p.scope_label for p in result.compare_diagnostics.packets}
    assert ears in registered_graph_nodes(scope_labels)        # not collapsed to Body + Head
    assert "Body + Head" not in {scope_labels} or whole_assembly_packet_present(result)

def test_missing_and_over_scaled_part_surface_as_graph_diff(...):
    build_scene_without(expected_node="snout_mass")            # or oversize head
    result = reference_compare_stage_checkpoint(...)
    diff = result.compare_diagnostics.graph_diff
    assert any(n.state == "missing" and n.node_id == "snout_mass" for n in diff.nodes)
    assert any(e.state == "proportion_out_of_bounds" for e in diff.edges)
    assert diff.advisory_only is True                          # advisory, deterministic oracle still authority
    assert not serialized_prompt_has_raw_coordinates(captured_requests)
```

## Runtime / Security Contract Notes

- the proof lane must keep deterministic quality metrics
  (`_squirrel_quality_metrics`) and deterministic relation/assertion checks as
  the authority; the graph diff is asserted as advisory (`advisory_only`,
  `not_truth_source`) and must not be allowed to pass any gate in the test.
- all Blender-touching scene construction stays main-thread-safe and reversible
  through the existing fixtures (`clean_scene`, `modeling_handler`); the lane
  must restore scene state between cases as the current tests do.
- the no-raw-coordinate assertion enforces the TASK-181-03 boundary; ratios are
  proportional vs the trusted reference anchor only.

## Tests To Add/Update

- `tests/e2e/vision/test_reference_guided_squirrel_quality_regression.py` —
  update the scope-label assertions to the registered-graph target; add the
  whole-assembly-precedence case and the missing/over-scaled-part graph-diff case
- `tests/fixtures/vision_eval/` — extend an existing `squirrel_*` golden scenario
  (or add one) with expected `SCENE_GRAPH:` triplets and graph-diff expectations
- `scripts/vision_harness.py` — surface the serialized graph block, graph diff,
  and the no-raw-coordinate check in the golden-run output

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`

## Changelog Impact

- add/update the historical `_docs/_CHANGELOG/*` entry when this slice lands

## Status / Board Update

- board tracking remains on umbrella `TASK-181`
- no separate promoted board-row change is expected for this subtask unless it
  later becomes a standalone follow-on

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_guided_squirrel_quality_regression.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py` (Blender-backed squirrel scene construction and guided compare change)

## Validation Category

- scene-graph scope-drift regression and re-measurement proof
