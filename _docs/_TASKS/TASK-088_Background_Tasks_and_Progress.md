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

## Implementation Constraints

Follow [FASTMCP_3X_IMPLEMENTATION_MODEL.md](./FASTMCP_3X_IMPLEMENTATION_MODEL.md).

For this repo, background execution is a two-layer problem:

- FastMCP task UX at the MCP boundary
- addon/server-side Blender job execution beyond the current blocking RPC timeout model

This task is not complete if only the MCP layer becomes task-aware while the addon still blocks on a single `result_queue.get(timeout=30.0)` path.

Implementation should stay split across four seams:

- server task bridge
- server RPC verbs and protocol changes
- addon job lifecycle and main-thread coordination
- incremental adoption by selected heavy tools
- async task-capable adapter entrypoints (`async def` + `task=True`) for selected heavy operations

### Runtime Requirement (Hard Gate)

- FastMCP runtime must include task support (`fastmcp[tasks]` or equivalent dependency set enabled in this repo baseline).
- MCP entrypoints marked with `task=True` must be `async def` and verified in tests.
- Task-capable surfaces must keep an explicit compatibility fallback for non-task/sync clients when required.
- Task-enabled entrypoints must use explicit `TaskConfig` execution semantics (`mode="optional" | "required" | "forbidden"`) rather than implicit behavior.
- Registration-guard tests must prove that `task=True` on a sync function fails at registration time.

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
- Task-mode entrypoints are explicitly async and validated against a runtime with task support enabled.
- Task execution mode behavior (`optional`/`required`/`forbidden`) is explicitly defined, tested, and documented per adopted endpoint.

---

## Umbrella Execution Notes

This remains the umbrella task. The original scope stays unchanged.

### Atomic Delivery Waves

1. Classify which operations truly need task mode instead of synchronous execution.
2. Build the FastMCP task bridge and explicit job identity mapping.
3. Define progress, cancellation, and result retrieval contracts.
4. Adapt RPC and addon runtime to launch, poll, and cancel Blender jobs safely.
5. Convert selected heavy entrypoints to async task-capable adapters and roll task mode into the highest-value tools first.
6. Add operations-focused tests and docs for task behavior.

Implementation is decomposed into:

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-088-01](./TASK-088-01_Heavy_Operation_Inventory_and_Task_Candidacy.md) | Classify which operations should support task execution |
| 2 | [TASK-088-02](./TASK-088-02_Async_Task_Bridge_and_Job_Registry.md) | Build the background-task bridge and job registry |
| 3 | [TASK-088-03](./TASK-088-03_Progress_Cancellation_and_Result_Retrieval.md) | Define progress, cancellation, and result retrieval contracts |
| 4 | [TASK-088-04](./TASK-088-04_RPC_and_Blender_Main_Thread_Adaptation.md) | Adapt RPC and Blender runtime for longer-running jobs |
| 5 | [TASK-088-05](./TASK-088-05_Background_Adoption_for_Imports_Renders_Extraction_and_Workflow_Import.md) | Roll task mode into concrete heavy tools |
| 6 | [TASK-088-06](./TASK-088-06_Task_Mode_Tests_Operations_and_Docs.md) | Add operations docs and regression coverage |
