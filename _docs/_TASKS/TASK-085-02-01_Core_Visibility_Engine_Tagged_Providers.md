# TASK-085-02-01: Core Visibility Policy Engine and Tagged Providers

**Parent:** [TASK-085-02](./TASK-085-02_Visibility_Policy_Engine_and_Tagged_Providers.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-085-01](./TASK-085-01_Session_State_Model_and_Capability_Phases.md), [TASK-083-04](./TASK-083-04_Transform_Pipeline_Baseline.md), [TASK-084-01](./TASK-084-01_Tool_Inventory_Normalization_and_Discovery_Taxonomy.md)

---

## Objective

Implement the core code changes for **Visibility Policy Engine and Tagged Providers**.

---

## Repository Touchpoints

- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/visibility/tags.py`
- `server/adapters/mcp/platform/capability_manifest.py`
- `server/adapters/mcp/providers/core_tools.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`

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

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-085-02-01-01](./TASK-085-02-01-01_Visibility_Tags_and_Manifest_Wiring.md) | Visibility Tags and Manifest Wiring | Core slice |
| [TASK-085-02-01-02](./TASK-085-02-01-02_Visibility_Transform_and_Policy_Engine.md) | Visibility Transform and Policy Engine | Core slice |

---

## Acceptance Criteria

- visibility rules are deterministic and testable
- provider tags become the canonical grouping mechanism for visibility decisions
- the first implementation scopes visibility adaptation to the guided entry surface
- the first implementation uses canonical phase tags rather than alternate labels such as `phase:inspect`

---

## Atomic Work Items

1. Materialize profile, audience, phase, and entry-surface tags on provider components.
2. Implement one deterministic visibility policy function.
3. Apply the policy first to `router_*`, `workflow_catalog`, and other entry capabilities.
4. Add tests for profile-only visibility, phase-only visibility, and pinned-tool exceptions.
