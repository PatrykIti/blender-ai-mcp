# TASK-091: Versioned Client Surfaces for Safe API Evolution

**Priority:** 🔴 High  
**Category:** FastMCP Platform  
**Estimated Effort:** Medium  
**Dependencies:** TASK-083, TASK-086, TASK-089  
**Status:** ⬜ To Do

---

## Objective

Evolve the public MCP product surface safely by supporting more than one server surface at the same time.

---

## Problem

The project needs to improve how it presents tools to LLMs, but a hard cut-over creates real risk:

- existing clients may expect the current tool surface
- prompt libraries may depend on current names and flows
- internal and external users may migrate at different speeds
- future LLM-optimized surfaces may intentionally differ from legacy ones

Without a versioning strategy, every public-surface improvement becomes a coordination problem.

---

## Business Outcome

Allow the project to move faster without forcing all consumers to migrate at once.

This enables:

- stable legacy support
- new LLM-optimized surfaces
- safer experimentation
- staged rollout of new discovery and interaction models

---

## Proposed Solution

Use FastMCP versioned components and filtered server surfaces to expose different product variants intentionally.

Examples of business-level use cases:

- legacy flat surface for compatibility
- curated `llm-guided` surface for modern clients
- future expert or internal surface for power workflows

This is not only about backwards compatibility. It is also a strategic enabler for product evolution.

---

## Implementation Constraints

Follow [FASTMCP_3X_IMPLEMENTATION_MODEL.md](./FASTMCP_3X_IMPLEMENTATION_MODEL.md).

This task must preserve the distinction between:

- surface profile: which surface is booted
- contract version: which public contract version a capability exposes

Profiles and versions should work together, not become two competing configuration systems.

Public contract versioning should start only after:

- the naming and public contract baseline exists
- the adapter contract model exists for structured-first payloads

This prevents versioning unstable aliases or half-defined response contracts.

---

## FastMCP Features To Use

- **Component Versioning** — **FastMCP 3.0.0**
- **VersionFilter** — **FastMCP 3.0.0**

---

## Scope

This task covers:

- coexistence of multiple public server surfaces
- safer migration strategy
- compatibility management
- staged adoption of `llm-guided` contract lines and related public-surface changes

This task does not cover:

- per-session adaptation
- search-based discovery itself

---

## Why This Matters For Blender AI

This project is moving from “many tools are available” toward “the right surface is presented to the right client.”

That transition is much easier when different surfaces can coexist intentionally rather than replacing one another abruptly.

---

## Success Criteria

- The project can expose more than one public API surface safely.
- New LLM-optimized designs do not require a destructive migration.
- Compatibility becomes a product capability instead of a release risk.
- Future experimentation becomes easier to manage.

---

## Umbrella Execution Notes

This remains the umbrella task. The original scope stays unchanged.

### Atomic Delivery Waves

1. Define the surface matrix and contract-line lifecycle rules.
2. Assign baseline versions to shared provider components before introducing alternate versions.
3. Compose profile-specific surfaces through built-in `VersionFilter`.
4. Expose surface-profile and contract-line selection through bootstrap config.
5. Add coexistence tests and migration guidance for maintainers and clients.

Implementation is decomposed into:

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-091-01](./TASK-091-01_Versioning_Policy_and_Surface_Matrix.md) | Define the surface matrix and version lifecycle |
| 2 | [TASK-091-02](./TASK-091-02_Shared_Providers_with_Component_Versions.md) | Add component versions on shared providers |
| 3 | [TASK-091-03](./TASK-091-03_Version_Filtered_Server_Composition.md) | Compose surfaces through VersionFilter |
| 4 | [TASK-091-04](./TASK-091-04_Client_Selection_and_Bootstrap_Configuration.md) | Select surface variants through bootstrap and config |
| 5 | [TASK-091-05](./TASK-091-05_Versioned_Surface_Tests_and_Documentation.md) | Add coexistence tests and migration docs |
