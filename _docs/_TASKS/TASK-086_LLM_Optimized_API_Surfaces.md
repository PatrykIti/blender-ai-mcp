# TASK-086: LLM-Optimized API Surfaces

**Priority:** 🔴 High  
**Category:** FastMCP Tool UX  
**Estimated Effort:** Medium  
**Dependencies:** TASK-083  
**Status:** 🚧 In Progress

**Current State:** The first stable `llm-guided` public line is implemented and documented: manifest-owned public contracts exist, transform-based aliases and hidden-argument rules are live, dispatcher/router compatibility is tested, and public docs/prompts now describe the new surface. This umbrella remains open because the search-discovered/versioned parity slice still depends on TASK-084 and TASK-091.

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

## Implementation Constraints

Follow [FASTMCP_3X_IMPLEMENTATION_MODEL.md](./FASTMCP_3X_IMPLEMENTATION_MODEL.md).

This task should rely on built-in FastMCP public-surface shaping:

- `ToolTransform`
- `ArgTransform`
- profile-specific renderers and visibility

Do not fork business logic or duplicate router execution paths to create LLM-friendly naming.

This task establishes the first stable baseline public `llm-guided` contract line.
That line is:

- the public surface that TASK-084 discovery infrastructure should index
- the baseline public surface that TASK-091 later versions for coexistence and rollback

Do not wait for TASK-091 to create this baseline.
Versioning layers on after the baseline public line is clear enough to compare safely.

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

---

## Umbrella Execution Notes

This remains the umbrella task. The original scope stays unchanged.

### Atomic Delivery Waves

1. Define a platform-owned public naming and argument convention.
2. Apply aliasing and hidden-argument rules on the public surface only.
3. Simplify the LLM-guided surface while keeping expert and internal variants richer.
4. Prove dispatcher and router internals still operate on canonical internal names.
5. Add examples and QA cases focused on how LLMs choose and fill tools.

Implementation is decomposed into:

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-086-01](./TASK-086-01_Public_Surface_Manifest_and_Naming_Conventions.md) | Define the public surface manifest and naming rules |
| 2 | [TASK-086-02](./TASK-086-02_Transform_Based_Tool_and_Parameter_Aliasing.md) | Apply tool and parameter aliasing through transforms |
| 3 | [TASK-086-03](./TASK-086-03_LLM_First_Surface_Simplification_and_Hidden_Args.md) | Hide backend-only arguments and simplify the LLM-facing surface |
| 4 | [TASK-086-04](./TASK-086-04_Compatibility_Adapters_and_Dispatcher_Alignment.md) | Keep aliases compatible with router and dispatcher internals |
| 5 | [TASK-086-05](./TASK-086-05_Surface_QA_Examples_and_Documentation.md) | Add surface QA, examples, and documentation |
