# TASK-090-04: Session-Aware Prompt Selection

**Parent:** [TASK-090](./TASK-090_Prompt_Layer_and_Tool_Compatible_Prompts.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-085-01](./TASK-085-01_Session_State_Model_and_Capability_Phases.md), [TASK-090-02](./TASK-090-02_FastMCP_Prompt_Provider_and_Rendering.md)

---

## Objective

Make prompt selection depend on session phase and client profile.

---

## Planned Work

- add prompt tags such as:
  - `phase:planning`
  - `phase:repair`
  - `profile:llm-guided`
- expose recommended prompts by phase or profile

---

## Acceptance Criteria

- the prompt layer reacts to session context instead of behaving like a flat static library

---

## Atomic Work Items

1. Align prompt profile tags with the canonical surface profile names.
2. Add one recommendation path by phase and one by profile.
3. Add tests that prompt recommendations change when session phase changes.
