# TASK-172-03-01: Localization Runtime Config And Provider Boundary

**Parent:** [TASK-172-03](./TASK-172-03_GroundingDINO_Or_OWL_Localization_For_Packet_Bounded_Part_Ambiguity.md)
**Depends On:** [TASK-172-02](./TASK-172-02_Stage_Bound_Activation_Policy_And_Localized_Support_Contracts.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Objective:** Add one default-off runtime/config seam and provider-neutral internal candidate contract for packet-bounded text-conditioned localization, without widening public compare/iterate payloads before the projection leaf lands.
**Repository Touchpoints:** `server/adapters/mcp/vision/config.py`, `server/adapters/mcp/vision/runtime.py`, `server/adapters/mcp/vision/backends.py`, `server/infrastructure/config.py`, `server/adapters/mcp/areas/reference_compare_packets.py`, `tests/unit/adapters/mcp/test_vision_runtime_config.py`, `tests/unit/adapters/mcp/test_vision_external_backend.py`, `tests/unit/adapters/mcp/test_vision_local_backend.py`, `_docs/_VISION/README.md`, `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
**Acceptance Criteria:**
- the runtime exposes one default-off localization config/provider seam that does not overload `VISION_SEGMENTATION_*` or classifier env names unless an explicit compatibility choice is documented
- one provider-neutral internal localization-candidate contract exists for packet id, reference/view provenance, label query, confidence, and literal box data needed for downstream support-only projection
- disabled or unavailable localization configuration degrades to bounded diagnostics and does not create a new public compare payload by itself

## Implementation Notes

- keep the first provider boundary vendor-neutral even if the first real
  implementation is GroundingDINO-like or OWL-ViT / OWLv2-like
- this leaf owns config/runtime/provider shape only; do not widen
  `ReferencePartSegmentationContract`, `ReferenceComparePacketContract`, or
  `support_evidence` here
- reuse the existing optional-runtime patterns from:
  - `TASK-140-06` for capability-aware external runtime posture
  - `TASK-128-03` for default-off generic sidecar seams
  - `TASK-164` for repo-local optional-sidecar operator expectations when a
    concrete local helper is later needed
- likely owner shape:
  - `VisionLocalizationProviderName`
  - `VisionLocalizationConfig`
  - `VisionLocalizationCandidate`
  - one runtime resolver/helper that maps config into a compare-time provider
    call contract
- if the chosen first provider is repo-local sidecar packaging rather than an
  already-running external/local service, track that packaging explicitly on a
  follow-on leaf instead of hiding it here

## Pseudocode

```python
config = VisionLocalizationConfig(
    enabled=False,
    provider_name="generic_sidecar",
    endpoint="http://127.0.0.1:9300/localize",
)

candidate = VisionLocalizationCandidate(
    packet_id="packet:tail_front",
    query_label="tail_mass",
    reference_id="ref_tail_front",
    target_view="front",
    confidence=0.88,
    box_xyxy=[101, 44, 218, 162],
)
```

## Runtime / Security Contract Notes

- keep localization config secret-safe and consistent with the existing sidecar
  credential redaction rules
- no raw image bytes or oversized provider payloads should persist on the
  internal candidate model
- disabled localization must remain a non-fatal optional branch

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `tests/unit/adapters/mcp/test_vision_local_backend.py`
- targeted runtime/provider tests on `reference_compare_packets.py` only where
  the new config seam is consumed

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md` if new operator-facing env
  names or provider choices become real

## Changelog Impact

- include the localization config/provider boundary in the first `TASK-172`
  implementation entry that ships compare-time localization

## Status / Board Update

- remains nested under `TASK-172-03`; no promoted board-row change by itself

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_vision_external_backend.py tests/unit/adapters/mcp/test_vision_local_backend.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`

## Validation Category

- localization runtime/config and provider-boundary proof
