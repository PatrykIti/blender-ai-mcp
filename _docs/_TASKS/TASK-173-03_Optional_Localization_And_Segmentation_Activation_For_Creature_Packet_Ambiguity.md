# TASK-173-03: Creature-Packet Consumer Policy For Optional Localization And Segmentation

**Parent:** [TASK-173](./TASK-173_Reference_Guided_Creature_Scope_Convergence_And_Optional_Grounding_Followups.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Follow-on After:** [TASK-172-02](./TASK-172-02_Stage_Bound_Activation_Policy_And_Localized_Support_Contracts.md), [TASK-172-03](./TASK-172-03_GroundingDINO_Or_OWL_Localization_For_Packet_Bounded_Part_Ambiguity.md)
**Related:** [TASK-172-04](./TASK-172-04_SAM_Or_SAM2_Local_Mask_And_Landmark_Support.md)
**Objective:** Add one creature-specific consumer policy on top of the already-shipped optional localization and segmentation seams, so bounded appendage packets can request extra grounding only when the current creature compare path is under-grounded, and so feedback explains why those sidecars were invoked, skipped, or unavailable.
**Repository Touchpoints:** `server/adapters/mcp/areas/reference_compare_packets.py`, `server/adapters/mcp/areas/reference_feedback.py`, `server/adapters/mcp/contracts/reference.py`, `server/adapters/mcp/vision/config.py`, `server/adapters/mcp/vision/runtime.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_vision_runtime_config.py`, `tests/unit/adapters/mcp/test_reference_compare_packets.py`, `tests/unit/adapters/mcp/test_contract_payload_parity.py`, `tests/unit/router/application/test_router_contracts.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, `tests/e2e/vision/test_reference_guided_squirrel_quality_regression.py`, `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
**Acceptance Criteria:**
- the creature compare loop can invoke already-shipped localization and/or segmentation only for bounded appendage packets where current creature evidence says the packet is ambiguous or under-grounded after the current broad/local compare policy has already failed to resolve that packet cleanly
- the task does not reopen generic provider/runtime transport semantics from `TASK-172`; it adds only creature-packet trigger policy, selection rules, and explainability on top of those seams
- optional localization/segmentation remain default-off, advisory-only, and packet-bounded
- compare-time feedback can explain when those sidecars were considered, used, skipped, or unavailable for the current creature packet

## Implementation Notes

- the latest session proved a very specific gap:
  - classifier worked
  - OpenRouter vision worked
  - localization sidecar was healthy
  - but localization was never invoked even while appendage ambiguity remained
- this is not generic runtime or transport work; `TASK-172-02` and
  `TASK-172-03` already shipped that substrate
- packet-local segmentation carrier ownership remains historical on the
  earlier optional-segmentation lane tracked through `TASK-172-04`; this task
  only consumes that existing seam for creature-packet trigger policy
- this task is the creature-policy consumer on top of the existing runtime:
  - when should ears/legs/tail ambiguity trigger localization?
  - when is segmentation worth the cost?
  - when should the loop stay with pure compare-time vision + truth?
- keep compare-time execution ownership on `reference_compare_packets.py`; do
  not re-open generic sidecar packaging or RU-time activation policy here
- activation must be tied to bounded packet reasons such as:
  - unresolved appendage gate with repeated stale/failure on assembled loop
  - mismatch between packet focus and expected creature role
  - repeated broad-body/head packets while appendage gates remain unresolved

## Pseudocode

```python
if packet_is_creature_appendage(packet) and packet_under_grounded(packet, gate_plan, compare_state):
    if localization_available(runtime):
        localization_support = run_localization_sidecar(packet)
    if segmentation_available(runtime) and localization_support_requests_mask(packet, localization_support):
        segmentation_support = run_segmentation_sidecar(packet, localization_support)
packet_support = merge_optional_support(packet_support, localization_support, segmentation_support)
```

## Runtime / Security Contract Notes

- optional sidecars stay advisory-only and cannot pass quality gates
- keep activation packet-bounded; do not turn this into a hidden whole-scene
  heavy pass
- public payloads must continue to expose bounded support evidence, not raw
  sidecar-native blobs or oversized image data

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_reference_compare_packets.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/router/application/test_router_contracts.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`
- `tests/e2e/vision/test_reference_guided_squirrel_quality_regression.py`

## Docs To Update

- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`

## Changelog Impact

- add/update the historical `_docs/_CHANGELOG/*` entry when this slice lands

## Status / Board Update

- board tracking remains on umbrella `TASK-173`
- no separate promoted board-row change is expected for this subtask unless it
  later becomes a standalone follow-on

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/router/application/test_router_contracts.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py tests/e2e/vision/test_reference_guided_squirrel_quality_regression.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`

## Validation Category

- optional grounding activation and advisory-support proof
