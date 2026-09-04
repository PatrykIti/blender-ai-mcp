# TASK-158-05: Optional Perception Adapter Readiness And Eval Harness

**Status:** ✅ Done
**Priority:** 🟠 High
**Parent:** [TASK-158](./TASK-158_Vision_And_Creature_Gate_Boundary_Doc_Alignment.md)
**Category:** Vision / Optional Perception Readiness
**Estimated Effort:** Medium

## Objective

Build on the closed `TASK-157` substrate with the readiness layer for optional
perception evidence that was intentionally excluded from the first
quality-gate substrate: default-off support contracts on the currently shipped
segmentation-sidecar/runtime seam, deterministic fixture/eval harness support,
and clear provider/runtime boundaries for future CLIP/SigLIP-style
classification or localization follow-ons.

This slice is not a mandate to ship heavy adapters by default. It creates the
safe extension shape so future adapters can produce bounded proposal/support
records without becoming verifier truth.

## Repository Touchpoints

| Path / Module | Expected Change |
|---------------|-----------------|
| `server/adapters/mcp/vision/config.py` | Extend typed optional sidecar/adapter config only through `VisionRuntimeConfig` / `VisionSegmentationSidecarConfig` |
| `server/adapters/mcp/vision/runtime.py` | Keep optional perception lazy, default-off, and aligned with the shipped `build_vision_runtime_config(...)` seam |
| `server/adapters/mcp/vision/evaluation.py` | Extend fixture/eval scoring only if optional-evidence diagnostics become first-class scored output |
| `server/adapters/mcp/contracts/quality_gates.py` | Reuse `TASK-157` proposal/support evidence refs; do not add new pass/fail authority |
| `server/adapters/mcp/contracts/reference.py` | Preserve `ReferencePartSegmentationContract` and any other declared support envelopes; add new client-facing optional-evidence contracts explicitly |
| `server/adapters/mcp/contracts/router.py` | Declare any operator-facing readiness diagnostics before `router_get_status(...)` exposes them outside compare/iterate payloads |
| `server/adapters/mcp/areas/reference.py` | Keep top-level and compact-iterate `part_segmentation` envelope behavior aligned with the shipped compare/iterate surface |
| `server/adapters/mcp/areas/router.py` | Surface optional-readiness diagnostics only through the existing `router_get_status(...)` lane when they become public there |
| `server/adapters/mcp/session_capabilities.py` | Keep goal-time unavailable evidence bounds aligned for `part_segmentation` / `classification_scores` and any new optional support-only evidence kinds |
| `server/infrastructure/config.py` | Extend the current `VISION_SEGMENTATION_*` opt-in surface first; do not create a parallel flag family for the same readiness path |
| `server/infrastructure/di.py` | Keep runtime wiring on the shared `build_vision_runtime_config(...)` DI path; do not create a second runtime loader/registry |
| `tests/fixtures/vision_eval/` | Reuse the existing golden fixture tree for reference-understanding and optional evidence scoring |
| `tests/unit/adapters/mcp/test_vision_runtime_config.py` | Validate default-off config and typed runtime opt-in behavior |
| `tests/unit/adapters/mcp/test_reference_images.py` | Keep compare/iterate envelopes and compact-iterate behavior aligned |
| `tests/unit/adapters/mcp/test_vision_evaluation.py` | Verify optional-evidence fixture scoring only if evaluation schema expands |
| `tests/unit/router/application/test_router_contracts.py` | Keep `RouterStatusContract` aligned when optional-readiness diagnostics become public |
| `scripts/vision_harness.py` | Add a providerless fixture/eval mode only as an explicit opt-in path; keep the current default backend-executing flow unchanged |
| `tests/unit/scripts/test_script_tooling.py` | Keep harness CLI semantics and default backend-executing flow unchanged |
| `tests/e2e/vision/test_reference_stage_silhouette_contract.py` | Preserve disabled/unavailable compare/iterate optional-evidence envelopes |
| `tests/e2e/integration/test_guided_gate_state_transport.py` | Own compare/iterate and gate-intake transport parity when optional evidence becomes public there |
| `tests/e2e/integration/test_mcp_transport_modes.py` | Preserve stdio / Streamable HTTP contract parity for public compare/iterate payload changes |
| `tests/e2e/integration/test_guided_surface_contract_parity.py` | Run only when optional readiness diagnostics affect guided visibility or router-status public surfaces |
| `tests/e2e/vision/test_reference_guided_creature_comparison.py` | Preserve the default backend-executing harness path if `vision_harness` semantics change |
| `tests/e2e/vision/test_real_view_variant_model_comparison.py` | Preserve live-backend harness defaults when fixture-only modes or providerless helpers are added |
| `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md` | Document what is ready now vs deferred adapter implementation |

