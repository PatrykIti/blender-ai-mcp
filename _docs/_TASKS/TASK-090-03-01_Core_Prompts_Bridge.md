# TASK-090-03-01: Core Prompts as Tools Bridge

**Parent:** [TASK-090-03](./TASK-090-03_Prompts_As_Tools_Bridge.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-090-02](./TASK-090-02_FastMCP_Prompt_Provider_and_Rendering.md)

---

## Objective

Implement the core code changes for **Prompts as Tools Bridge**.

---

## Repository Touchpoints

- `server/adapters/mcp/transforms/prompts_bridge.py`
- `server/adapters/mcp/factory.py`
- `server/adapters/mcp/surfaces.py`
- `tests/unit/adapters/mcp/test_prompt_provider.py`
- `tests/unit/adapters/mcp/test_transform_pipeline.py`
---

## Planned Work

- use a `PromptsAsTools`-style transform
- define visibility and pinning rules for prompt bridge tools
---

## Acceptance Criteria

- tool-only clients can access prompt products without copying markdown outside the server
---

## Atomic Work Items

1. Implement the leaf scope in the listed touchpoints.
2. Keep the implementation aligned with the parent task boundaries and the existing runtime call path.
