# TASK-121-04-01: Small Vision Runtime Selection and Execution Policy

**Parent:** [TASK-121-04](./TASK-121-04_Lightweight_Vision_Runtime_And_Evaluation.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

---

## Objective

Choose the lightweight vision runtime/model path and define exactly how it may
run inside the product.

---

## Implementation Direction

- evaluate small vision-capable model/runtime options for:
  - before/after change interpretation
  - reference-image similarity guidance
  - likely-issue localization
- define execution policy:
  - request-bound only vs optional background
  - time/token/image limits
  - when vision is allowed on `llm-guided`
  - what data may be sent and stored
- align the runtime choice with repo ops constraints and product latency goals

---

## Repository Touchpoints

- `server/infrastructure/config.py`
- `server/adapters/mcp/sampling/`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TESTS/README.md`

---

## Acceptance Criteria

- one explicit lightweight runtime/model strategy is chosen
- runtime policy is documented before deep integration work continues
