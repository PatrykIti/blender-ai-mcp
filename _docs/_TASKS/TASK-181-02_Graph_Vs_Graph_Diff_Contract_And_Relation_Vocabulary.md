# TASK-181-02: Graph-Vs-Graph Diff Contract And Relation Vocabulary

**Parent:** [TASK-181](./TASK-181_Scene_Graph_Diff_Compare_And_Registry_Scoped_Convergence.md)
**Status:** ⏳ To Do
**Follow-on After:** [TASK-181-01](./TASK-181-01_Part_Registry_As_First_Class_Scene_Graph_And_Compare_Scope.md)
**Priority:** 🔴 High
**Objective:** Define a typed graph-vs-graph diff contract — per-node attribute deltas and per-edge relation mismatches over a fixed relation vocabulary — as the primary compare evidence shape, so compare can report a missing expected part (absent node) and a wrong part-to-part proportion (out-of-bounds edge ratio) against the expected graph derived from reference understanding. The legacy bare-string evidence fields stay populated for backward compatibility.

**Repository Touchpoints:** `server/adapters/mcp/contracts/reference.py`, `server/adapters/mcp/areas/reference_planner.py`, `server/adapters/mcp/sampling/result_types.py`

**Acceptance Criteria:**
- a typed graph-diff contract is added additively to `ReferenceCompareDiagnosticsContract` (and projected per packet on `ReferenceComparePacketContract`) carrying expected-vs-observed nodes and edges
- node diffs distinguish at least `present`, `missing`, and `unexpected` states; edge diffs distinguish at least `relation_match`, `relation_mismatch`, and `proportion_out_of_bounds`, where proportion is a PROPORTIONAL RATIO vs a trusted reference anchor, never an absolute measurement
- edge relation kinds are drawn only from the existing fixed `SceneRelationKindLiteral` vocabulary; no parallel taxonomy is introduced
- `reference_planner.py` maps node-missing diffs and edge-relation/proportion mismatches into the existing typed planner blockers (relation / proportion / scope) instead of new ad-hoc string blockers
- the existing `shape_mismatches` / `proportion_mismatches` / `correction_focus` string lists on `VisionAssistContract` remain populated so no downstream consumer regresses

## Implementation Notes

- The fixed relation vocabulary already exists:
  `SceneRelationKindLiteral = Literal["contact", "gap", "overlap", "alignment",
  "attachment", "support", "symmetry"]` (`contracts/scene.py:22`) and the typed
  deterministic relation graph `SceneRelationGraphPairContract`
  (`contracts/scene.py:249-266`). The diff contract MUST reuse this vocabulary so
  the advisory graph diff and the deterministic relation graph speak the same
  edge language. This is the SceneVerse (arXiv:2401.09340) fixed-taxonomy idea.
- The expected graph comes from reference understanding: `mass_recipe`,
  `attachment_plan`, `contact_expectations`, `part_order`
  (`contracts/reference.py:280-286`, normalized in `reference_understanding.py`
  around `:176-258`). `attachment_plan[*].required_relation`
  (`ReferenceUnderstandingAttachmentRelationLiteral`,
  `contracts/reference.py:102-109`) supplies expected edges; `part_order` /
  `required_parts` supply expected nodes. The diff is observed-graph vs this
  expected-graph (a 3DGraphLLM-style relation-triplet comparison,
  arXiv:2412.18450, and ConceptGraphs-style multi-view-fused object graph,
  arXiv:2309.16650).
- Add additive contracts in `contracts/reference.py` near the existing compare
  contracts (`ReferenceComparePacketContract` at `:532`,
  `ReferenceCompareDiagnosticsContract` at `:557`), e.g.
  `ReferenceCompareGraphNodeDiffContract` and
  `ReferenceCompareGraphEdgeDiffContract`, plus a container
  `ReferenceCompareGraphDiffContract`. Follow the existing house style: bare
  `MCPContract` subclasses (`contracts/base.py`), `Literal` status enums, no raw
  coordinate fields.
