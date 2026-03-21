# TASK-085-02: Visibility Policy Engine and Tagged Providers

**Parent:** [TASK-085](./TASK-085_Session_Adaptive_Tool_Visibility.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-085-01](./TASK-085-01_Session_State_Model_and_Capability_Phases.md), [TASK-083-04](./TASK-083-04_Transform_Pipeline_Baseline.md)

---

## Objective

Implement visibility filtering around component tags, audience, and session phase.

---

## Planned Work

- create:
  - `server/adapters/mcp/transforms/visibility_policy.py`
  - `server/adapters/mcp/visibility/tags.py`
  - `tests/unit/adapters/mcp/test_visibility_policy.py`
- introduce tags such as:
  - `phase:planning`
  - `phase:build`
  - `phase:repair`
  - `audience:legacy`
  - `audience:llm`
  - `risk:destructive`

---

## Pseudocode

```python
def is_visible(component, phase, profile):
    if profile == "legacy":
        return True
    if f"phase:{phase}" in component.tags:
        return True
    return component.name in profile.pinned_tools
```

---

## Acceptance Criteria

- visibility rules are deterministic and testable
- provider tags become the canonical grouping mechanism for visibility decisions
