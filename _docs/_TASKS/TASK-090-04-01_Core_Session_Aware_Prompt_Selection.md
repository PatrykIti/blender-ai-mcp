# TASK-090-04-01: Core Session-Aware Prompt Selection

**Parent:** [TASK-090-04](./TASK-090-04_Session_Aware_Prompt_Selection.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-085-01](./TASK-085-01_Session_State_Model_and_Capability_Phases.md), [TASK-090-02](./TASK-090-02_FastMCP_Prompt_Provider_and_Rendering.md)

---

## Objective

Implement the core code changes for **Session-Aware Prompt Selection**.

---

## Repository Touchpoints

- `server/adapters/mcp/prompts/prompt_catalog.py`
- `server/adapters/mcp/prompts/provider.py`
- `server/adapters/mcp/session_state.py`
- `server/adapters/mcp/context_utils.py`
- `tests/unit/adapters/mcp/test_prompt_provider.py`
---

## Planned Work

- add prompt tags such as:
  - `phase:planning`
  - `phase:inspect_validate`
  - `profile:llm-guided`
- expose recommended prompts by phase or profile
---

## Acceptance Criteria

- the prompt layer reacts to session context instead of behaving like a flat static library
---

## Atomic Work Items

1. Align prompt profile tags with the canonical surface profile names.
2. Add one recommendation path by canonical phase and one by profile.
3. Add tests that prompt recommendations change when session phase changes.
