# TASK-114-02-02: Prompt Asset and Demo Example Audit

**Parent:** [TASK-114-02](./TASK-114-02_Surface_Prompt_And_Goal_First_Audit.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** Prompt and demo-example drift is now documented. The biggest remaining issue is not the core production prompts, but which examples normalize manual/no-router usage and how strongly the demos default to workflow-first vs manual exception flows.

---

## Objective

Audit the prompt assets and demo prompts for remaining drift toward the old manual-first model.

---

## Exact Audit Targets

- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_PROMPTS/MANUAL_TOOLS_NO_ROUTER.md`
- `_docs/_PROMPTS/DEMO_TASK_GENERIC_MODELING.md`
- `_docs/_PROMPTS/DEMO_TASK_LOW_POLY_MEDIEVAL_WELL.md`

---

## Focus

- manual mode overuse
- insufficient `set_goal` emphasis
- missing verification/compare instructions
- examples that still normalize flat low-level tool selection

---

## Acceptance Criteria

- prompt-layer drift is documented with exact file/section targets

## Audit Result

### Good

- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
  - already strongly aligned with goal-first
- `_docs/_PROMPTS/MANUAL_TOOLS_NO_ROUTER.md`
  - now clearly marked as an exception surface

### Remaining Drift

- demo prompts still need a stronger default bias toward workflow-first
- prompt README still needs a later cleanup pass that makes manual/no-router feel even less like a normal first choice

### Priority

- `P0`: demo/example defaults
- `P1`: remaining wording polish in prompt README
