# TASK-086: LLM-Optimized API Surfaces

**Priority:** 🔴 High  
**Category:** FastMCP Tool UX  
**Estimated Effort:** Medium  
**Dependencies:** TASK-083  
**Status:** ⬜ To Do

---

## Objective

Create cleaner, more LLM-friendly public tool surfaces without rewriting the whole business layer underneath.

---

## Problem

A server can have strong internal tool design and still present a suboptimal public API to language models.

Typical issues include:

- names that are too implementation-oriented
- parameters that are too Blender-specific for the first interaction
- arguments that are technically correct but cognitively noisy
- multiple tools that should appear as one conceptual action to the model
- different clients needing different naming or surface conventions

These problems reduce tool selection quality even when the backend behavior is correct.

---

## Business Outcome

Separate the public LLM-facing API shape from the internal handler shape.

This allows the project to present:

- a simpler surface for general-purpose LLMs
- a richer expert surface for power users
- compatibility layers for older clients
- guided variants for workflow-first clients

without duplicating the underlying business capabilities.

---

## Proposed Solution

Use FastMCP tool transformation to reshape the public surface:

- rename tools for clearer intent
- rename parameters for more natural prompting
- hide backend-only arguments
- improve descriptions and examples
- create alternate views of the same capabilities for different client modes

The goal is not to change what the server can do, but to change how clearly the model understands what it can do.

---

## FastMCP Features To Use

- **Tool Transformation** — **FastMCP 3.0.0**
- **Tool transformation lineage introduced in v2** — **FastMCP 2.8.0**

---

## Scope

This task covers:

- public tool naming
- public argument naming and visibility
- differentiated API surfaces for different clients or modes
- product-level API clarity for LLMs

This task does not cover:

- adding brand new Blender features
- changing the addon’s core behavior

---

## Why This Matters For Blender AI

This project is serving models, not just developers.

LLM-facing API quality directly affects:

- whether the right tool is chosen
- whether the right arguments are supplied
- how much prompt scaffolding the user must add
- how often the router must compensate for bad first choices

Tool transformation is one of the cleanest ways to improve that without destabilizing the core system.

---

## Success Criteria

- The project can expose cleaner public tool surfaces than the raw internal surface.
- Tool and parameter naming become easier for LLMs to use correctly.
- Different clients can receive different API shapes without forking the business layer.
- The server becomes easier to productize for Blender creation workflows.

