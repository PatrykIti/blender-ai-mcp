# TASK-092-03-01: Core Inspection Summarizer and Repair Suggester Assistants

**Parent:** [TASK-092-03](./TASK-092-03_Inspection_Summarizer_and_Repair_Suggester_Assistants.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-092-02](./TASK-092-02_Assistant_Runner_with_Typed_Result_Wrappers.md)

---

## Objective

Implement the core code changes for **Inspection Summarizer and Repair Suggester Assistants**.

---

## Repository Touchpoints

- `server/application/tool_handlers/scene_handler.py`
- `server/application/tool_handlers/mesh_handler.py`
- `server/router/application/router.py`

---

## Planned Work

### Slice Outputs

- enforce bounded sampling usage with explicit masking and budget controls
- keep assistant outputs typed and policy-gated
- prevent assistant paths from bypassing router safety or inspection truth layers

### Implementation Checklist

- touch `server/application/tool_handlers/scene_handler.py` with explicit change notes and boundary rationale
- touch `server/application/tool_handlers/mesh_handler.py` with explicit change notes and boundary rationale
- touch `server/router/application/router.py` with explicit change notes and boundary rationale
- add or update focused regression coverage for the slice behavior
- capture before/after evidence tied to the slice outputs

### Review Notes To Attach

- rationale per changed touchpoint and any explicit no-change decisions
- exact test commands and profile/config context used during validation
- deferred work list with safety rationale

---

## Acceptance Criteria

- assistant behavior is request-bound, typed, and policy-compliant
- masking and budget limits are deterministic and test-covered
- fallback behavior is explicit when sampling is unavailable or blocked
- no boundary violations relative to semantic/safety/truth split

---

## Atomic Work Items

1. Implement bounded assistant behavior and policy hooks in listed touchpoints.
2. Add tests for available, unavailable, masked, and budget-exceeded paths.
3. Capture typed output examples for each terminal assistant status.
4. Document allowed/forbidden assistant responsibilities for this slice.
