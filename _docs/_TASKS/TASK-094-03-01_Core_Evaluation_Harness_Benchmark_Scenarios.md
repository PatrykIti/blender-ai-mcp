# TASK-094-03-01: Core Evaluation Harness and Benchmark Scenarios

**Parent:** [TASK-094-03](./TASK-094-03_Evaluation_Harness_and_Benchmark_Scenarios.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-094-02](./TASK-094-02_Read_Only_Code_Mode_Pilot_Surface.md)

---

## Objective

Implement the core code changes for **Evaluation Harness and Benchmark Scenarios**.

---

## Repository Touchpoints

- `tests/unit/adapters/mcp/test_server_factory.py`
- `tests/unit/adapters/mcp/test_prompt_provider.py`
- `_docs/_MCP_SERVER/README.md`
---

## Planned Work

### Slice Outputs

- deliver explicit experimental Code Mode behavior with guardrails
- limit pilot surface to approved read-heavy workflows
- produce measurable comparison artifacts against explicit named baselines:
  - `legacy-flat`
  - `llm-guided`
  - `code-mode-pilot`

### Implementation Checklist

- touch `tests/unit/adapters/mcp/test_server_factory.py` with explicit change notes and boundary rationale
- touch `tests/unit/adapters/mcp/test_prompt_provider.py` with explicit change notes and boundary rationale
- touch `_docs/_MCP_SERVER/README.md` with explicit change notes and boundary rationale
- add or update focused regression coverage for the slice behavior
- capture before/after evidence tied to the slice outputs

### Review Notes To Attach

- rationale per changed touchpoint and any explicit no-change decisions
- exact test commands and profile/config context used during validation
- deferred work list with safety rationale

---

## Acceptance Criteria

- code-mode experiment boundaries are explicit and enforceable
- write/destructive operations are blocked where required
- benchmark artifacts are reproducible and linked to recommendations
- slice remains profile-scoped and opt-in only

---

## Atomic Work Items

1. Implement pilot/benchmark/documentation behavior in listed touchpoints.
2. Add tests for guardrail enforcement and discovery/execution flow.
3. Capture benchmark metrics vs classic tool-loop baseline.
4. Document go/no-go criteria and retained constraints.
