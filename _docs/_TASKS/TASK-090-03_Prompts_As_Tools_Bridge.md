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
- use canonical bridge tool names exposed by the transform:
  - `list_prompts`
  - `get_prompt`
- define visibility and pinning rules for prompt bridge tools

### Pinning Rule

For tool-only `llm-guided` surfaces:

- keep `list_prompts` pinned as the discovery entry point
- keep `get_prompt` discoverable without forcing it into every pinned set unless profile UX requires it
- do not introduce duplicate custom bridge names for the same behavior

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-090-03-01](./TASK-090-03-01_Core_Prompts_Bridge.md) | Core Prompts as Tools Bridge | Core implementation layer |
| [TASK-090-03-02](./TASK-090-03-02_Tests_Prompts_Bridge.md) | Tests and Docs Prompts as Tools Bridge | Tests, docs, and QA |

---

## Acceptance Criteria

- tool-only clients can access prompt products without copying markdown outside the server
- bridge tool naming is explicit and stable (`list_prompts`, `get_prompt`)
