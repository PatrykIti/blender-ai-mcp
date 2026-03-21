# TASK-094-02-01: Core Read-Only Code Mode Pilot Surface

**Parent:** [TASK-094-02](./TASK-094-02_Read_Only_Code_Mode_Pilot_Surface.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-094-01](./TASK-094-01_Code_Mode_Experiment_Design_and_Guardrails.md)

---

## Objective

Implement the core code changes for **Read-Only Code Mode Pilot Surface**.

---

## Repository Touchpoints

- `server/adapters/mcp/factory.py`
- `server/adapters/mcp/surfaces.py`
- `server/adapters/mcp/settings.py`
- `server/adapters/mcp/transforms/discovery.py`
- `tests/unit/adapters/mcp/test_server_factory.py`

---

## Planned Work

### Slice Outputs

- deliver explicit experimental Code Mode behavior with guardrails
- limit pilot surface to approved read-heavy workflows
- produce measurable comparison artifacts against classic tool loops

### Implementation Checklist

- touch `server/adapters/mcp/factory.py` with explicit change notes and boundary rationale
- touch `server/adapters/mcp/surfaces.py` with explicit change notes and boundary rationale
- touch `server/adapters/mcp/settings.py` with explicit change notes and boundary rationale
- touch `server/adapters/mcp/transforms/discovery.py` with explicit change notes and boundary rationale
- touch `tests/unit/adapters/mcp/test_server_factory.py` with explicit change notes and boundary rationale
- add or update focused regression coverage for the slice behavior
- capture before/after evidence tied to the slice outputs

### Layer Boundary Rule

Keep this slice in MCP platform composition.
Do not rewrite scene/mesh/workflow handlers only to make Code Mode read-only.

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
- business handler logic remains unchanged unless a separate domain task explicitly requires it

---

## Atomic Work Items

1. Implement pilot/benchmark/documentation behavior in listed MCP platform touchpoints.
2. Add tests for guardrail enforcement and discovery/execution flow.
3. Capture benchmark metrics vs classic tool-loop baseline.
4. Document go/no-go criteria and retained constraints.
