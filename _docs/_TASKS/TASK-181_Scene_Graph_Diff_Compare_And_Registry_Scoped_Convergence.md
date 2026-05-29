# TASK-181: Scene-Graph Diff Compare And Registry-Scoped Convergence

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Category:** Vision / Scene-Graph Compare
**Estimated Effort:** Extra Large
**Follow-on After:** [TASK-173](./TASK-173_Reference_Guided_Creature_Scope_Convergence_And_Optional_Grounding_Followups.md), [TASK-172](./TASK-172_Optional_Vision_Capability_Runtime_And_Localized_Perception.md), [TASK-171](./TASK-171_Creature_Attachment_First_Build_Contract_And_Structured_Vision_Handoff.md)
**Related:** [TASK-178](./TASK-178_Structured_Per_Finding_Compare_Schema.md), [TASK-180](./TASK-180_Set_Of_Mark_Object_Bound_Visual_Marks.md), [TASK-166](./TASK-166_Hierarchical_Reference_Compare_Perceived_Evidence_And_Budget_Control.md)

## Relationship To Existing Board Items

- `TASK-171` shipped the attachment-first creature contract and a
  registry-backed seam authority, but compare still treats the part registry as
  build bookkeeping rather than as the canonical comparison scope.
- `TASK-172` shipped the optional, default-off perception runtime (localization
  / segmentation sidecars) used additively inside `execute_compare_packets`.
  This family must consume that seam without reopening it and without reopening
  the `TASK-140-06` provider-capability substrate.
- `TASK-173` diagnosed the squirrel-session scope drift: packeted compare
  narrowed toward `Body + Head` (`_semantic_scope_label(...)` clustering in
  `reference_compare_packets.py:603-616` and `_scope_clusters_from_target_scope`
  at `:676-764`) while whole-assembly convergence lost precedence. `TASK-173`
  scopes patches to workset persistence and arbitration; this family removes the
  root cause by making the registered part graph the comparison scope itself.
- `TASK-166` established the hierarchical packet-compare and budget substrate
  this family extends; the new graph-diff evidence shape must stay within the
  same `VISION_MAX_IMAGES` packet budgeting (`resolve_complex_compare_policy` at
  `reference_compare_packets.py:783-807`).
- `TASK-178` (structured per-finding compare schema) and `TASK-180` (set-of-mark
  object-bound visual marks) are sibling vision-quality families; the
  relation-triplet serialization and graph-diff evidence here must stay
  compatible with their structured-finding and object-bound-mark posture and not
  contradict it.
- This umbrella is a STANDALONE family. It links the families above as
  upstream context via **Follow-on After** / **Related**, and its own subtasks
  use **Parent: TASK-181**.

## Objective

Make the guided part registry / `assembled_target_scope` a first-class scene
graph that is simultaneously the build state AND the canonical compare scope, so
that registering a part extends the comparison scope instead of letting compare
re-derive an ad-hoc scope by name heuristics. Emit compare as a graph-vs-graph
diff (per-node attribute mismatches and per-edge relation mismatches over a
fixed relation vocabulary), and serialize the active graph for the VLM as
per-object k-nearest relation triplets — symbolic relations plus proportional
ratios — rather than raw coordinates. The result is that compare can report a
missing part or a wrong part-to-part proportion against a known structure, and
whole-assembly convergence keeps precedence over narrowed appendage packets.

## Business Problem

The current staged compare has no inventory of expected parts, no relationship
model, and no expected-relation set:

- `build_compare_packets(...)` (`reference_compare_packets.py:1016`) re-derives
  scope from name heuristics (`_is_head_like`, `_is_body_like`, etc., at
  `:571-600`) and clusters into hardcoded labels such as `Body + Head`, `Tail`,
  `Ears` (`_semantic_scope_label` at `:603-616`; `_scope_clusters_from_target_scope`
  at `:676-764`). Because scope is ad-hoc rather than the registered part graph,
  the squirrel session drifted to `Body + Head` and whole-assembly convergence
  lost precedence — exactly the regression `TASK-173` documented.
