# TASK-094-01-01: Core Code Mode Experiment Design and Guardrails

**Parent:** [TASK-094-01](./TASK-094-01_Code_Mode_Experiment_Design_and_Guardrails.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-083-04](./TASK-083-04_Transform_Pipeline_Baseline.md), [TASK-084-02](./TASK-084-02_Search_Transform_and_Pinned_Entry_Surface.md)

---

## Objective

Implement the core code changes for **Code Mode Experiment Design and Guardrails**.

---

## Repository Touchpoints

- `server/adapters/mcp/surfaces.py`
- `server/adapters/mcp/settings.py`
- `tests/unit/adapters/mcp/test_server_factory.py`
- `_docs/_MCP_SERVER/README.md`
---

## Planned Work

### Slice Outputs

- deliver explicit experimental Code Mode behavior with guardrails
- limit pilot surface to approved read-heavy workflows
- produce measurable comparison artifacts against classic tool loops
- preserve the repo invariant that Code Mode orchestrates MCP capabilities only and never opens raw Python / Blender execution

### Implementation Checklist

- touch `server/adapters/mcp/surfaces.py` with explicit change notes and boundary rationale
- touch `server/adapters/mcp/settings.py` with explicit change notes and boundary rationale
- touch `tests/unit/adapters/mcp/test_server_factory.py` with explicit change notes and boundary rationale
- touch `_docs/_MCP_SERVER/README.md` with explicit change notes and boundary rationale
- add or update focused regression coverage for the slice behavior
- capture before/after evidence tied to the slice outputs
- make the raw-execution ban explicit in both code-facing config and operator-facing docs

### Review Notes To Attach

- rationale per changed touchpoint and any explicit no-change decisions
- exact test commands and profile/config context used during validation
- deferred work list with safety rationale

---

## Acceptance Criteria

- code-mode experiment boundaries are explicit and enforceable
- write/destructive operations are blocked where required
- raw Python / `bpy` execution is unavailable on the experiment surface
- benchmark artifacts are reproducible and linked to recommendations
- slice remains profile-scoped and opt-in only

---

## Atomic Work Items

1. Implement pilot/benchmark/documentation behavior in listed touchpoints.
2. Add tests for guardrail enforcement and discovery/execution flow.
3. Capture benchmark metrics vs classic tool-loop baseline.
4. Document go/no-go criteria and retained constraints.