## Implementation Notes

- SAM/segmentation sidecars and any future CLIP/SigLIP-style classification or
  localization adapters must be default-off.
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
- The current typed config/runtime/DI seam only owns `segmentation_sidecar`.
  If CLIP/SigLIP-style classification or localization needs dedicated flags,
  loader wiring, or runtime registration beyond support-only contracts and
  explicit unavailable diagnostics, split that work into a follow-on task
  before implementation instead of overloading this leaf.
- Future concrete adapter implementation should be split into follow-on leaves
  if it requires new dependencies, model downloads, service startup, or
  external provider credentials.
- Reuse the shipped segmentation-sidecar config/runtime seam first:
  `VISION_SEGMENTATION_*` in `server/infrastructure/config.py`,
  `VisionSegmentationSidecarConfig` in `server/adapters/mcp/vision/config.py`,
  `VisionRuntimeConfig` plus `build_vision_runtime_config(...)` in
  `server/adapters/mcp/vision/runtime.py`, and the shared DI wiring in
  `server/infrastructure/di.py`. Do not invent a second default-off
  registry/flag path, env prefix, or runtime loader for the same readiness
  concern.
- The current guided gate-intake seam already treats `part_segmentation` and
  `classification_scores` as goal-time unavailable evidence via
  `_GOAL_TIME_UNAVAILABLE_GATE_EVIDENCE_KINDS` and
  `_apply_goal_time_gate_input_bounds(...)` in
  `server/adapters/mcp/session_capabilities.py`. Keep any new optional
  evidence kinds aligned with that default-off intake policy unless a later
  contract explicitly widens it.
- The current `scripts/vision_harness.py` default path is live-backend-capable
  and `--backend` defaults to `all`. Any providerless fixture mode introduced by
  this task must be an explicit opt-in path or helper; it must not silently
  change `_run_backend()` / `_run()` or the default CLI semantics.
- `ReferencePartSegmentationContract` is the existing compare/iterate owner for
  support-only optional evidence. Extend that contract or another declared
  contract in `server/adapters/mcp/contracts/reference.py` before surfacing new
  diagnostics; do not invent a second optional-evidence envelope for the same
  compare/iterate lane.
- If optional-readiness diagnostics become operator-visible outside
  compare/iterate payloads, declare them in `RouterStatusContract` and expose
  them through `router_get_status(...)`; do not add a second adapter-status
  tool or free-form router payload.

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

`ReferencePartSegmentationContract` already exists in
`server/adapters/mcp/contracts/reference.py`; extend that contract and the
current `server/adapters/mcp/areas/reference.py` compare/iterate envelope
rather than creating a second readiness record. If the same diagnostics become
public in router status, declare them in `RouterStatusContract` first.

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
- Extend `tests/e2e/integration/test_guided_gate_state_transport.py` when
  compare/iterate payloads or goal-time gate intake behavior changes for
  optional evidence kinds such as `part_segmentation` or
  `classification_scores`.
- Extend `tests/e2e/integration/test_mcp_transport_modes.py` when public
  compare/iterate payload shape changes must stay aligned across stdio and
  Streamable HTTP.
- Extend `tests/unit/scripts/test_script_tooling.py` if `scripts/vision_harness.py`
  changes; the default harness path must stay backend-executing unless a new
  explicit fixture-only opt-in is selected.
- Extend `tests/unit/adapters/mcp/test_router_elicitation.py` when
  `router_get_status(...)` publishes optional-readiness diagnostics outside the
  compare/iterate payloads.
- Extend `tests/unit/router/application/test_router_contracts.py` when
  operator-visible readiness fields become part of `RouterStatusContract`.
- Run `tests/e2e/integration/test_guided_surface_contract_parity.py` only when
  optional readiness changes affect guided visibility or router-status public
  surfaces outside compare/iterate payloads.
- Extend `tests/e2e/vision/test_reference_guided_creature_comparison.py` and
  `tests/e2e/vision/test_real_view_variant_model_comparison.py` when
  `scripts/vision_harness.py` default backend behavior or subprocess-facing
  invocation semantics change.

## Docs To Update

- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
- `_docs/_MCP_SERVER/README.md` if support evidence appears in client-facing
  payloads.
- `_docs/_TESTS/README.md` if new fixture or harness structure is introduced.
- `_docs/_TASKS/TASK-158_Vision_And_Creature_Gate_Boundary_Doc_Alignment.md`
  completion summary.

## Changelog Impact

- If this leaf closes independently, add a scoped `_docs/_CHANGELOG/*` entry in
  the same branch and update `_docs/_CHANGELOG/README.md`.
- If multiple `TASK-158` leaves land together in one wave, one shared
  completion entry may cover them, but it must name this leaf explicitly and
  record its validation in the summary.

