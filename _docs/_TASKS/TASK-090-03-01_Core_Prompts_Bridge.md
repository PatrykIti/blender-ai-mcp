# TASK-090-03-01: Core Prompts as Tools Bridge

**Parent:** [TASK-090-03](./TASK-090-03_Prompts_As_Tools_Bridge.md)  
**Status:** ✅ Done  
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
- expose canonical bridge tool names:
  - `list_prompts`
  - `get_prompt`
- define visibility and pinning rules for prompt bridge tools
- keep `list_prompts` pinned by default on tool-only `llm-guided` surfaces; keep `get_prompt` discoverable and pin only when profile UX requires it
---

## Acceptance Criteria

- tool-only clients can access prompt products without copying markdown outside the server
---

## Atomic Work Items

1. Implement PromptsAsTools bridge with canonical `list_prompts` and `get_prompt` names.
2. Implement deterministic pinning/visibility policy per surface profile without duplicate bridge aliases.
3. Keep the implementation aligned with the parent task boundaries and the existing runtime call path.
