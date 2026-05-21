# TASK-172-02: Stage-Bound Activation Policy And Localized Support Contracts

**Parent:** [TASK-172](./TASK-172_Optional_Vision_Capability_Runtime_And_Localized_Perception.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Objective:** Define exactly when RU refresh and staged compare/iterate may invoke localized optional perception, and keep that support packet-bounded, advisory-only, and on the current public surfaces.
**Repository Touchpoints:** `server/adapters/mcp/areas/reference_understanding.py`, `server/adapters/mcp/areas/reference_compare_packets.py`, `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/vision/reference_support.py`, `server/adapters/mcp/contracts/reference.py`, `server/adapters/mcp/contracts/quality_gates.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_contract_payload_parity.py`, `tests/unit/adapters/mcp/test_public_surface_docs.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
**Acceptance Criteria:**
- heavy optional perception is not invoked by default for every reference or packet
- each localized invocation path names one bounded reason such as missing part ambiguity, anchor ambiguity, seam uncertainty, or local mask need
- emitted contracts remain additive support evidence and do not become a second truth or gate authority path

## Implementation Notes

- do not build a new global trigger engine; keep activation policy on the seams
  that already own reference refresh and packet compare:
  - `reference_images(...)` / RU refresh
  - staged compare packet planning
  - staged iterate follow-up
- define one small normalized vocabulary for invocation reasons, for example:
  - `part_missing_ambiguity`
  - `anchor_ambiguity`
  - `attachment_gap`
  - `seam_unclear`
  - `mask_needed`
- localized support payloads should carry bounded scope:
  - packet id or compare slice
  - reference ids / view ids
  - target role labels or target objects where already known
  - optional focus pair or local region hint
- preserve the current rule that optional perception may inform support
  evidence, planner hints, or operator diagnostics, but not final completion

## Pseudocode

```python
if packet.reason in {"seam_unclear", "part_missing_ambiguity"}:
    support_request = LocalizedPerceptionRequest(
        packet_id=packet.packet_id,
        target_roles=["tail_mass", "body_core"],
        request_kind="mask_or_box",
    )
```

## Runtime / Security Contract Notes

- no default full-image heavy pass
- no implicit adapter startup during unrelated guided steps
- localized support requests must stay bounded in image count, region scope, and
  returned artifacts

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`

## Docs To Update

- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`

## Changelog Impact

- record the new activation-policy and support-contract vocabulary in the first
  `TASK-172` runtime entry that ships this leaf

## Status / Board Update

- board tracking remains on the umbrella `TASK-172`

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`

## Validation Category

- localized support policy and transport proof
