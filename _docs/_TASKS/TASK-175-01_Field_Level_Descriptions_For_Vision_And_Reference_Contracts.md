# TASK-175-01: Field-Level Descriptions For Vision And Reference Contracts

**Parent:** [TASK-175](./TASK-175_Vision_Contract_Field_Descriptions_And_Stage_Read_Order.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Follow-on After:** [TASK-171](./TASK-171_Creature_Attachment_First_Build_Contract_And_Structured_Vision_Handoff.md), [TASK-166](./TASK-166_Hierarchical_Reference_Compare_Perceived_Evidence_And_Budget_Control.md)
**Objective:** Add concise, accurate `Field(description=...)` to every LLM-facing vision / reference result contract so the client can disambiguate near-synonymous fields and understand the advisory/authoritative posture from the schema alone, without changing any payload shape, field set, or default value.
**Repository Touchpoints:** `server/adapters/mcp/sampling/result_types.py`, `server/adapters/mcp/contracts/reference.py`, `server/adapters/mcp/contracts/base.py`, `tests/unit/adapters/mcp/test_contract_payload_parity.py`, `tests/unit/adapters/mcp/test_contract_docs.py`
**Acceptance Criteria:**
- the ~7 near-synonymous string lists on `VisionAssistContract`
  (`visible_changes`, `shape_mismatches`, `proportion_mismatches`,
  `correction_focus`, `next_corrections`, plus `goal_summary` /
  `reference_match_summary`) each carry a `Field(description=...)` that explains
  how that field differs from its siblings
- the packet status axes on `ReferenceComparePacketContract`
  (`extraction_status`, `ranking_status`, `packet_status`,
  `ranking_recommendation`, `localized_support_reason`, `status_reason`) each
  carry an inline description distinguishing extraction outcome from ranking
  outcome from packet-local delivery guidance
- every `confidence` field on the LLM-facing contracts carries an inline
  description stating it is non-authoritative and must not drive correctness
- magnitude-bearing fields (`ReferenceSilhouetteMetricContract.delta` /
  `reference_value` / `observed_value`, `ReferenceCompareSupportEvidenceContract.observed_value` /
  `delta`) describe values as reference-relative proportions, not absolute
  measurements
- all existing payload-parity fixtures in
  `test_contract_payload_parity.py` still validate unchanged; no field is added,
  removed, renamed, or re-typed

## Implementation Notes

- `MCPContract` (`server/adapters/mcp/contracts/base.py:13-16`) is a bare
  `BaseModel` with `model_config = ConfigDict(extra="forbid")`. `Field(...)`
  with a `description` is fully compatible with `extra="forbid"` because
  descriptions are schema metadata, not extra data; confirm this and add a short
  class docstring note that LLM-facing subclasses should self-describe.
- `pydantic.Field` is already imported and used in
  `server/adapters/mcp/contracts/reference.py` (e.g.
  `ReferenceUnderstandingClassificationScoreContract.score = Field(ge=0.0, le=1.0)`
  at `:247`, and `classification_scores = Field(default_factory=list, max_length=5)`
  at `:293`). `result_types.py` does not yet import `Field`, so add the import.
- Primary vision target is `VisionAssistContract`
  (`server/adapters/mcp/sampling/result_types.py:149-171`). Disambiguate the
  near-synonymous lists:
  - `visible_changes`: descriptive, what the VLM perceives changed between
    before / after captures (not necessarily reference-relative).
  - `shape_mismatches`: reference-relative shape divergences.
  - `proportion_mismatches`: reference-relative proportion / relative-size
    divergences expressed as ratios vs a trusted reference anchor, never
    absolute measurements.
  - `correction_focus`: the few areas the orchestrator should attend to now.
  - `next_corrections`: candidate next-step actions, still advisory.
  - `goal_summary` / `reference_match_summary`: narrative context only.
  - `confidence`: non-authoritative self-report; must not gate decisions.
- Add descriptions on the nested vision contracts at the same time:
  `VisionIssueContract` (`:90`), `VisionRecommendedCheckContract` (`:98`),
  `VisionInputSummaryContract` (`:106`), `VisionPacketStatusContract` (`:126`),
  `VisionCapabilitySummaryContract` (`:134`), and reinforce the existing booleans
  on `VisionBoundaryPolicyContract` (`:115-123`) with one-line descriptions so
  the advisory boundary is legible inline, not only via field names.
- Reference targets in `server/adapters/mcp/contracts/reference.py`:
  - `ReferenceOrchestratorFeedbackContract` (`:336-366`): describe the compact
    read-model fields the client should consume first (`status`,
    `blocking_reasons`, `next_actions`, `next_checkpoint_tool`,
    `recommended_repair`, `correction_focus`, `loop_disposition`).
  - `ReferenceComparePacketContract` (`:532-555`): describe the status axes and
    `localized_support_reason`.
  - `ReferenceCompareSupportEvidenceContract` (`:515-529`): describe
    `observed_value` / `delta` as reference-relative and `confidence` as
    non-authoritative.
  - `ReferenceSilhouetteMetricContract` (`:699-715`) and
    `ReferenceSilhouetteAnalysisContract` (`:748-758`): describe the metric ids
    and that deltas are 2D-bbox-normalized proportions (deterministic, but still
    coarse), not metric measurements.
  - `ReferenceActionHintContract` (`:718-734`): describe `hint_type` as a typed
    deterministic corrective hint.
- Keep descriptions short (one sentence, imperative or declarative) to avoid
  bloating the schema payload. Do not introduce raw-coordinate guidance; where a
  field could carry coordinates (e.g. localization seams), describe them as
  on-demand secondary evidence behind symbolic relations + ratios.
- Research basis to cite inline in the source comment / commit body when the
  slice lands: Descrip3D (arXiv:2507.14555) shows per-object/per-field natural
  language descriptions improve downstream 3D-scene understanding; Structured
  Interfaces / GraphRAG schema framing (arXiv:2510.16643) shows that
  schema-level field framing improves an LLM's ability to consume structured
  graph/record output. RESEARCH CAVEAT: both are indoor-scan / synthetic, not
  Blender-vs-reference; re-measure on `tests/fixtures/vision_eval` before
  promoting any gain.

## Pseudocode

```python
# server/adapters/mcp/sampling/result_types.py
from pydantic import Field

class VisionAssistContract(MCPContract):
    """Structured bounded vision result for macro/workflow reporting."""

    visible_changes: list[str] = Field(
        description=(
            "Advisory VLM-perceived changes between before/after captures; "
            "descriptive only, not reference-relative, not truth."
        ),
    )
    shape_mismatches: list[str] = Field(
        default=[],
        description="Advisory reference-relative shape divergences vs the anchor reference.",
    )
    proportion_mismatches: list[str] = Field(
        default=[],
        description=(
            "Advisory reference-relative proportion divergences expressed as "
            "ratios vs a trusted reference anchor; never absolute measurements."
        ),
    )
    correction_focus: list[str] = Field(
        default=[],
        description="Advisory: the few areas the orchestrator should attend to now.",
    )
    next_corrections: list[str] = Field(
        default=[],
        description="Advisory candidate next-step actions; not a deterministic plan.",
    )
    confidence: float | None = Field(
        default=None,
        description=(
            "Non-authoritative VLM self-report; must not gate correctness. "
            "Deterministic checks own scene truth."
        ),
    )
```

## Runtime / Security Contract Notes

- Vision stays ADVISORY. Every description must keep the
  `not_truth_source` / `requires_deterministic_checks_for_correctness` posture
  from `VisionBoundaryPolicyContract`; no description may suggest vision can mark
  a gate complete or unlock a tool. Deterministic inspection / assertion /
  silhouette own scene truth.
- `confidence` descriptions must state non-authoritative explicitly; the buried
  boolean stays, but the inline wording is the durable signal.
- Magnitude descriptions stay PROPORTIONAL RATIOS vs a trusted reference anchor,
  never authoritative absolute measurements.
- This slice is additive metadata only: no field, default, type, or behavior
  change, so it is reversible by reverting description text and does not require
  any Blender / addon main-thread or `capture_scene_state` / `restore_scene_state`
  work.
- Do not reopen the optional heavy-sidecar runtime (`TASK-172`) or the
  `TASK-140-06` provider-capability substrate; descriptions may name optional
  fields but must not change their default-off, advisory posture.

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_contract_payload_parity.py` (confirm existing
  representative payloads still validate; optionally add a schema-level check that
  the disambiguated fields now carry a non-empty `description`)
- `tests/unit/adapters/mcp/test_contract_docs.py` (add coverage that the
  LLM-facing vision/reference contracts expose field descriptions and that the
  `confidence` descriptions contain the non-authoritative wording)

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
- `_docs/_MCP_SERVER/README.md`

## Changelog Impact

- add/update the historical `_docs/_CHANGELOG/*` entry when this slice lands

## Status / Board Update

- board tracking remains on umbrella `TASK-175`
- no separate promoted board-row change is expected for this subtask unless it
  later becomes a standalone follow-on

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_contract_docs.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`

## Validation Category

- additive contract self-description proof
