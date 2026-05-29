# TASK-181-03: K-Nearest Relation-Triplet Prompt Serialization

**Parent:** [TASK-181](./TASK-181_Scene_Graph_Diff_Compare_And_Registry_Scoped_Convergence.md)
**Status:** ⏳ To Do
**Follow-on After:** [TASK-181-01](./TASK-181-01_Part_Registry_As_First_Class_Scene_Graph_And_Compare_Scope.md), [TASK-181-02](./TASK-181-02_Graph_Vs_Graph_Diff_Contract_And_Relation_Vocabulary.md)
**Priority:** 🔴 High
**Objective:** Serialize the active scene graph for the VLM packet prompt as per-object k-nearest relation triplets (symbolic relations plus proportional ratios), explicitly NOT raw coordinates, and scope the serialized roster to the current graph nodes plus declared expected relations. This is how the registered graph from TASK-181-01 and the expected graph from reference understanding reach the model without coordinate tokens that degrade spatial reasoning.

**Repository Touchpoints:** `server/adapters/mcp/vision/prompting.py`, `server/adapters/mcp/areas/reference_understanding.py`

**Acceptance Criteria:**
- the packet compare prompt path emits an explicit `SCENE_GRAPH` / relation-triplet block scoped to the current graph nodes plus the declared expected relations, instead of (or in addition to) the flat `IMAGES:` roster
- triplets are serialized symbolically as `(subject_role, relation_kind, object_role)` with an optional proportional ratio token, drawn from the fixed `SceneRelationKindLiteral` vocabulary; per object only the k-nearest related nodes are emitted (bounded k)
- no raw coordinate tokens (positions, world transforms, bbox corner floats) appear as primary evidence anywhere in the serialized prompt
- the serialization stays within the existing packet budget and packet-bounded scope; it does not reopen the `VISION_MAX_IMAGES` budget or add a heavy full-scene pass

## Implementation Notes

- The packet compare prompt is built in `build_vision_payload_text(...)`
  (`prompting.py:620-732`). Today its scene context is a flat `IMAGES:` roster
  (`:659-661`) plus `PACKET_REFERENCE_IDS` / `PACKET_CAPTURE_LABELS` /
  `SUPPORT_EVIDENCE` / `TRUTH_SUMMARY` lines (`:662-669`). There is no symbolic
  graph block, so the model has to infer structure from prose.
- Add a `SCENE_GRAPH:` block (k-nearest relation triplets) sourced from the
  active registered graph (TASK-181-01) and the expected graph from reference
  understanding. Expected edges come from `attachment_plan[*].required_relation`
  (`contracts/reference.py:161-169`) and `contact_expectations`
  (`:172-179`); node roles come from the registered `object_roles`
  (`SceneScopeObjectRoleContract`, `contracts/scene.py:175-179`). The
  normalization helper in `reference_understanding.py` (around `:176-258`,
  `_canonicalize_reference_understanding_summary_targets`) is the right place to
  expose a bounded triplet projection alongside the existing summary so the
  prompt builder can consume it via request metadata.
- Serialize each triplet as `(subject_role, relation_kind, object_role)` plus an
  optional proportional-ratio annotation (e.g. `head:body size ratio ~ 0.6x`)
  derived from the trusted reference anchor. This is the 3DGraphLLM
  relation-triplet posture (arXiv:2412.18450) and the Text-Scene finding that
  symbolic relations (59.4) beat raw coordinates (18.4) for spatial reasoning
  (arXiv:2509.16721). SceneCraft (arXiv:2403.01248) motivates emitting the graph
  blueprint explicitly to the model.
- "k-nearest" here is graph-structural / relation-declared nearness, not
  geometric distance over coordinates: for each node, emit only its declared /
  highest-priority related neighbors (bounded k, e.g. k<=3) from `attachment_plan`
  + `part_order` adjacency, so the prompt stays packet-bounded.
- Do not add VLM-side chain-of-thought instructions for spatial judgments
  (VSI-Bench regression -1..-21%); the prompt still asks for the same bounded
  JSON keys (`prompting.py:704-731`) and the graph-diff fields from TASK-181-02.
  Reasoning stays in the orchestrator.
- Keep the local-model payload (`build_local_vision_payload_text(...)`,
  `prompting.py:758-768`) consistent: it already delegates packet compare to
  `build_vision_payload_text(...)`, so the `SCENE_GRAPH:` block flows to both
  transmit paths.

## Pseudocode

```python
# prompting.py — inside the packet compare branch of build_vision_payload_text
def _scene_graph_triplet_lines(graph_payload, *, k=3):
    lines = ["SCENE_GRAPH:"]
    for node in graph_payload.nodes:               # current graph nodes only
        neighbors = node.declared_relations[:k]    # k-nearest by declared adjacency, NOT coordinates
        for rel in neighbors:
            ratio = f" ratio~{rel.proportion_ratio:.2f}x" if rel.proportion_ratio else ""
            lines.append(f"- ({node.role}, {rel.relation_kind}, {rel.object_role}){ratio}")
    return lines

# scope strictly to graph nodes + declared expected relations; never emit coordinates
if scene_graph_payload is not None:
    parts.extend(_scene_graph_triplet_lines(scene_graph_payload))
assert not any(_looks_like_raw_coordinate(line) for line in parts)  # guard in tests/fixtures
```

## Runtime / Security Contract Notes

- the serialized graph is advisory context, not authority: the prompt continues
  to require the advisory JSON shape and the boundary policy
  (`VisionBoundaryPolicyContract`, `sampling/result_types.py:115-123`) is
  unchanged — `not_truth_source`, `requires_deterministic_checks_for_correctness`.
- proportional ratios in triplets are vs the trusted reference anchor, never
  absolute measurements; the model is told they are advisory ratios.
- raw coordinates are never emitted as primary evidence; a fixture/test guard
  asserts the serialized prompt contains no coordinate tokens.
- the `SCENE_GRAPH:` block is packet-bounded and must not enlarge the image
  budget or trigger a full-scene heavy pass.

## Tests To Add/Update

- `tests/fixtures/vision_eval/` — add a golden fixture (e.g. under a
  `squirrel_*` scenario directory) whose expected serialized prompt contains a
  `SCENE_GRAPH:` triplet block and asserts the absence of raw coordinate tokens
- `tests/unit/adapters/mcp/test_reference_compare_packets.py` — assert the
  packet prompt for a registered graph emits per-object k-nearest relation
  triplets scoped to graph nodes and proportional-ratio annotations, with no
  coordinate tokens

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
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_compare_packets.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- `poetry run python scripts/vision_harness.py --help` (confirm the harness can drive the updated packet prompt against `tests/fixtures/vision_eval` golden scenarios)

## Validation Category

- k-nearest relation-triplet serialization and no-raw-coordinates proof
