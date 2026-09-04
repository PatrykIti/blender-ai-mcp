# TASK-094: Code Mode Exploration for Large-Scale Orchestration

**Priority:** 🟡 Medium  
**Category:** FastMCP Research  
**Estimated Effort:** Medium  
**Dependencies:** TASK-083 (platform baseline). Optional comparison input: TASK-084 (search-first discovery baseline, when available).
**Status:** ✅ Done

**Completion Summary:** Benchmark baselines are named explicitly as `legacy-flat`, `llm-guided`, and `code-mode-pilot`. The experimental `code-mode-pilot` surface is implemented with explicit guardrails, a read-only allowlist, FastMCP `CodeMode`, prompt bridge support, fail-fast sandbox dependency checks, benchmark harness coverage, and an explicit go/no-go recommendation. The result is a go for an opt-in read-only pilot and a no-go for making Code Mode the default path for write/destructive Blender work.

---

## Objective

Evaluate whether FastMCP Code Mode can improve orchestration efficiency for very large or very analytical Blender server interactions.

---

## Problem

Classic MCP tool loops have two known scaling costs:

- the model sees too much catalog upfront
- every intermediate tool result flows back through the outer context window

For Blender creation workflows, that can become expensive when the model needs to:

- inspect multiple objects
- compare intermediate states
- chain many read operations before deciding what to do

This does not automatically mean Code Mode should become the default. It does mean it is worth evaluating as a controlled product experiment.

---

## Business Outcome

Understand whether a code-driven orchestration mode can provide real value for:

- very large catalogs
- advanced inspection workflows
- expert clients
- low-context, high-capability usage modes

This task is about evidence and product fit, not about committing blindly to an experimental feature.

---

## Proposed Solution

Run Code Mode as an optional laboratory surface and assess where it helps and where it does not.

The likely best-fit scenarios are:

- read-heavy discovery and analysis
- multi-step internal orchestration
- expert workflows with large catalogs

The likely bad-fit scenario is making it the default execution path for direct geometry-changing operations before the platform is fully proven.

---

## Implementation Constraints

Follow [FASTMCP_3X_IMPLEMENTATION_MODEL.md](./FASTMCP_3X_IMPLEMENTATION_MODEL.md).

For this repo, Code Mode should remain:

- explicit
- opt-in
- profile-scoped
- read-heavy first

Hard safety rule:

- Code Mode may orchestrate only the existing MCP product surface: tools, prompts, and resources exposed through the composed FastMCP server
- Code Mode must not expose or execute raw Blender Python, direct `bpy` snippets, arbitrary Python execution, shell commands, or any bypass path around the MCP tool contract

Code Mode research does not require search-first rollout to exist.
If TASK-084 is available, it should be used as the named `llm-guided` search-first comparison baseline, but it is not a prerequisite for experiment guardrails or the first read-only pilot surface.

Hard gate:

- TASK-094 implementation is blocked until TASK-083 Gate 0 is green (3.0+ baseline) and the runtime for this experimental surface is moved to a FastMCP 3.1+ feature line (`>=3.1,<4.0` unless explicitly revised).

It should not become the default write path for Blender mutations without a separate proof burden.

---

## FastMCP Features To Use

- **Code Mode** — **FastMCP 3.1.0**  
  Status note: official docs describe it as **experimental**

---

## Scope

This task covers:

- product evaluation of Code Mode
- identifying safe and useful usage scenarios
- understanding the tradeoff between classic tool calling and code-based orchestration

This task does not cover:

- making Code Mode the default for all clients
- replacing the router or all normal tools
- exposing raw Python or raw Blender execution as an orchestration shortcut

---

## Why This Matters For Blender AI

This repo is one of the kinds of servers where Code Mode could matter, because:

- the tool catalog is large
- the domain is stateful
- analysis often precedes action

But because Blender writes are high-impact, the feature should be treated carefully and validated against product goals rather than adopted automatically.

---

## Success Criteria

- The team has a clear answer on where Code Mode helps and where it should stay out of the critical path.
- Experimental value is separated from production-default decisions.
- The project gains a research path for lower-context orchestration at catalog scale.
- the experiment preserves the repo invariant that Blender work happens through explicit MCP capabilities rather than raw code execution

---

## Umbrella Execution Notes

This remains the umbrella task. The original scope stays unchanged.

### Atomic Delivery Waves

1. Define experiment guardrails and exclusion rules.
2. Build a read-only pilot surface on top of the same provider set.
3. Benchmark discovery and orchestration cost against explicit named baselines:
   - `legacy-flat`
   - `llm-guided`
   - `code-mode-pilot`
   `llm-guided` remains the primary modern comparison baseline; `legacy-flat` stays as compatibility/control context.
4. Record an explicit go/no-go decision with retained constraints.

Implementation is decomposed into:

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-094-01](./TASK-094-01_Code_Mode_Experiment_Design_and_Guardrails.md) | Define the experiment scope and safety guardrails |
| 2 | [TASK-094-02](./TASK-094-02_Read_Only_Code_Mode_Pilot_Surface.md) | Build a read-only pilot surface for Code Mode |
| 3 | [TASK-094-03](./TASK-094-03_Evaluation_Harness_and_Benchmark_Scenarios.md) | Benchmark Code Mode against classic tool loops |
| 4 | [TASK-094-04](./TASK-094-04_Decision_Memo_and_Documentation.md) | Record the outcome and final recommendation |
