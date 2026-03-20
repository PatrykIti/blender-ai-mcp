# TASK-094: Code Mode Exploration for Large-Scale Orchestration

**Priority:** 🟡 Medium  
**Category:** FastMCP Research  
**Estimated Effort:** Medium  
**Dependencies:** TASK-083, TASK-084  
**Status:** ⬜ To Do

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

