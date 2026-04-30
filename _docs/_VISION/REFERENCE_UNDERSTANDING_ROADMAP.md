# Reference Understanding Roadmap

This document defines the repo-facing development direction for pre-build
reference understanding in the Vision layer.

The long-form research note
[`_docs/blender-ai-mcp-vision-reference-understanding-plan.md`](../blender-ai-mcp-vision-reference-understanding-plan.md)
is useful strategy input, but it is not itself the implementation contract. This
document is the shorter normative bridge between that strategy, the current
Vision runtime, and the task families that should implement it.

When the long-form plan names draft families or tools that are absent from the
current MCP surface and router metadata, treat them as strategy aliases or
future candidates and normalize them through this roadmap before implementation.

## Problem

The current reference-guided loop is strongest after a scene already exists:
stage compare, iterate, silhouette metrics, action hints, truth follow-up,
repair candidates, and the `TASK-145` repair-planner handoff can all describe
what is wrong with the current build.

The remaining gap is earlier:

1. A user attaches references.
2. The LLM starts building before the system has classified the reference.
3. The first build path may choose smooth primitives or sculpt-like thinking
   even when the reference clearly calls for faceted low-poly construction.
4. Later vision feedback then has to correct a path choice that should have
   been avoided before the first object was created.

Reference understanding closes that gap by producing a typed pre-build summary:

- what the references depict
- which style and construction path they imply
- which parts and non-goals matter
- which tool families are suitable
- which verification gates should exist later

## Owner Boundaries

Reference understanding must preserve the existing responsibility split.

| Layer | Responsibility |
|-------|----------------|
| Vision / perception | Describe references, extract bounded evidence, propose construction path and gate candidates |
| Router / guided policy | Normalize proposals, apply safety policy, choose visibility and stage cadence |
| Quality-gate verifier | Decide gate status from typed evidence and authoritative scene/spatial/mesh/assertion checks |
| LLM orchestrator | Execute within the visible bounded surface and consume checkpoint feedback |
| FastMCP surface | Expose a stable contract without creating parallel discovery or visibility paths |

Hard rules:

- Vision output is advisory.
- Vision must not mark gates complete.
- Vision must not directly unlock tools.
- `vision_contract_profile` remains prompt/schema/parser routing metadata, not
  gate evidence by itself.
- SAM, CLIP, SigLIP, Grounding DINO, or similar heavier perception modules are
  optional future adapters, not the MVP baseline.
- If a perception source is unavailable, the runtime returns a typed blocked or
  unavailable status instead of silently pretending evidence exists.

## Relationship To Current Tasks

| Task | Role |
|------|------|
| `TASK-157` | Generic gate substrate: proposal sources, evidence refs, verifier authority, status model, guided cadence |
| `TASK-135` | First creature consumer of the gate substrate |
| `TASK-135-03` | First low-poly form-refinement consumer; owns the faceted refinement stage and any creature profile macros |
| `TASK-140` | External VLM model-family profile reliability; owns `vision_contract_profile` expansion, not quality-gate authority |

When `TASK-140` payloads are later consumed by `TASK-157`, treat
`vision_contract_profile` as routing/provenance context only. Parsed diagnostic
or compare payload fields may become proposal/support refs, but the quality
gate verifier still owns pass/fail status.

Do not create a second task family that duplicates these owners. New work should
land as leaves under the nearest existing task unless a separate future adapter
really needs its own task family.

## Target Flow

The intended reference-guided flow is:

```text
router_set_goal(...)
  ↓
reference_images(action="attach", ...)
  ↓
reference understanding pass
  ↓
server normalizes understanding into active strategy and gate proposals
  ↓
guided blockout / modeling / mesh / material stages
  ↓
reference_compare_stage_checkpoint(...)
  ↓
reference_iterate_stage_checkpoint(...)
  ↓
gate verifier and repair planner select bounded next actions
```

The "reference understanding pass" may be exposed as an action on the existing
reference surface or as a focused MCP tool only if the public-surface review
justifies it. It must not introduce a public `router_apply_reference_strategy`
tool. Applying the strategy is server-owned guided state, visibility, and gate
policy work.

## Reference Understanding Contract

The first contract should be typed, bounded, and source-aware. It may live in a
dedicated `server/adapters/mcp/contracts/reference_understanding.py` file if the
current `reference.py` surface would become too large, but it should reuse the
existing reference/vision payload types where possible.

Minimum fields:

| Field | Purpose |
|-------|---------|
| `understanding_id` | Stable id for the reference-understanding result |
| `goal` / `goal_id` | Active guided goal used for the pass |
| `reference_ids` | Reference images included in the pass |
| `subject` | Label, category, confidence, and uncertainty notes |
| `style` | Controlled style classification such as `low_poly_faceted` |
| `views` | Detected reference views and key visual features |
| `required_parts` | Candidate required parts with construction hints and source refs |
| `non_goals` | Explicit things the build should avoid |
| `construction_strategy` | Controlled `construction_path`, stage sequence, and finish policy |
| `router_handoff_hints` | Advisory families and constraints for guided policy normalization |
| `gate_proposals` | Candidate `TASK-157` gate declarations, all initially advisory/pending |
| `visual_evidence_refs` | Links to silhouette/CV/reference evidence payloads, not embedded blobs |
| `classification_scores` | Optional future CLIP/SigLIP-style scores |
| `segmentation_artifacts` | Optional future sidecar mask/crop refs |
| `verification_requirements` | Suggested checks that the gate normalizer may convert to typed gates |
| `boundary_policy` | Explicit advisory/truth/tool-unlock limits |

