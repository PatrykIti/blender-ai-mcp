# TASK-113: Tool Layering, Goal-First, and Vision-Assertion Strategy

**Priority:** 🔴 High  
**Category:** Product Strategy / MCP Surface Architecture  
**Estimated Effort:** Large  
**Dependencies:** TASK-084, TASK-085, TASK-086, TASK-090, TASK-091, TASK-112  
**Status:** ⏳ To Do

---

## Objective

Replace the remaining flat-catalog / tool-first operating model with one coherent product strategy for:

- tool layering (`atomic` / `macro` / `workflow`)
- small public LLM-facing surfaces
- `set_goal`-first orchestration
- vision-assisted before/after analysis
- measurement/assertion as the source of truth
- documentation and governance updates across `_docs/`

---

## Why This Matters

The repo now has enough low-level power that the limiting factor is no longer “can the server do it?”

The limiting factor is:

- can the LLM choose the right level of abstraction?
- can the LLM verify whether a result is actually correct?
- can the public MCP surface stay small enough to be reliable?
- can operators and future contributors understand the intended tool architecture without reconstructing it from old docs?

The old flat-catalog approach leaks too much low-level detail into normal LLM usage. The new strategy should make the product surface intentional, layered, and explicitly goal-aware.

---

## Business Outcome

If this task is done correctly, the repo should move toward:

- fewer wrong low-level tool choices by LLMs
- higher success rate on proportion/alignment/contact-sensitive tasks
- better use of vision without treating vision as the truth source
- better maintainability for future contributors
- clearer product rules for which tools belong on public surfaces vs hidden/internal layers

---

## Target Product Model

### 1. Atomic Tools

Small, deterministic, precise.

Used as the implementation substrate.
Usually hidden from normal LLM-facing surfaces.

### 2. Macro Tools

Task-oriented operations composed from atomic tools.

These should become the normal working layer for LLMs.

### 3. Workflow / Mega Tools

Bounded multi-step process tools for one domain/process.

These should orchestrate atomic + macro tools, apply rules, and return structured reports.
They are not “do anything” tools.

### 4. Goal-First Orchestration

Normal production LLM surfaces should begin from `router_set_goal(...)`.

The MCP server should know:

- what the LLM is trying to build/fix
- which phase it is in
- what verification context to apply
- what visual analysis should be interpreted against the active goal

### 5. Vision + Measure + Assert

Vision should help interpret change, but it should not be the final truth source.

Truth should come from deterministic measurement/assertion tools:

- dimensions
- distance
- gap/contact
- overlap/intersection
- alignment
- proportion
- symmetry

---

## Scope

This umbrella covers:

- policy and terminology
- surface/profile exposure rules
- goal-first orchestration rules
- macro/workflow tool design rules
- vision/multiview/compare strategy
- measure/assert tool family planning
- prompt and instruction rewrite plan
- `_docs/` migration map and implementation rollout sequencing

This umbrella does **not** itself deliver all code changes.
It defines the governing policy and execution map for the next product wave.

---

## Success Criteria

- the repo has one explicit, canonical policy for tool layering and public-surface design
- future docs stop implying that flat public tool exposure is the preferred model
- production-oriented surfaces are explicitly designed around small public catalogs and goal-first behavior
- measurement/assertion and vision boundaries are documented before new tool waves are implemented
- documentation migration is decomposed enough that context cannot be lost between implementation waves

---

## Umbrella Execution Notes

This umbrella should be executed in the following order:

1. establish policy and terminology
2. define surface exposure and goal-first rules
3. define macro/workflow and vision/assertion design rules
4. map exact documentation migration targets
5. only then roll through code/tool migrations

Implementation is decomposed into:

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-113-01](./TASK-113-01_Tool_Layering_Policy_And_Terminology.md) | Canonical policy doc, ownership, terminology, and historical supersession rules |
| 2 | [TASK-113-02](./TASK-113-02_Surface_Exposure_Matrix_And_Hidden_Atomic_Layer.md) | Public/private tool exposure matrix, visibility, discovery, and escape-hatch rules |
| 3 | [TASK-113-03](./TASK-113-03_Goal_First_Orchestration_And_Session_Contract.md) | `set_goal`-first policy, router/session contract, and vision context handoff |
| 4 | [TASK-113-04](./TASK-113-04_Macro_And_Workflow_Tool_Design_Rules.md) | Macro/workflow design rules, bounded mega-tool contracts, and structured reporting |
| 5 | [TASK-113-05](./TASK-113-05_Vision_Measurement_And_Assertion_Layer.md) | Vision boundaries, before/after multiview contracts, and measure/assert tool family |
| 6 | [TASK-113-06](./TASK-113-06_Surface_Instructions_And_Prompt_Layer_Rewrite.md) | Rework instructions and prompt library around the new tool model |
| 7 | [TASK-113-07](./TASK-113-07_Documentation_Migration_And_Delivery_Roadmap.md) | Exact `_docs/` migration map, historical banner strategy, and implementation waves |
