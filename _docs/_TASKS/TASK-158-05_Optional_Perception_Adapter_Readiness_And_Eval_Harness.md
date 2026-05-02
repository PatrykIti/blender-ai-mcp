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
| `server/adapters/mcp/vision/config.py` | Extend typed optional sidecar/adapter config only through the existing vision runtime contract |
| `server/adapters/mcp/vision/runtime.py` | Keep optional perception lazy, default-off, and aligned with the shipped segmentation-sidecar opt-in seam |
| `server/adapters/mcp/vision/evaluation.py` | Extend fixture/eval scoring only if optional-evidence diagnostics become first-class scored output |
| `server/adapters/mcp/contracts/quality_gates.py` | Reuse `TASK-157` proposal/support evidence refs; do not add new pass/fail authority |
| `server/adapters/mcp/contracts/reference.py` | Preserve declared support envelopes and add any new client-facing optional-evidence contracts explicitly |
| `server/adapters/mcp/areas/reference.py` | Keep top-level and compact-iterate `part_segmentation` envelope behavior aligned with the shipped compare/iterate surface |
| `server/infrastructure/config.py` | Extend the current `VISION_SEGMENTATION_*` opt-in surface first; do not create a parallel flag family for the same readiness path |
| `tests/fixtures/vision_eval/` | Reuse the existing golden fixture tree for reference-understanding and optional evidence scoring |
| `tests/unit/adapters/mcp/test_vision_runtime_config.py` | Validate default-off config and typed runtime opt-in behavior |
| `tests/unit/adapters/mcp/test_reference_images.py` | Keep compare/iterate envelopes and compact-iterate behavior aligned |
| `tests/unit/adapters/mcp/test_vision_evaluation.py` | Verify optional-evidence fixture scoring only if evaluation schema expands |
| `scripts/vision_harness.py` | Add a providerless fixture/eval mode only as an explicit opt-in path; keep the current default backend-executing flow unchanged |
| `tests/unit/scripts/test_script_tooling.py` | Keep harness CLI semantics and default backend-executing flow unchanged |
| `tests/e2e/vision/test_reference_stage_silhouette_contract.py` | Preserve disabled/unavailable compare/iterate optional-evidence envelopes |
| `tests/e2e/integration/test_guided_surface_contract_parity.py` | Run when optional evidence becomes client-facing on stdio or Streamable HTTP compare/iterate payloads |
| `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md` | Document what is ready now vs deferred adapter implementation |

## Implementation Notes

- CLIP/SigLIP-style classification, SAM/segmentation sidecars, Grounding DINO,
  OWL-ViT, and similar adapters must be default-off.
- Missing optional adapters must return unavailable/default-off diagnostics, not
  errors that break guided/reference flow.
- No model downloads, provider calls, or local sidecar startups may happen
  implicitly during verifier evaluation or reference checkpoint calls.
- The current compare/iterate surface already returns explicit
  `part_segmentation` envelopes in `disabled` or `unavailable` states. Extend
  that explicit support-only envelope pattern in
  `server/adapters/mcp/areas/reference.py`; do not switch the contract to
  presence-only behavior or break the compact-iterate reset path.
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
- Reuse the shipped segmentation-sidecar config/runtime seam first:
  `VISION_SEGMENTATION_*` in `server/infrastructure/config.py`,
  `VisionSegmentationSidecarConfig` in `server/adapters/mcp/vision/config.py`,
  and `build_vision_runtime_config(...)` in `server/adapters/mcp/vision/runtime.py`.
  Do not invent a second default-off registry/flag path for the same readiness
  concern.
- The current `scripts/vision_harness.py` default path is live-backend-capable
  and `--backend` defaults to `all`. Any providerless fixture mode introduced by
  this task must be an explicit opt-in path or helper; it must not silently
  change `_run_backend()` / `_run()` or the default CLI semantics.

## Pseudocode

```python
runtime = build_vision_runtime_config(config)
sidecar = runtime.active_segmentation_sidecar
if sidecar is None or not sidecar.enabled:
    return ReferencePartSegmentationContract(
        status="disabled",
        advisory_only=True,
        notes=["Optional perception remains default-off on the current runtime."],
    )

return ReferencePartSegmentationContract(
    status="unavailable",
    provider_name=sidecar.provider_name,
    advisory_only=True,
    notes=["Optional adapter readiness is support-only and cannot pass gates."],
)
```

