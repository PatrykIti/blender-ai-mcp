# TASK-114-02: Surface, Prompt, and Goal-First Audit

**Parent:** [TASK-114](./TASK-114_Existing_Tool_Surface_Audit_And_Alignment.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** The first surface/prompt audit is complete. The repo now has an explicit record of where surface instructions and prompt assets still over-index on manual or legacy framing relative to the intended goal-first production model.

---

## Objective

Audit whether surfaces, prompt assets, and examples consistently enforce the new goal-first and macro/workflow-first model.

---

## Repository Touchpoints

- `server/adapters/mcp/surfaces.py`
- `_docs/_PROMPTS/*.md`
- `_docs/_MCP_SERVER/README.md`
- `README.md`

---

## Planned Work

- find places where manual/no-router usage is still overrepresented
- find places where `router_set_goal(...)` should be stronger or clearer
- find examples/prompts that still bias the model toward low-level manual tool selection

---

## Acceptance Criteria

- the repo has an explicit list of prompt/surface mismatches against the goal-first model

## Audit Findings

### P0

- `llm-guided` is correctly positioned as goal-first, but the instruction/prompt layer still needs a stronger macro/workflow-first tone in some places

### P1

- `legacy-flat` and `legacy-manual` are now described better than before, but more product-level differentiation still belongs in a later wording cleanup

### P1 Prompt Drift

- manual/no-router assets still dominate some demo/example pairings
- some prompt wording still reflects the old “manual fallback is normal” mindset more than the new “manual is an exception” posture

### Next Action

- keep the rewritten policy/instructions as baseline
- later rewrite demos and high-signal examples to default to workflow-first where appropriate
