# TASK-158-05: Optional Perception Adapter Readiness And Eval Harness

**Status:** ⏳ To Do
**Priority:** 🟠 High
**Parent:** [TASK-158](./TASK-158_Vision_And_Creature_Gate_Boundary_Doc_Alignment.md)
**Category:** Vision / Optional Perception Readiness
**Estimated Effort:** Medium

## Objective

Add the post-`TASK-157` readiness layer for optional perception evidence that
was intentionally excluded from the first quality-gate substrate: default-off
adapter contracts, deterministic fixture/eval harness support, and clear
provider/runtime boundaries for CLIP/SigLIP-style classification,
SAM/segmentation sidecars, and related part-localization sketches.

This slice is not a mandate to ship heavy adapters by default. It creates the
safe extension shape so future adapters can produce bounded proposal/support
records without becoming verifier truth.

## Repository Touchpoints

| Path / Module | Expected Change |
|---------------|-----------------|
| `server/adapters/mcp/vision/` | Optional adapter protocol/registry and no-op/default-off behavior |
| `server/adapters/mcp/contracts/quality_gates.py` | Reuse `TASK-157` proposal/support evidence refs; do not add new pass/fail authority |
| `server/adapters/mcp/contracts/reference.py` | Carry optional classification/mask support refs only when configured and present |
| `server/infrastructure/config.py` | Add explicit default-off config only if adapter readiness needs config flags |
| `tests/fixtures/reference_understanding/` | Golden fixture directories for reference-understanding and optional evidence scoring |
| `tests/unit/adapters/mcp/` | Adapter registry, default-off, fixture parsing, and evidence-boundary tests |
| `scripts/vision_harness.py` | Add reference-understanding/eval mode only if it can run without live provider calls by default |
| `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md` | Document what is ready now vs deferred adapter implementation |

## Implementation Notes

- CLIP/SigLIP-style classification, SAM/segmentation sidecars, Grounding DINO,
  OWL-ViT, and similar adapters must be default-off.
- Missing optional adapters must return unavailable/default-off diagnostics, not
  errors that break guided/reference flow.
- No model downloads, provider calls, or local sidecar startups may happen
  implicitly during verifier evaluation or reference checkpoint calls.
- Optional adapter output may include:
  - `classification_scores`
  - `segmentation_artifacts`
  - `part_localization_candidates`
  - fixture/eval diagnostics
- Optional adapter output may select a construction-path candidate, challenge a
  VLM suggestion, or provide support refs, but it must not prove object
  existence, attachment, contact, proportions, or final completion.
- Future concrete adapter implementation should be split into follow-on leaves
  if it requires new dependencies, model downloads, service startup, or external
  provider credentials.

## Pseudocode

```python
adapter = optional_perception_registry.get("clip_siglip")
if not adapter.enabled:
    return OptionalEvidence.unavailable(reason="default_off")

scores = adapter.classify(reference_image, labels=allowed_labels)
return OptionalEvidence(
    evidence_type="classification_scores",
    status="support_only",
    scores=scores,
    can_pass_gate=False,
)
```

## Runtime / Security Contract Notes

- Visibility level: internal/support evidence only unless a later public surface
  explicitly exposes diagnostics.
- Read-only behavior: optional adapter readiness must not mutate Blender scene
  state or guided gate status directly.
- Session/auth assumptions: fixture/eval output and optional evidence refs stay
  scoped to the active MCP session.
- Provider/key handling: do not store provider keys, local private paths, image
  bytes, or raw masks in client-facing logs.
- Resource limits: adapters must have explicit timeout/resource limits before
  they can be enabled.
- Dependency policy: no new heavy dependency is introduced without a dedicated
  task note and validation plan.

## Tests To Add / Update

- Unit tests that optional adapters are default-off and unavailable diagnostics
  are non-fatal.
- Unit tests that `classification_scores` and `segmentation_artifacts` cannot
  set gate status to `passed`.
- Fixture tests for `tests/fixtures/reference_understanding/*/golden.json`.
- Harness tests only if `scripts/vision_harness.py` gets a providerless
  reference-understanding/eval mode.

## Docs To Update

- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
- `_docs/_MCP_SERVER/README.md` if support evidence appears in client-facing
  payloads.
- `_docs/_TESTS/README.md` if new fixture or harness structure is introduced.
- `_docs/_TASKS/TASK-158_Vision_And_Creature_Gate_Boundary_Doc_Alignment.md`
  completion summary.

## Changelog Impact

- Roll this slice into the single
  `_docs/_CHANGELOG/279-...task-158-...completion.md` entry created during
  `TASK-158-03` closeout.

## Validation Commands

- `git diff --check`
- Focused unit tests for optional adapter registry/config once files exist.
- Fixture/harness command if `scripts/vision_harness.py` gains a providerless
  reference-understanding/eval mode.
- `rg -n "can_pass_gate=True|status=\\\"passed\\\"|model download|provider key" server/adapters/mcp/vision tests/unit/adapters/mcp scripts/vision_harness.py`

## Acceptance Criteria

- Optional perception adapters are default-off and non-fatal when unavailable.
- Optional evidence can support or challenge proposals but cannot pass gates.
- No implicit SAM/CLIP/SigLIP/Grounding DINO/OWL-ViT runtime activation occurs.
- Golden fixtures document expected support evidence shape without requiring a
  live provider.
- Any future heavy adapter implementation is clearly deferred to its own
  follow-on task unless explicitly implemented and validated here.
