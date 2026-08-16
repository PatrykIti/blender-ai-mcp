# TASK-114: Existing Tool Surface Audit and Alignment

**Priority:** 🔴 High  
**Category:** Product Audit / Tool Surface Hardening  
**Estimated Effort:** Medium  
**Dependencies:** TASK-113  
**Status:** ✅ Done

**Completion Summary:** The existing-tool audit is complete. The repo now has explicit findings for public tool semantics, prompt/surface drift, metadata/discovery drift, verification/truth-model gaps, and a prioritized follow-up plan for wording fixes plus the first measure/assert code wave.

---

## Objective

Audit the existing MCP tool surface, tool docstrings, prompt guidance, and supporting docs against the new architecture defined in `TASK-113`, then produce a concrete, execution-ready backlog of fixes.

---

## Business Problem

The repo now has a clear strategy:

- layered tools (`atomic` / `macro` / `workflow`)
- small public LLM-facing surfaces
- hidden atomic layer
- `set_goal`-first production flow
- vision as interpretation support
- measure/assert as the truth layer

But large parts of the existing tool surface were authored before that strategy existed.

This creates product drift:

- some tool docstrings still imply the old flat-catalog mindset
- some surfaces/prompts still teach low-level manual-first behavior too aggressively
- some “mega tool” descriptions are still too loose or too old in wording
- some tools expose old semantics that no longer match the intended public model
- the repo still lacks one explicit audit pass that turns these mismatches into a prioritized execution backlog

Without this audit, later work on new atomic measure/assert tools and macro/workflow tools will pile on top of an inconsistent product surface.

---

## Business Outcome

If this task is done correctly, the repo gains:

- one explicit picture of where current tools still violate or lag behind `TASK-113`
- a prioritized backlog of concrete fixes to existing tools before adding more tools
- less semantic drift between code, docs, prompts, metadata, and surface policy
- a cleaner handoff into the next code waves:
  - existing tool fixes first
  - then new measure/assert atomics
  - then new macro/workflow tools

---

## Scope

This task covers:

- audit of existing MCP-facing tool semantics
- audit of tool docstrings and public descriptions
- audit of prompt guidance and surface instructions
- audit of router metadata wording/examples
- audit of public-vs-hidden classification drift
- creation of a concrete fix backlog

This task does not itself deliver all code fixes.
It prepares the execution backlog for those fixes.

---

## Success Criteria

- the repo has one explicit audit of where existing tools still reflect the old architecture
- the audit is broken into concrete technical areas instead of one vague “clean this up later”
- the next execution waves after the audit are clear and sequenced

---

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-114-01](./TASK-114-01_Public_Tool_Semantics_And_Docstring_Audit.md) | Audit MCP-facing tool semantics and docstrings against the new product model |
| 2 | [TASK-114-02](./TASK-114-02_Surface_Prompt_And_Goal_First_Audit.md) | Audit prompts, surface instructions, and goal-first consistency |
| 3 | [TASK-114-03](./TASK-114-03_Metadata_Discovery_And_Public_Surface_Audit.md) | Audit router metadata, discovery wording, and public-vs-hidden classification drift |
| 4 | [TASK-114-04](./TASK-114-04_Verification_And_Truth_Model_Audit.md) | Audit current verification/truth semantics vs the new measure/assert model |
| 5 | [TASK-114-05](./TASK-114-05_Prioritized_Fix_Backlog_And_Code_Wave_Plan.md) | Produce the prioritized execution backlog and next code-wave order |