- Add a matching optional graph-diff field on `VisionAssistContract`
  (`sampling/result_types.py:149-171`) so packet extraction can carry the typed
  diff additively next to `shape_mismatches` / `proportion_mismatches`
  (`:159-160`). `synthesize_packet_vision_result(...)`
  (`reference_compare_packets.py:1258`) must union node/edge diffs the same way
  it unions the string lists, deduping by node id / edge (from,to,kind).
- In `reference_planner.py`, extend `_relation_planner_blockers(...)` (`:300`),
  `_proportion_planner_blockers(...)` (`:368`), and the route selection
  `select_refinement_route(...)` (`:623`) so a `missing` node becomes a scope/part
  blocker and a `proportion_out_of_bounds` edge becomes a proportion blocker,
  reusing `ReferencePlannerBlockerContract` (`contracts/reference.py:619-628`).
- Confidence on edge diffs must be range-validated `[0,1]` (the repo already
  has the bug pattern of un-validated compare confidence; do not repeat it). Use
  `Field(ge=0.0, le=1.0)` as `ReferenceUnderstandingClassificationScoreContract`
  does (`contracts/reference.py:247`).

## Pseudocode

```python
# contracts/reference.py (additive)
class ReferenceCompareGraphNodeDiffContract(MCPContract):
    node_id: str                      # opaque registered object name / expected target_label
    role: str | None = None
    state: Literal["present", "missing", "unexpected"]
    summary: str | None = None

class ReferenceCompareGraphEdgeDiffContract(MCPContract):
    from_node: str
    to_node: str
    relation_kind: SceneRelationKindLiteral          # reuse fixed vocabulary
    expected_relation: ReferenceUnderstandingAttachmentRelationLiteral | None = None
    state: Literal["relation_match", "relation_mismatch", "proportion_out_of_bounds"]
    proportion_ratio: float | None = None            # PROPORTIONAL ratio vs trusted anchor, not absolute
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    summary: str | None = None

class ReferenceCompareGraphDiffContract(MCPContract):
    advisory_only: bool = True
    nodes: list[ReferenceCompareGraphNodeDiffContract] = []
    edges: list[ReferenceCompareGraphEdgeDiffContract] = []

# reference_planner.py
def graph_diff_blockers(graph_diff):
    blockers = []
    for node in graph_diff.nodes:
        if node.state == "missing":
            blockers.append(planner_blocker(category="scope", reason=f"expected part {node.node_id} absent"))
    for edge in graph_diff.edges:
        if edge.state == "proportion_out_of_bounds":
            blockers.append(planner_blocker(category="proportion", reason=f"{edge.from_node}->{edge.to_node} ratio drift"))
        elif edge.state == "relation_mismatch":
            blockers.append(planner_blocker(category="relation", reason=f"{edge.from_node}->{edge.to_node} {edge.relation_kind} mismatch"))
    return blockers
```

## Runtime / Security Contract Notes

- the graph diff is advisory VLM interpretation: it carries `advisory_only` and
  must not flip any gate or unlock any tool. Deterministic relation graph /
  assertion / silhouette remain the authority for the same node/edge identities.
- `proportion_ratio` is explicitly a ratio against a trusted reference anchor,
  never an authoritative absolute measurement (VLMs ~37% within 2x on metric
  tasks); the planner must treat it as a hint that triggers a deterministic
  re-check, not as a measured truth.
- edge `confidence` is range-validated `[0,1]` and non-authoritative
  (`confidence_is_non_authoritative`, `sampling/result_types.py:123`).
- do not add any coordinate fields to node/edge diffs; coordinates stay
  on-demand only and never primary evidence.

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_compare_packets.py` — assert a missing
  expected node surfaces as a `missing` node diff and an over-scaled edge surfaces
  as `proportion_out_of_bounds`; assert `synthesize_packet_vision_result(...)`
  unions node/edge diffs and still populates the legacy string fields
- `tests/unit/router/application/test_router_contracts.py` — assert the new
  graph-diff fields round-trip across the router contract boundary and remain
  optional/additive

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
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/router/application/test_router_contracts.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`

## Validation Category

- graph-vs-graph diff contract and relation-vocabulary proof