- The compare evidence shape is a bag of bare strings: `VisionAssistContract`
  carries `shape_mismatches: list[str]`, `proportion_mismatches: list[str]`,
  `correction_focus: list[str]` (`sampling/result_types.py:159-161`), and the
  packet prompt asks the VLM only for those flat string lists
  (`prompting.py:704-731`). There is no typed concept of "node X is missing" or
  "edge X->Y has a wrong proportion ratio".
- The reference-understanding pass already produces rich per-part semantics —
  `mass_recipe`, `attachment_plan`, `contact_expectations`, `part_order`
  (`contracts/reference.py:280-286`; serialized in `reference_understanding.py`
  around `:176-258`) — but the compare loop never turns them into an expected
  graph, so it cannot detect a missing part or a violated expected relation.
- `guided_register_part(...)` already widens the active scope additively
  (`session_capabilities_registry.py:182-211` `_maybe_expand_active_target_scope_dict`
  and `:214-273` `register_guided_part_role_async`), but compare does not treat
  that widened scope as authoritative; the heuristic clustering can still shrink
  it back to `Body + Head`.
- The deterministic relation substrate already exists: a fixed relation
  vocabulary `SceneRelationKindLiteral = contact | gap | overlap | alignment |
  attachment | support | symmetry` (`contracts/scene.py:22`) plus a typed
  relation graph (`SceneRelationGraphPairContract` at `contracts/scene.py:249`).
  Compare evidence does not reuse this graph, so VLM prose and deterministic
  truth never line up on the same node/edge identities.

The net effect: compare cannot say "the snout part is missing" or "the head is
twice too large relative to the body", and the loop drifts away from
whole-assembly convergence.

Published scene-understanding work motivates the chosen evidence shape, but the
benchmarks below are indoor-scan / synthetic, not Blender-vs-reference. Treat
their absolute numbers as direction only, and re-measure on
`tests/fixtures/vision_eval` golden fixtures before any promotion:

- SceneVerse (arXiv:2401.09340) — a fixed relation taxonomy for 3D scene graphs.
- 3DGraphLLM (arXiv:2412.18450) — relation triplets help and raw coordinates
  hurt (reported 50.1 -> 42.6 when coordinates are injected).
- Text-Scene (arXiv:2509.16721) — symbolic relations 59.4 vs raw coordinates
  18.4 for spatial reasoning.
- SceneCraft (arXiv:2403.01248) — scene-graph blueprint for layout.
- ConceptGraphs (arXiv:2309.16650) — multi-view fusion into an object graph.

## Business Outcome

After this umbrella lands:

- the registered part graph is the single source of compare scope; registering
  a part extends the comparison scope and whole-assembly convergence keeps
  precedence over any narrowed appendage packet
- compare can report a missing expected part (graph node absent) and a wrong
  part-to-part proportion (graph edge ratio out of bounds) against the
  reference-understanding-derived expected graph
- compare evidence is a typed graph-vs-graph diff (per-node attribute deltas,
  per-edge relation mismatches) rather than only bare string lists, while the
  legacy string fields remain populated for backward compatibility
- the VLM prompt is scoped to the current graph nodes plus declared expected
  relations and serialized as per-object k-nearest relation triplets with
  proportional ratios, never raw coordinate tokens
- the squirrel proof lane demonstrates compare scope no longer collapses to
  `Body + Head` and that a deliberately missing/over-scaled part is reported as
  a node/edge diff

## Non-Goals

- Vision stays ADVISORY. The new graph-diff fields are still VLM interpretation
  and must keep `not_truth_source` / `requires_deterministic_checks_for_correctness`
  (`VisionBoundaryPolicyContract` at `sampling/result_types.py:115-123`).
  Deterministic inspection / assertion / silhouette own scene truth. Vision must
  not mark gates complete or unlock tools.
- Magnitudes in the graph diff are PROPORTIONAL RATIOS against a trusted
  reference anchor, never authoritative absolute measurements (VLMs are right
  only ~37% within 2x on metric tasks). Absolute dimensions remain the job of
  deterministic measurement / assertion seams.
