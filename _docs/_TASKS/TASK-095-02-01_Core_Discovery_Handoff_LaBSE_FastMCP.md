# TASK-095-02-01: Core Discovery Handoff from LaBSE to FastMCP Search

**Parent:** [TASK-095-02](./TASK-095-02_Discovery_Handoff_From_LaBSE_to_FastMCP_Search.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-084-02](./TASK-084-02_Search_Transform_and_Pinned_Entry_Surface.md)

---

## Objective

Implement the core code changes for **Discovery Handoff from LaBSE to FastMCP Search**.

---

## Repository Touchpoints

- `server/adapters/mcp/transforms/discovery.py`
- `server/adapters/mcp/platform/capability_manifest.py`
- `server/adapters/mcp/factory.py`
- `server/router/application/classifier/intent_classifier.py`
- `tests/unit/adapters/mcp/test_tool_inventory.py`
---

## Planned Work

### Slice Outputs

- move target decisions from semantic inference to platform/inspection ownership
- harden allowed LaBSE roles for workflow/parameter semantics only
- surface boundary enforcement through tests and telemetry markers

### Implementation Checklist

- touch `server/adapters/mcp/transforms/discovery.py` with explicit change notes and boundary rationale
- touch `server/adapters/mcp/platform/capability_manifest.py` with explicit change notes and boundary rationale
- touch `server/adapters/mcp/factory.py` with explicit change notes and boundary rationale
- touch `server/router/application/classifier/intent_classifier.py` with explicit change notes and boundary rationale
- touch `tests/unit/adapters/mcp/test_tool_inventory.py` with explicit change notes and boundary rationale
- add or update focused regression coverage for the slice behavior
- capture before/after evidence tied to the slice outputs

### Review Notes To Attach

- rationale per changed touchpoint and any explicit no-change decisions
- exact test commands and profile/config context used during validation
- deferred work list with safety rationale

---

## Acceptance Criteria

- semantic boundary rules are explicit and enforced in code paths
- discovery/truth responsibilities are not delegated to LaBSE
- boundary violations are detectable in regression tests and telemetry
- slice preserves multilingual semantic benefits in allowed scope

---

## Atomic Work Items

1. Implement boundary enforcement changes in listed touchpoints.
2. Add tests for allowed-role and forbidden-role behaviors.
3. Capture one before/after decision trace showing ownership handoff.
4. Document boundary rationale and operational implications.