The contract should carry provenance for each important statement. A low-poly
squirrel example may say "tail should be a curled segmented chain", but that
statement should be tied to reference ids, view ids, or a model/provider
provenance record.

## Controlled Vocabulary

Start with a small vocabulary. Avoid adding free-form tool or workflow names
that the server cannot normalize.

Suggested `construction_path` values:

| Value | Meaning |
|-------|---------|
| `low_poly_facet` | Faceted low-poly object or creature construction |
| `hard_surface` | Product, prop, mechanical, or CAD-like shape |
| `organic_sculpt` | Soft organic shape where bounded local sculpt may be primary |
| `creature_blockout` | Generic assembled creature blockout without a stronger style cue |
| `dental_surface` | Dental visualization/mockup support, with explicit medical guardrails |
| `architectural_mass` | Building/facade/massing reference |
| `unknown` | Insufficient confidence; fall back to inspect-safe behavior |

Current canonical refinement families are:

- `macro`
- `modeling_mesh`
- `sculpt_region`
- `inspect_only`

These are reference-planner refinement families, not the full guided
visibility vocabulary. When implementing guided visibility, translate planner
families into current `GuidedFlowFamilyLiteral` values and concrete tool names:
for example `modeling_mesh` usually materializes through `secondary_parts`
mesh/modeling tools, while attachment repair uses `attachment_alignment`.
Do not invent intermediate guided families such as `macro_profile`,
`macro_attachment`, or `inspect_assert` unless the typed guided-flow contract
is deliberately expanded.

The strategic plan mentions `mesh_edit` and `material_finish`. In current repo
contracts those names are non-normative strategy aliases or future concepts and
should not become new planner families by default:

- `mesh_edit` maps to `modeling_mesh`
- `material_finish` should be modeled as a stage, action hint, or future family
  only after a dedicated contract change
- `mesh_shade_flat`, `macro_low_poly_finish`,
  `macro_low_poly_facet_refine`, and similar `macro_low_poly_*` names remain
  proposed `TASK-135-03`/follow-on candidates until they exist in the MCP
  surface and router metadata
- Long-form examples that list those names as allowed tools are illustrative
  strategy sketches, not a current implementation contract.

## Construction Path Policy

The router/guided policy layer should normalize the advisory
`construction_path` into allowed families and next-stage guidance.

Initial policy:

| Construction Path | Primary Family | Allowed Families | Default Sculpt Policy |
|-------------------|----------------|------------------|-----------------------|
| `low_poly_facet` | `modeling_mesh` | `macro`, `modeling_mesh`, `inspect_only` | `local_detail_only`, hidden until prerequisites pass |
| `hard_surface` | `modeling_mesh` | `macro`, `modeling_mesh`, `inspect_only` | forbidden by default |
| `organic_sculpt` | `sculpt_region` when preconditions pass | `macro`, `modeling_mesh`, `sculpt_region`, `inspect_only` | allowed or primary only through bounded handoff |
| `creature_blockout` | `macro` | `macro`, `modeling_mesh`, `inspect_only` | allowed after blockout only when planner preconditions pass |
| `dental_surface` | `inspect_only` or `modeling_mesh` | `inspect_only`, `modeling_mesh` | local-only, no clinical authority |
| `architectural_mass` | `modeling_mesh` | `macro`, `modeling_mesh`, `inspect_only` | forbidden by default |
| `unknown` | `inspect_only` | `inspect_only`, possibly safe `macro` | hidden |

This policy must remain subordinate to active gate status. For example, a
`shape_profile` gate should not open mesh refinement while required seam gates
still fail.

## MVP Scope

The MVP should solve the orchestration problem without adding heavy model
dependencies.

Include:

- typed `ReferenceUnderstandingContract`
- prompt/schema/parser path using the existing VLM backend
- no-reference and no-backend blocked/readiness responses
- construction-path policy normalized into guided state and visibility
- gate-proposal output that feeds `TASK-157` as advisory/pending gates
- low-poly squirrel golden scenario proving `low_poly_facet` chooses
  `modeling_mesh` or `macro`, not `sculpt_region` as primary
- docs and unit coverage for boundary rules

Do not include in the MVP:

- SAM or part-segmentation runtime
- CLIP/SigLIP runtime
- Grounding DINO / OWL-ViT
- new provider/transport branches
- new public router strategy tools
- clinical/dental correctness claims

Runtime defaults should stay safe:

- optional sidecars default off
- external calls require the existing vision backend configuration
- missing or disabled reference understanding must not break normal guided
  sessions