- Heavier perception sidecars (SAM / SAM2 / GroundingDINO / Depth-Anything /
  CLIP / DINO embeddings) stay DEFAULT-OFF, advisory-only, and packet-bounded
  per the `TASK-172` optional-runtime seam. Do not reopen the `TASK-140-06`
  provider-capability substrate.
- Do not emit raw coordinate tokens as primary evidence; prefer symbolic
  relations plus proportional ratios, with coordinates only on explicit demand.
- Do not add VLM-side chain-of-thought for spatial judgments (VSI-Bench
  regression -1..-21%); reasoning stays in the orchestrator.
- Do not replace bounded packet compare with a mandatory full-scene heavy pass,
  and do not weaken `spatial_refresh_required` or visibility gating.
- No squirrel-only logic: the graph contract is generic over creatures,
  hard-surface, and architectural scopes.

## Execution Structure

| Order | Task | Purpose |
|------|------|---------|
| 1 | [TASK-181-01](./TASK-181-01_Part_Registry_As_First_Class_Scene_Graph_And_Compare_Scope.md) | Part Registry As First-Class Scene Graph And Compare Scope |
| 2 | [TASK-181-02](./TASK-181-02_Graph_Vs_Graph_Diff_Contract_And_Relation_Vocabulary.md) | Graph-Vs-Graph Diff Contract And Relation Vocabulary |
| 3 | [TASK-181-03](./TASK-181-03_K_Nearest_Relation_Triplet_Prompt_Serialization.md) | K-Nearest Relation-Triplet Prompt Serialization |
| 4 | [TASK-181-04](./TASK-181-04_Scene_Graph_Scope_Drift_Regression_Proof_Lane.md) | Scene-Graph Scope-Drift Regression Proof Lane |

## Repository Touchpoints

| Path / Module | Expected Ownership | Why It Is In Scope |
|---------------|--------------------|--------------------|
| `server/adapters/mcp/areas/reference_compare_packets.py` | packet planner / scope clustering / packet execution | `build_compare_packets` (`:1016`), `_scope_clusters_from_target_scope` (`:676-764`), `_semantic_scope_label` (`:603-616`), and `execute_compare_packets` (`:1788`) must consume the registered graph instead of re-deriving scope by name heuristics |
| `server/adapters/mcp/session_capabilities_registry.py` | guided part registry and active-scope widening | `register_guided_part_role(_async)` (`:214`/`:276`) and `_maybe_expand_active_target_scope_dict` (`:182-211`) must promote the registry to a typed graph that is the canonical compare scope |
| `server/adapters/mcp/contracts/reference.py` | public compare/diagnostics contracts | the graph-vs-graph diff (nodes/edges) lands as additive fields on `ReferenceCompareDiagnosticsContract` (`:557`) / `ReferenceComparePacketContract` (`:532`) without breaking the existing string fields |
| `server/adapters/mcp/contracts/vision.py` | capture bundle scope contract | `VisionCaptureBundleContract.assembled_target_scope` (`:31`) carries the scope; the graph projection must travel with the same bundle without leaking coordinates |
| `server/adapters/mcp/contracts/scene.py` | deterministic relation vocabulary | reuse `SceneRelationKindLiteral` (`:22`) and `SceneRelationGraphPairContract` (`:249`) as the fixed relation vocabulary; do not invent a parallel taxonomy |
| `server/adapters/mcp/areas/reference_planner.py` | correction-candidate planner | `select_refinement_route` (`:623`) and relation/proportion blockers (`:300`/`:368`) must map graph-diff nodes/edges into existing typed planner blockers |
| `server/adapters/mcp/areas/reference_understanding.py` | expected-graph source | `mass_recipe` / `attachment_plan` / `contact_expectations` / `part_order` (`:176-258`) become the expected node/edge set the diff is measured against |
| `server/adapters/mcp/vision/prompting.py` | packet prompt serialization | `build_vision_payload_text` packet path (`:620-732`) must emit per-object k-nearest relation triplets scoped to graph nodes, never raw coordinates |
| `server/adapters/mcp/sampling/result_types.py` | vision result envelope | additive graph-diff fields on `VisionAssistContract` (`:149`) alongside the existing `shape_mismatches` / `proportion_mismatches` lists |
| `tests/unit/adapters/mcp/`, `tests/unit/router/application/`, `tests/e2e/vision/`, `tests/fixtures/vision_eval/`, `scripts/vision_harness.py` | proof lanes and harness | the regression came from a real guided creature session; the fix must prove graph-scoped compare and a missing/over-scaled-part diff on repo-owned fixtures |
| `_docs/_VISION/README.md`, `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`, `_docs/_TASKS/README.md` | canonical docs | docs must describe the graph-diff evidence shape, the registry-as-compare-scope rule, and the relation-triplet serialization posture |