## Status / Board Update

- This leaf stays under the umbrella `TASK-158`; keep `_docs/_TASKS/README.md`
  tracking on the parent row.
- When this slice closes, record whether optional evidence stayed internal,
  changed compare/iterate envelopes, or added transport-visible diagnostics so
  the parent closeout names the exact validation lane that was run.
- Do not leave this leaf open under a closed `TASK-158`. If concrete heavy
  adapter work is deferred, create an explicit `Follow-on After` task for that
  adapter scope and close or supersede the stale leaf state in the same branch.

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_vision_evaluation.py tests/unit/adapters/mcp/test_reference_images.py -v`
- `PYTHONPATH=. poetry run pytest tests/unit/scripts/test_script_tooling.py -k vision_harness -v` if `scripts/vision_harness.py` changes.
- `poetry run pytest tests/e2e/vision/test_reference_stage_silhouette_contract.py -q`
  when compare/iterate optional-evidence envelopes change.
- `poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
  when compare/iterate payloads or goal-time gate intake behavior change for
  optional evidence kinds.
- `poetry run pytest tests/e2e/integration/test_mcp_transport_modes.py -q`
  when public compare/iterate payload shape changes must stay aligned across
  stdio and Streamable HTTP.
- `poetry run pytest tests/e2e/integration/test_guided_surface_contract_parity.py -q`
  when optional readiness changes affect guided visibility or router-status
  public surfaces outside compare/iterate payloads.
- `poetry run pytest tests/unit/adapters/mcp/test_router_elicitation.py -v`
  when optional-readiness diagnostics become visible on `router_get_status(...)`.
- `poetry run pytest tests/unit/router/application/test_router_contracts.py -v`
  when optional-readiness diagnostics become part of `RouterStatusContract`.
- `poetry run pytest tests/e2e/vision/test_reference_guided_creature_comparison.py tests/e2e/vision/test_real_view_variant_model_comparison.py -q`
  when `scripts/vision_harness.py` default backend behavior changes.
- `rg -n -P "can_pass_gate\\s*[:=]\\s*true|status\\s*[:=]\\s*[\"']passed[\"']|gate_status\\s*[:=]\\s*[\"']passed[\"']|SAM|CLIP|SigLIP|Grounding ?DINO|OWL-ViT|from_pretrained|mlx_vlm\\.load|httpx\\.AsyncClient|provider key|api_key" server/adapters/mcp/vision tests/unit/adapters/mcp tests/fixtures/vision_eval scripts/vision_harness.py`
  - classify every hit as default-off/support-only or an explicit
    live-provider opt-in.

## Acceptance Criteria

- Optional perception adapters are default-off and non-fatal when unavailable.
- Optional evidence can support or challenge proposals but cannot pass gates.
- No implicit SAM/CLIP/SigLIP/Grounding DINO/OWL-ViT runtime activation occurs.
- Existing compare/iterate surfaces keep explicit disabled/unavailable optional
  evidence envelopes where those contracts already exist.
- Goal-time gate intake keeps `part_segmentation` and
  `classification_scores` unavailable-by-default unless a later contract
  explicitly widens that policy.
- Runtime opt-in remains owned by the existing `VISION_SEGMENTATION_*` ->
  `VisionSegmentationSidecarConfig` / `VisionRuntimeConfig` ->
  `build_vision_runtime_config(...)` / shared DI wiring path.

## Completion Summary

- completed on 2026-05-02 by keeping optional perception on the shipped
  default-off segmentation/runtime seam and by adding an explicit
  providerless-only `--fixture-only reference-understanding` harness mode to
  `scripts/vision_harness.py`
- compare/iterate surfaces continue to expose explicit
  `part_segmentation.status="disabled"` / `"unavailable"` envelopes instead of
  silently pretending support exists
- goal-time intake continues to treat `part_segmentation` and
  `classification_scores` as unavailable-by-default evidence kinds
- no operator-visible adapter-status tool or implicit SAM/CLIP/SigLIP runtime
  activation was introduced in this wave
- validated with:
  `PYTHONPATH=. poetry run pytest tests/unit/scripts/test_script_tooling.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py -q`
- CLIP/SigLIP-style classification and localization adapters remain follow-on
  contract/runtime work unless this task explicitly introduces and validates a
  dedicated typed owner for them.
- Any public readiness/status diagnostics are declared via the existing
  `ReferencePartSegmentationContract` or `RouterStatusContract`; no parallel
  adapter-status surface is introduced.
- Golden fixtures document expected support evidence shape without requiring a
  live provider on the default fixture/eval path.
- Any future heavy adapter implementation is clearly deferred to its own
  follow-on task unless explicitly implemented and validated here.
