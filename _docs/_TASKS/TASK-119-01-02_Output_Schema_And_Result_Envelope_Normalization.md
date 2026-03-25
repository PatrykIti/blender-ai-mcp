# TASK-119-01-02: Output Schema and Result Envelope Normalization

**Parent:** [TASK-119-01](./TASK-119-01_Public_Tool_Semantics_And_Contract_Hardening.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

---

## Objective

Reduce drift in result shape and output-schema exposure across grouped/high-value
public tools.

---

## Implementation Direction

- inventory public/grouped tools that still have inconsistent structured payloads,
  legacy text-heavy paths, or weak output-schema declarations
- normalize shared fields such as:
  - `action`
  - `payload`
  - `error`
  - optional `assistant`
- review whether more grouped/public tools should move into the
  `structured-first` contract set
- keep compatibility behavior explicit instead of accidental

---

## Repository Touchpoints

- `server/adapters/mcp/contracts/*.py`
- `server/adapters/mcp/contracts/compat.py`
- `server/adapters/mcp/areas/*.py`
- `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- `tests/unit/adapters/mcp/test_delivery_strategy.py`

---

## Acceptance Criteria

- grouped/high-value public tools expose predictable machine-readable envelopes
- output-schema and delivery-policy drift are covered by regression tests