## Test Matrix

| Slice | Primary Validation Lane | Why |
|------|--------------------------|-----|
| registry-as-compare-scope | `tests/unit/adapters/mcp/test_reference_compare_packets.py`, `tests/unit/adapters/mcp/test_guided_flow_state_contract.py` | proves registering a part extends compare scope and whole-assembly precedence holds instead of drifting to `Body + Head` |
| graph-vs-graph diff contract | `tests/unit/adapters/mcp/test_reference_compare_packets.py`, `tests/unit/router/application/test_router_contracts.py` | proves node/edge diff fields serialize additively and round-trip across the router contract boundary |
| relation-triplet prompt serialization | `tests/fixtures/vision_eval/`, `tests/unit/adapters/mcp/test_reference_compare_packets.py` | proves the packet payload emits k-nearest relation triplets with proportional ratios and no raw coordinate tokens |
| scope-drift regression proof | `tests/e2e/vision/test_reference_guided_squirrel_quality_regression.py` | proves compare scope no longer collapses to `Body + Head` and a deliberately missing/over-scaled part is reported as a node/edge diff |

## Acceptance Criteria

- registering a part via `guided_register_part(...)` extends the canonical
  compare scope, and `build_compare_packets(...)` derives packets from that
  registered graph rather than from name heuristics
- whole-assembly graph convergence keeps precedence: the assembled graph cannot
  be silently replaced by a `Body + Head`-only scope unless a later packet
  contract explicitly narrows it
- compare emits a typed graph-vs-graph diff that can report a missing expected
  node (part) and an out-of-bounds expected edge ratio (proportion), while the
  legacy `shape_mismatches` / `proportion_mismatches` string fields stay
  populated
- the packet prompt for the active graph is serialized as per-object k-nearest
  relation triplets with proportional ratios and contains no raw coordinate
  tokens as primary evidence
- the new graph-diff fields keep `advisory_only` / `not_truth_source` /
  `requires_deterministic_checks_for_correctness` and do not unlock tools or
  pass gates
- RE-MEASUREMENT CAVEAT: the cited SceneVerse / 3DGraphLLM / Text-Scene /
  SceneCraft / ConceptGraphs benchmarks are indoor-scan / synthetic, NOT
  Blender-vs-reference; absolute compare-quality gains must be re-measured on
  `tests/fixtures/vision_eval` golden fixtures before any promotion

## Docs To Update

- `_docs/_TASKS/README.md`
- `_docs/_VISION/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`

## Tests To Add/Update

- split across the execution slices below; each child task owns its exact lane

## Changelog Impact

- planning-only now; add a `_docs/_CHANGELOG/*` entry when the first slice lands
- do not treat this planning-only task creation as the changelog event

## Status / Board Update

- `_docs/_TASKS/README.md` should track `TASK-181` as an open item on the
  Vision / Hybrid Loop lane (board update owned by the coordinator)
- child tasks stay nested under the open umbrella and do not need board rows
  unless one later becomes a separately promoted follow-on

## Validation Commands

- `git diff --check`
- `rg -n "TASK-181|Scene-Graph Diff Compare And Registry-Scoped Convergence|Part Registry As First-Class Scene Graph|Graph-Vs-Graph Diff Contract|K-Nearest Relation-Triplet|Scene-Graph Scope-Drift Regression" _docs/_TASKS/TASK-181*.md`

## Validation Category

- planning / governance / task-family definition
