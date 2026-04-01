# TASK-120-04-02: Prompt, Instruction, and Workflow Integration

**Parent:** [TASK-120-04](./TASK-120-04_Macro_Validation_And_Adoption.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** The public teaching surface now presents the macro layer as the normal bounded working layer: `llm-guided` runtime instructions explicitly recommend `macro_cutout_recess`, `macro_relative_layout`, and `macro_finish_form` before manual atomic chains, prompt templates now show macro-first examples for cutout/layout/finish flows, and public surface doc tests lock those examples in place.

---

## Objective

Make macro tools the natural working layer in prompts, guided instructions, and
workflow-oriented examples.

---

## Implementation Direction

- update `llm-guided` instructions to mention macro tools before atomics
- update prompt assets and examples so models learn:
  - goal-first
  - macro-first
  - verification-aware
- review where existing workflows should call or recommend macro tools instead of
  repeating raw atomic sequences in user-facing guidance

---

## Repository Touchpoints

- `server/adapters/mcp/surfaces.py`
- `_docs/_PROMPTS/*.md`
- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

---

## Acceptance Criteria

- macro tools are part of the normal public teaching surface
- users and models no longer need to infer the intended mid-layer from code alone
