# TASK-121-01-01: Vision Assistant Result Envelope and Status Model

**Parent:** [TASK-121-01](./TASK-121-01_Vision_Assistant_Boundary_And_Delivery_Contract.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** The bounded `vision_assistant` envelope now carries a
reusable richer result model on top of the earlier base shape. In addition to
`goal_summary`, `reference_match_summary`, `visible_changes`,
`likely_issues`, and `recommended_checks`, the contract now exposes
`backend_name`, `shape_mismatches`, `proportion_mismatches`, and
`next_corrections` as optional machine-readable fields for later correction
loops.

---

## Objective

Define one reusable machine-readable envelope for all vision-assist outputs.

---

## Implementation Direction

- include fields such as:
  - `status`
  - `backend_kind`
  - `backend_name`
  - `model_name`
  - `goal_summary`
  - `reference_match_summary`
  - `visible_changes`
  - `likely_issues`
  - `recommended_checks`
  - `confidence`
  - `input_summary`
  - optional `captures_used`
- keep the output concise and structured enough for macro/workflow reports
- align status handling with existing assistant-style product semantics where useful
- make the envelope backend-agnostic so the same contract works for:
  - local `transformers` runtimes
  - external OpenAI-compatible vision endpoints

---

## Repository Touchpoints

- `server/adapters/mcp/contracts/`
- `server/adapters/mcp/sampling/result_types.py`
- `tests/unit/adapters/mcp/`

---

## Acceptance Criteria

- vision-assisted outputs do not require ad hoc per-tool payloads
- later macro/workflow integrations can attach vision results without redesign