If future classification or localization evidence becomes client-facing, declare
it alongside the existing reference/quality-gate contracts and map it to
support-only `GateEvidenceRefContract.authority` semantics rather than
inventing a parallel ad hoc optional-evidence envelope.

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
- Extend `tests/unit/adapters/mcp/test_vision_runtime_config.py` first for the
  shipped default-off config/runtime seam.
- Extend `tests/unit/adapters/mcp/test_vision_evaluation.py` and the existing
  `tests/fixtures/vision_eval/*/golden.json` tree for reference-understanding
  and optional-evidence fixture scoring only if `vision/evaluation.py` grows
  declared optional-evidence fields.
- Extend `tests/unit/adapters/mcp/test_reference_images.py` and
  `tests/e2e/vision/test_reference_stage_silhouette_contract.py` if optional
  evidence envelopes on compare/iterate responses change.
- Extend `tests/unit/scripts/test_script_tooling.py` if `scripts/vision_harness.py`
  changes; the default harness path must stay backend-executing unless a new
  explicit fixture-only opt-in is selected.
- Run `tests/e2e/integration/test_guided_surface_contract_parity.py` when
  optional evidence becomes visible on stdio or Streamable HTTP
  compare/iterate payloads.

## Docs To Update

- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
- `_docs/_MCP_SERVER/README.md` if support evidence appears in client-facing
  payloads.
- `_docs/_TESTS/README.md` if new fixture or harness structure is introduced.
- `_docs/_TASKS/TASK-158_Vision_And_Creature_Gate_Boundary_Doc_Alignment.md`
  completion summary.

## Changelog Impact

- Roll this slice into the single
  `_docs/_CHANGELOG/<next-number>-...task-158-...completion.md` entry created
  during `TASK-158-03` closeout.

## Status / Board Update

- This leaf stays under the umbrella `TASK-158`; keep `_docs/_TASKS/README.md`
  tracking on the parent row.
- When this slice closes, record whether optional evidence stayed internal,
  changed compare/iterate envelopes, or added transport-visible diagnostics so
  the parent closeout names the exact validation lane that was run.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_vision_evaluation.py tests/unit/adapters/mcp/test_reference_images.py -v`
- `PYTHONPATH=. poetry run pytest tests/unit/scripts/test_script_tooling.py -k vision_harness -v` if `scripts/vision_harness.py` changes.
- `poetry run pytest tests/e2e/vision/test_reference_stage_silhouette_contract.py -q`
  when compare/iterate optional-evidence envelopes change.
- `poetry run pytest tests/e2e/integration/test_guided_surface_contract_parity.py -q`
  when optional evidence becomes transport-visible on stdio or Streamable HTTP
  public surfaces.
- `rg -n -P "can_pass_gate\\s*[:=]\\s*true|status\\s*[:=]\\s*[\"']passed[\"']|gate_status\\s*[:=]\\s*[\"']passed[\"']|SAM|CLIP|SigLIP|Grounding ?DINO|OWL-ViT|from_pretrained|mlx_vlm\\.load|httpx\\.AsyncClient|provider key|api_key" server/adapters/mcp/vision tests/unit/adapters/mcp tests/fixtures/vision_eval scripts/vision_harness.py`
  - classify every hit as default-off/support-only or an explicit
    live-provider opt-in.

## Acceptance Criteria

- Optional perception adapters are default-off and non-fatal when unavailable.
- Optional evidence can support or challenge proposals but cannot pass gates.
- No implicit SAM/CLIP/SigLIP/Grounding DINO/OWL-ViT runtime activation occurs.
- Existing compare/iterate surfaces keep explicit disabled/unavailable optional
  evidence envelopes where those contracts already exist.
- Golden fixtures document expected support evidence shape without requiring a
  live provider on the default fixture/eval path.
- Any future heavy adapter implementation is clearly deferred to its own
  follow-on task unless explicitly implemented and validated here.
