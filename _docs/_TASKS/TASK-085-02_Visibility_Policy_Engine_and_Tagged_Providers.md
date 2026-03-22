# TASK-085-02: Visibility Policy Engine and Tagged Providers

**Parent:** [TASK-085](./TASK-085_Session_Adaptive_Tool_Visibility.md)  
**Status:** 🚧 In Progress  
**Priority:** 🔴 High  
**Depends On:** [TASK-085-01](./TASK-085-01_Session_State_Model_and_Capability_Phases.md), [TASK-083-04](./TASK-083-04_Transform_Pipeline_Baseline.md), [TASK-084-01](./TASK-084-01_Tool_Inventory_Normalization_and_Discovery_Taxonomy.md)

---

## Objective

Implement deterministic visibility filtering around component tags, audience, and session phase, starting with the small guided entry surface instead of the full catalog.

---

## Planned Work

- create:
  - `server/adapters/mcp/transforms/visibility_policy.py`
  - `server/adapters/mcp/visibility/tags.py`
  - `tests/unit/adapters/mcp/test_visibility_policy.py`
- introduce tags such as:
  - `phase:planning`
  - `phase:build`
  - `phase:inspect_validate`
  - `audience:legacy`
  - `audience:llm`
  - `entry:guided`

### Ownership Rule

Visibility tags should come from the shared platform capability manifest and provider registration.
Router metadata may inform policy, but it is not the canonical visibility registry.

### Phase Taxonomy Rule

Use the canonical phase vocabulary from TASK-085-01.
For the first rollout, activate only the subset `planning`, `build`, and `inspect_validate` on top of the implicit `bootstrap` default.

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

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-085-02-01](./TASK-085-02-01_Core_Visibility_Engine_Tagged_Providers.md) | Core Visibility Policy Engine and Tagged Providers | Core implementation layer |
| [TASK-085-02-02](./TASK-085-02-02_Tests_Visibility_Engine_Tagged_Providers.md) | Tests and Docs Visibility Policy Engine and Tagged Providers | Tests, docs, and QA |

---

## Acceptance Criteria

- visibility rules are deterministic and testable
- provider tags become the canonical grouping mechanism for visibility decisions
- the first implementation operates on the guided entry surface before expanding to the deeper catalog
- the first implementation uses canonical phase tags rather than alternate labels such as `phase:inspect`

---

## Atomic Work Items

1. Materialize profile, audience, phase, and entry-surface tags on provider components.
2. Implement one deterministic visibility policy function.
3. Apply the policy first to `router_*`, `workflow_catalog`, and other small entry capabilities.
4. Leave the deeper catalog reachable through profile defaults and/or search until later expansion is justified.
5. Add tests for profile-only visibility, phase-only visibility, and pinned-tool exceptions.
