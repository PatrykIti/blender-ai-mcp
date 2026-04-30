# TASK-157-02: Deterministic Gate Verifier And Status Model

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-157](./TASK-157_Goal_Derived_Quality_Gates_And_Deterministic_Verification.md)
**Category:** Guided Runtime / Gate Verification
**Estimated Effort:** Large

## Objective

Build the status model and verifier layer that evaluates normalized gates using
deterministic scene, spatial, mesh, assertion, and bounded reference evidence.

This layer must make evidence authority explicit. Perception outputs can
support a verifier only when the gate type allows that evidence class; they do
not become a generic substitute for Blender truth.

## Repository Touchpoints

| Path / Module | Expected Change |
|---------------|-----------------|
| `server/adapters/mcp/contracts/quality_gates.py` | Gate status, evidence, blocker, and verifier-result contracts |
| `server/adapters/mcp/contracts/reference.py` | Stable refs to silhouette/action-hint/segmentation/reference-understanding payloads |
| `server/application/services/spatial_graph.py` | Evidence source for relation/contact/seam gates |
| `server/adapters/mcp/areas/scene.py` | Reuse scene assertions and relation graph outputs |
| `server/adapters/mcp/areas/reference.py` | Attach verifier results to checkpoint/iterate payloads |
| `server/adapters/mcp/vision/` | Source of bounded perception evidence refs when a gate supports them |
| `server/adapters/mcp/session_capabilities.py` | Persist gate status and last verification versions |
| `tests/unit/adapters/mcp/test_quality_gate_verifier.py` | Gate status transition tests |
| `tests/unit/tools/scene/` | Evidence mapping tests for scene/spatial verdicts |

## Status Model

| Status | Meaning |
|--------|---------|
| `pending` | Gate exists but has not been checked against current scene truth |
| `blocked` | Required evidence or scope is missing |
| `passed` | Deterministic evidence satisfies the gate |
| `failed` | Deterministic evidence proves the gate is not satisfied |
| `waived` | User/server policy explicitly marks the gate not required |
| `stale` | Scene changed since the last successful check |

## Evidence Authority Model

Gate evidence should be typed and ranked by authority rather than collapsed
into one confidence score.

| Evidence Kind | Typical Gate Use | Authority |
|---------------|------------------|-----------|
| `scene_truth` / assertion output | `required_part`, `final_completion`, object existence, mode/scope checks | Authoritative when fresh |
| `spatial_relation` | `attachment_seam`, `support_contact`, pair seating, floating gap detection | Authoritative for spatial contact/support |
| `mesh_metric` | `opening_or_cut`, selected `shape_profile`, dimensions, topology/count checks | Authoritative when the metric directly measures the gate |
| `silhouette_analysis` | `shape_profile`, coarse `proportion_ratio`, visible contour drift | Bounded supporting evidence; must include scope/capture/reference ids |
| `part_segmentation` | Target part masks, region hints, future part-aware profile checks | Supporting evidence only; cannot prove Blender object existence/contact |
| `classification_score` | Domain/profile or construction-strategy selection | Routing/proposal evidence only; cannot pass gates |
| `reference_understanding` | Candidate gate plan, style, required details, construction path | Proposal evidence only; cannot pass gates |
| LLM prose | Rationale and client guidance | No verifier authority |

Unsupported or unavailable evidence sources should produce `blocked` with a
machine-readable reason when the gate requires that evidence. Optional
perception evidence may be absent without blocking gates that have an
authoritative scene/spatial/mesh verifier.

## Implementation Notes

- Verifiers should be small and gate-type specific.
- Verification must carry evidence references:
  - tool used
  - scope
  - scene/spatial version
  - measured value or verdict
  - failure reason
- A gate cannot become `passed` without evidence.
- A gate cannot become `passed` solely because a VLM, CLIP-style classifier, or
  reference-understanding summary says the target looks correct.
- `shape_profile` and selected `proportion_ratio` gates may use bounded
  perception evidence only when their normalized `verification_strategy`
  explicitly allows it and the evidence carries fresh capture/reference scope.
- A scene mutation should mark affected gate statuses `stale` or require
  re-check before final completion.
- Completion blockers should be derived from required gates in `failed`,
  `blocked`, `pending`, or `stale`.

## Pseudocode

```python
def verify_gate(gate, scene_context):
    verifier = verifier_registry.for_type(gate.gate_type)
    evidence = verifier.collect(gate, scene_context)

    if evidence.missing_scope:
        return GateStatusResult(status="blocked", reason="missing_scope")

    if verifier.passes(gate, evidence):
        return GateStatusResult(status="passed", evidence=evidence)

    return GateStatusResult(
        status="failed",
        evidence=evidence,
        correction_hint=verifier.recommend_correction(gate, evidence),
    )
```

## Tests To Add/Update

- Required gate without scope returns `blocked`.
- Required gate with stale scene version returns `stale`.
- Passed gate requires evidence payload.
- Perception-only completion claims remain `pending` or `failed` until a
  supported verifier evaluates concrete evidence.
- Unsupported required perception evidence returns `blocked` with an actionable
  reason instead of triggering an implicit SAM/CLIP call.
- Completion blocker aggregation includes `pending`, `blocked`, `failed`, and
  `stale` required gates.
- Optional failed gates do not block final completion but remain visible.

## E2E Tests

- Add in TASK-157-04 after first concrete verifier slices exist.

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
- `_docs/_TESTS/README.md`

## Acceptance Criteria

- Gate status is evidence-backed and persisted.
- Required gate blockers are machine-readable.
- Scene mutations can invalidate gate status.
- Checkpoint payloads expose gate status without relying on prose summaries.