## Later Adapters

Later adapters should plug into the same contract rather than changing the
orchestration model.

| Phase | Adapter | Output |
|-------|---------|--------|
| 2 | Pillow/numpy plus optional OpenCV/scikit-image | `visual_evidence_refs`, edge/facet/color/silhouette metrics |
| 3 | CLIP/SigLIP | `classification_scores` that support or challenge VLM construction-path choice |
| 4 | SAM or segmentation sidecar | `segmentation_artifacts` with masks/crops, advisory only |
| 5 | Grounding DINO / OWL-ViT style localization | optional text-prompted boxes that can seed segmentation masks |

All later adapters must be typed, bounded, reproducible, optional, and
unavailable-by-default until their own task promotes them.

## Low-Poly Creature Consumer

For the low-poly squirrel class of failures, the desired behavior is:

1. reference understanding classifies the style as `low_poly_faceted`
2. strategy normalization selects `low_poly_facet`
3. guided policy keeps sculpt hidden as a primary path
4. blockout creates required masses and detail placeholders
5. seam/contact gates are verified or repaired
6. `TASK-135-03` opens a bounded low-poly form-refinement stage
7. mesh/modeling/profile tools or optional creature macros make facets,
   wedges, segment chains, and flat-shaded forms visible
8. only after those prerequisites can local deterministic sculpt be recommended
   for small details through the `TASK-145` planner handoff

The first implementation should not treat `mesh_shade_flat`,
`macro_low_poly_finish`, `macro_low_poly_facet_refine`, or similar names as
already shipped tools unless they exist in the MCP surface and router metadata.
Until then, they are proposed future tools/macros owned by `TASK-135-03` or a
dedicated follow-on leaf.

## Suggested File Ownership

Likely implementation touchpoints:

| Area | Likely Files |
|------|--------------|
| Contracts | `server/adapters/mcp/contracts/reference_understanding.py` or `reference.py` |
| Vision prompt/parser | `server/adapters/mcp/vision/reference_understanding.py`, `reference_understanding_prompt.py`, `reference_understanding_parser.py` |
| Reference surface | `server/adapters/mcp/areas/reference.py` first; split later only if needed |
| Guided state | `server/adapters/mcp/session_capabilities.py`, guided flow contracts |
| Visibility/search | `server/adapters/mcp/transforms/visibility_policy.py`, `server/adapters/mcp/discovery/search_documents.py` |
| Gate integration | `server/adapters/mcp/contracts/quality_gates.py` once `TASK-157` introduces it |
| Tests | focused unit tests under `tests/unit/adapters/mcp/` plus golden fixtures |
| Docs | `_docs/_VISION/README.md`, `_docs/_MCP_SERVER/README.md`, `_docs/_PROMPTS/`, task closeout docs |

Do not place router policy under a non-existent `server/adapters/mcp/router/`
package. Use the current adapter/guided-state seams or the actual
`server/router/` package when the policy belongs to the router layer.

## Test And Evaluation Plan

Minimum unit tests:

- contract accepts controlled vocabulary and rejects unknown status/tool claims
- parser repairs common JSON drift without accepting invented tool names
- `low_poly_facet` maps to `modeling_mesh` / `macro` and not primary
  `sculpt_region`
- `hard_surface` keeps sculpt hidden by default
- `organic_sculpt` can expose `sculpt_region` only when policy and
  preconditions allow it
- no references returns a readiness-style blocked result
- no configured vision backend returns a typed unavailable/blocked result
- gate proposals from reference understanding normalize to pending gates

Golden scenarios:

- low-poly squirrel front/side
- smooth organic creature
- hard-surface product
- architectural facade
- dental crown mockup with visualization-only guardrails

The harness score should include:

- subject/category match
- style match
- construction path match
- primary family match
- sculpt policy match
- required-parts recall
- non-goal coverage
- invented-tool rejection
- boundary-policy correctness

## Acceptance Criteria

The roadmap is satisfied when:

- attached references can be understood before the first build stage
- the result is a typed contract with explicit boundary policy
- the server normalizes understanding into guided state, gate proposals, and
  bounded visibility without trusting Vision as truth
- low-poly references produce `low_poly_facet` with `modeling_mesh` or `macro`
  as the primary path
- sculpt remains hidden as a default path for low-poly and hard-surface
  references
- missing optional perception adapters do not break guided sessions
- stage compare and iterate continue to use existing payloads and planner
  handoffs after the build starts

## Open Decisions

- Whether the first public surface is an action on `reference_images(...)`, a
  new `reference_understand(...)` tool, or an internal automatic pass surfaced
  through `router_get_status()` and checkpoint payloads.
- Whether `material_finish` deserves a new canonical planner family or should
  stay a stage/action-hint concept.
- Whether `ReferenceUnderstandingContract` lives in a separate file immediately
  or starts inside `reference.py` and is split later.
- Which existing VLM backend should be the first harness-ranked default for
  reference understanding, since compare-loop strength does not automatically
  prove pre-build understanding quality.
