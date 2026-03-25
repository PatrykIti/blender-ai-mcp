# TASK-120-01-02: Shared Macro Report Envelope and Status Vocabulary

**Parent:** [TASK-120-01](./TASK-120-01_Macro_Candidate_Matrix_And_Shared_Contract.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

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

- `server/adapters/mcp/contracts/`
- `server/adapters/mcp/areas/`
- `tests/unit/tools/`
- `tests/unit/adapters/mcp/`

---

## Acceptance Criteria

- first-wave macro tools can share one stable result contract
- later vision/report additions do not require per-macro ad hoc payload redesign
