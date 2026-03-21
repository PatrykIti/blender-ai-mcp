# TASK-090-03: Prompts as Tools Bridge

**Parent:** [TASK-090](./TASK-090_Prompt_Layer_and_Tool_Compatible_Prompts.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-090-02](./TASK-090-02_FastMCP_Prompt_Provider_and_Rendering.md)

---

## Objective

Expose prompt assets safely to tool-only clients through a prompt-as-tools bridge.

---

## Planned Work

- use a `PromptsAsTools`-style transform
- define visibility and pinning rules for prompt bridge tools

---

## Acceptance Criteria

- tool-only clients can access prompt products without copying markdown outside the server
