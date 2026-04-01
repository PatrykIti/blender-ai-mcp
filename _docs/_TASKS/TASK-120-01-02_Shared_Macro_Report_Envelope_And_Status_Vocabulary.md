# TASK-120-01-02: Shared Macro Report Envelope and Status Vocabulary

**Parent:** [TASK-120-01](./TASK-120-01_Macro_Candidate_Matrix_And_Shared_Contract.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** A shared macro report envelope now exists in code/tests under `server/adapters/mcp/contracts/macro.py`, covering bounded actions taken, modified/created objects, verification recommendations, follow-up state, and future assistant integration.

---

## Objective

Define one machine-readable report envelope for macro tools so they can be
searched, compared, verified, and later vision-augmented consistently.

---

## Implementation Direction

- define shared macro fields such as:
  - `status`
  - `macro_name`
  - `intent`
  - `actions_taken`
  - `objects_created`
  - `objects_modified`
  - `verification_recommended`
  - `requires_followup`
  - optional `assistant`
- keep macro reports bounded and process-oriented, not prose-heavy
- design for compatibility with later before/after capture and vision-assist layers

---

## Repository Touchpoints

- `server/adapters/mcp/contracts/macro.py`
- `server/adapters/mcp/contracts/__init__.py`
- `server/adapters/mcp/areas/`
- `tests/unit/adapters/mcp/test_macro_contracts.py`
- `tests/unit/tools/`
- `tests/unit/adapters/mcp/`

---

## Acceptance Criteria

- first-wave macro tools can share one stable result contract
- later vision/report additions do not require per-macro ad hoc payload redesign

## Contract Direction Implemented

The shared macro report envelope now includes:

- `status`
- `macro_name`
- `intent`
- `actions_taken`
- `objects_created`
- `objects_modified`
- `verification_recommended`
- `requires_followup`
- optional `error`
- optional `assistant`

Action records and verification recommendations are also typed so later macro
tools can stay machine-readable and comparable.
