# 369. TASK-175 vision contract field descriptions and stage read-order

Date: 2026-05-30

## Summary

Implemented `TASK-175`: the LLM-facing vision/reference result contracts now
carry inline `Field(description=...)` metadata, and the staged compare/iterate
tool docstrings now state an explicit read-order and authoritative-vs-advisory
precedence. Previously `MCPContract` was a bare `BaseModel` with no field
descriptions, so the orchestrating LLM had to disambiguate the five
near-synonymous compare lists (and the two scalar narrative summaries) by name
alone, and `confidence` was flagged non-authoritative only via a boolean buried
in `boundary_policy`. Purely additive: no field set, default, or payload shape
changes.

## Changes

- `server/adapters/mcp/sampling/result_types.py`: added concise descriptions to
  `VisionAssistContract` (the five `list[str]` compare fields, the scalar
  `goal_summary`/`reference_match_summary`, `likely_issues`,
  `recommended_checks`, `packet_guidance`, `capability_summary`, `captures_used`,
  `input_summary`, `boundary_policy`), with `confidence` now marked
  non-authoritative inline; also annotated `VisionIssueContract`,
  `VisionRecommendedCheckContract`, and the `VisionPacketStatusContract` status
  axes so `ready`/`clean`/`low_information`/`blocked` are distinguishable from
  the schema. Mutable list/model defaults were moved to `default_factory` (a
  correctness improvement) without changing the default values.
- `server/adapters/mcp/contracts/reference.py`: documented
  `ReferenceOrchestratorFeedbackContract` as the read-first normalized next-step
  contract and described its advisory fields (`next_actions`, `correction_focus`,
  `evidence_summary`, `uncertainty_notes`, `loop_disposition`, `status`,
  `construction_path`, `selected_family`).
- `server/adapters/mcp/areas/reference.py`: the
  `reference_compare_stage_checkpoint` and `reference_iterate_stage_checkpoint`
  docstrings now state the read order (orchestrator feedback -> deterministic
  truth -> advisory vision) and reiterate that vision is advisory
  (`not_truth_source`, non-authoritative `confidence`).

## Tests

- `tests/unit/adapters/mcp/test_vision_result_types.py`: core fields carry
  descriptions, `confidence` is marked non-authoritative, and defaults are
  unchanged
- full `poetry run pytest ./tests/unit` green; `ruff` and `mypy` clean

## Research Basis

Descrip3D (arXiv:2507.14555) and structured-interface schema framing
(arXiv:2510.16643): self-describing schemas improve LLM consumption of
structured state. Gains to be re-measured on `tests/fixtures/vision_eval`.
