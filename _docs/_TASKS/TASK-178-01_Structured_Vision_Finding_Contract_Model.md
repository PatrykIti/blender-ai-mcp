# TASK-178-01: Structured Vision Finding Contract Model

**Parent:** [TASK-178](./TASK-178_Structured_Per_Finding_Compare_Schema.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Follow-on After:** [TASK-171-05](./TASK-171-05_Attachment_First_Creature_Reference_Understanding_Contract_Expansion.md), [TASK-172-03-02](./TASK-172-03-02_Compare_Time_Localization_Projection_And_Transport.md)
**Objective:** Introduce a typed `VisionFinding` contract carrying `finding`, `view_id`, `target_label`, `axis`, `direction`, `magnitude_ratio`, `reference_id`, and `confidence`, and adopt it inside `VisionAssistContract` for the geometric-finding fields while keeping backward-compatible flat `list[str]` projections so weak/legacy models and the `google_family_compare` profile keep working unchanged.

**Repository Touchpoints:** `server/adapters/mcp/sampling/result_types.py`, `server/adapters/mcp/contracts/reference.py`, `tests/unit/adapters/mcp/test_contract_payload_parity.py`, `tests/unit/adapters/mcp/test_reference_compare_packets.py`

**Acceptance Criteria:**
- a new `VisionFinding` `MCPContract` exists with `finding: str`, `view_id: str | None`, `target_label: str | None`, `axis: Literal[...] | None`, `direction: Literal[...] | None`, `magnitude_ratio: float | None`, `reference_id: str | None`, and `confidence: float | None`
- `target_label` reuses the existing reference-understanding canonical role vocabulary (`body_core`, `head_mass`, `tail_mass`, `snout_mass`, `ear_pair`, `eye_pair`, `foreleg_pair`, `hindleg_pair`), not a new taxonomy
- `VisionAssistContract` gains structured finding lists for the geometric fields (e.g. `shape_findings`, `proportion_findings`) while the existing `shape_mismatches` / `proportion_mismatches` / `correction_focus` `list[str]` fields remain as derived backward-compatible string projections
- `magnitude_ratio` is documented as a proportional ratio relative to `reference_id` and never an absolute measurement
- `confidence` and `magnitude_ratio` fields keep the advisory `boundary_policy` semantics; nothing in the model implies truth authority
- `model_config = ConfigDict(extra="forbid")` (inherited from `MCPContract`) round-trips structured findings without breaking `test_contract_payload_parity.py`

## Implementation Notes

- the public compare model is `VisionAssistContract`
  (`server/adapters/mcp/sampling/result_types.py:149-171`). Today its
  geometric-finding fields are flat lists:
  - `visible_changes: list[str]` (`:158`)
  - `shape_mismatches: list[str] = []` (`:159`)
  - `proportion_mismatches: list[str] = []` (`:160`)
  - `correction_focus: list[str] = []` (`:161`)
  - `next_corrections: list[str] = []` (`:163`)
  - `captures_used: list[str] = []` (`:168`)
- the data model can already carry per-finding view/binding/confidence: see
  `VisionLocalizationCandidate` (`server/adapters/mcp/vision/config.py:420`) with
  `target_view`, `reference_id`, `box_xyxy`, and a range-validated
  `confidence: float | None = Field(default=None, ge=0.0, le=1.0)`. Reuse that
  same `ge=0.0, le=1.0` validation pattern for `VisionFinding.confidence`.
- `target_label` vocabulary already exists as the reference-understanding role
  labels. The prompt enumerates them at `vision/prompting.py:408`
  (`body_core, head_mass, tail_mass, snout_mass, ear_pair, eye_pair,
  foreleg_pair, hindleg_pair`), and reference-understanding contracts already
  type a free-text `target_label` field
  (`server/adapters/mcp/contracts/reference.py:133/152/164/175/184/193`). This
  subtask should keep `target_label` permissive (`str | None`) on the wire so a
  weak model can still answer, but document the canonical vocabulary as the
  expected value space and add it to the schema description in TASK-178-02.
- add a small helper (e.g. `VisionFinding.to_projection_string()` or a
  module-level `project_findings_to_strings(findings)`) that renders a structured
  finding into the existing flat-string form so the legacy `shape_mismatches` /
  `proportion_mismatches` projections stay populated for downstream consumers
  that have not yet migrated.
- `ReferenceCorrectionVisionEvidenceContract`
  (`server/adapters/mcp/contracts/reference.py:466-473`) currently carries only
  `list[str]` evidence (`correction_focus`, `shape_mismatches`,
  `proportion_mismatches`, `next_corrections`). Extend it (additively) with an
  optional `findings: list[VisionFinding] = []` so the planner side of
  TASK-178-03 has a typed channel; keep the existing string lists for
  compatibility.
- techniques to cite for the schema shape (advisory framing only, no VLM CoT):
  - **SpatialRGPT** (arXiv:2406.01584) — six-quantity spatial schema motivates
    splitting one opaque finding into `axis` + `direction` + `magnitude_ratio`
  - **SceneVerse** (arXiv:2401.09340) — relation-triplet structure motivates the
    `(target_label, reference_id, relation)` binding instead of free text
  - **ShapeLLM** (arXiv:2402.17766) — structured 3D output supports typed
    per-finding objects over prose
  - **SpatialVLM** (arXiv:2401.12168) / **SD-VLM** (arXiv:2509.17664) —
    proportional reasoning supports `magnitude_ratio` as a ratio anchored to
    `reference_id`, not an absolute measurement

## Pseudocode

```python
from typing import Literal
from pydantic import Field
from server.adapters.mcp.contracts.base import MCPContract

VisionFindingAxis = Literal["x", "y", "z", "width", "height", "depth", "none"]
VisionFindingDirection = Literal[
    "too_large", "too_small", "too_wide", "too_narrow",
    "too_tall", "too_short", "shifted", "rotated", "none",
]


class VisionFinding(MCPContract):
    """One structured, advisory geometric finding from compare interpretation."""

    finding: str
    view_id: str | None = None
    target_label: str | None = None          # canonical reference-understanding role
    axis: VisionFindingAxis | None = None
    direction: VisionFindingDirection | None = None
    magnitude_ratio: float | None = None      # proportional vs reference_id, never absolute
    reference_id: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    def to_projection_string(self) -> str:
        bits = [self.finding]
        if self.target_label:
            bits.append(f"({self.target_label})")
        if self.magnitude_ratio is not None and self.reference_id:
            bits.append(f"~{self.magnitude_ratio:g}x vs {self.reference_id}")
        return " ".join(bits)


# VisionAssistContract gains structured channels alongside the legacy lists:
#   shape_findings: list[VisionFinding] = []
#   proportion_findings: list[VisionFinding] = []
# and the existing shape_mismatches / proportion_mismatches stay populated via
# project_findings_to_strings(...) for backward compatibility.
```

## Runtime / Security Contract Notes

- `VisionFinding` is advisory interpretation only. It inherits the
  `VisionAssistContract.boundary_policy` posture
  (`interpretation_only`, `not_truth_source`,
  `requires_deterministic_checks_for_correctness`,
  `confidence_is_non_authoritative`). Nothing on the model may mark gates
  complete, unlock tools, or assert scene truth.
- `magnitude_ratio` must be treated and documented as a proportional ratio
  versus `reference_id` only. It is never an absolute measurement; deterministic
  measurement tools own absolute magnitudes.
- do not add `box_xyxy` or raw coordinate fields to `VisionFinding` as primary
  evidence. Symbolic `target_label` + `axis` + ratio is the primary signal;
  coordinates stay on the optional `VisionLocalizationCandidate` seam only.
- this subtask is contract/typing only and does not touch addon or Blender
  main-thread behavior, so no `capture_scene_state` / `restore_scene_state`
  reversibility work is required here.

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_reference_compare_packets.py`

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`

## Changelog Impact

- add/update a `_docs/_CHANGELOG/*` entry when this slice lands

## Status / Board Update

- board tracking remains on umbrella `TASK-178`
- no separate promoted board-row change is expected for this subtask unless it
  later becomes a standalone follow-on

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_reference_compare_packets.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`

## Validation Category

- typed-contract / backward-compatibility proof
