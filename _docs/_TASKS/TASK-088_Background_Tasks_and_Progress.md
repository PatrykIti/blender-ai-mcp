# TASK-088: Background Tasks and Progress for Heavy Blender Work

**Priority:** 🔴 High  
**Category:** FastMCP Operations  
**Estimated Effort:** Medium  
**Dependencies:** TASK-083  
**Status:** ⬜ To Do

---

## Objective

Make heavy, slow, or multi-step operations non-blocking and observable from the client side.

---

## Problem

Some Blender-related operations are expensive enough that synchronous execution becomes a product problem:

- imports and exports
- viewport or multi-angle rendering
- extraction and analysis passes
- large workflow imports
- future reconstruction pipelines
- future mesh and node-graph rebuild flows

When everything blocks in the foreground, users and clients lose visibility into what is happening, cancellation is awkward, and long tasks degrade the overall interaction quality.

---

## Business Outcome

Upgrade the server from “request/response only” to “observable long-running operations.”

This enables:

- better UX for heavy operations
- progress reporting
- more resilient client integration
- less pressure to keep every tool unrealistically short-running

---

## Proposed Solution

Use the MCP background task protocol for operations where immediate synchronous completion is not the best user experience.

The server should distinguish between:

- fast foreground interactions
- heavy background-capable jobs

This gives the product room to grow into more ambitious workflows without making the chat loop feel frozen or unreliable.

---

## FastMCP Features To Use

- **Background Tasks** — **FastMCP 2.14.0**

---

## Scope

This task covers:

- long-running server operations
- progress-aware client UX
- cancellation and later retrieval of results
- future-proofing for reconstruction and analysis jobs

This task does not cover:

- changing domain logic for every tool
- search or API visibility concerns

---

## Why This Matters For Blender AI

The more ambitious this project becomes, the more it needs a non-blocking execution model.

This is especially relevant if the project expands into:

- geometry reconstruction
- node graph rebuilds
- richer scene analysis
- image and asset pipelines

Without background tasks, those features become harder to ship cleanly.

---

## Success Criteria

- Heavy operations can run without blocking the main client interaction.
- Clients can observe progress and retrieve results later.
- The platform becomes ready for larger-scale Blender workflows.
- Long operations feel like a supported product pattern rather than an operational edge case.

