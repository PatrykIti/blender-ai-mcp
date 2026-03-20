# TASK-091: Versioned Client Surfaces for Safe API Evolution

**Priority:** 🔴 High  
**Category:** FastMCP Platform  
**Estimated Effort:** Medium  
**Dependencies:** TASK-083  
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
- curated LLM-first surface for modern clients
- future expert or internal surface for power workflows

This is not only about backwards compatibility. It is also a strategic enabler for product evolution.

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
- staged adoption of LLM-first changes

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

