# TASK-093: Observability, Timeouts, and Pagination

**Priority:** 🟡 Medium  
**Category:** FastMCP Operations  
**Estimated Effort:** Medium  
**Dependencies:** TASK-083 (platform baseline). Task-mode-specific timeout / diagnostics rollout depends on TASK-088-02.
**Status:** 🚧 In Progress

**Current State:** `TASK-093-01` and `TASK-093-02` are now complete: the repo has OTEL bootstrap, repo-specific router spans, explicit timeout boundary names, timeout policy diagnostics, and tests/docs for telemetry + timeout foundations. The umbrella remains open for pagination, diagnostics surface, and operations-focused documentation slices.

---

## Objective

Improve the server’s operational maturity so it is easier to observe, safer to run at scale, and less likely to overwhelm clients with oversized listings.

---

## Problem

As the server grows, reliability is no longer just a domain-logic problem. It is also an operations problem.

Current and future risks include:

- not knowing where the model or server got stuck
- long-running tools with weak guardrails
- giant component listings
- difficulty comparing client sessions
- weak visibility into where failures originate

These problems become more visible as the product shifts toward larger workflows, more tools, and stronger client integration.

---

## Business Outcome

Make the platform easier to operate, debug, and scale.

This is important both for maintainers and for diagnosing LLM behavior in real Blender tasks.

---

## Proposed Solution

Adopt FastMCP operational features that improve:

- tracing
- bounded execution
- large-list behavior
- server diagnostics

This task should be treated as product infrastructure, not just developer convenience.

---

## Implementation Constraints

Follow [FASTMCP_3X_IMPLEMENTATION_MODEL.md](./FASTMCP_3X_IMPLEMENTATION_MODEL.md).

This umbrella must treat these as separate concerns:

- built-in FastMCP OpenTelemetry spans vs repo-specific router/job attributes
- MCP component pagination vs domain payload pagination
- foreground tool timeouts vs background-task execution timeouts vs RPC timeouts

### Ownership Rule

- TASK-093 owns the shared timeout taxonomy, observability model, diagnostics payloads, and pagination policy
- TASK-088 owns the task bridge, RPC/job execution architecture, and concrete heavy-operation adoption
- when TASK-088 runtime code needs timeout behavior, it must consume the contracts defined here rather than creating a parallel policy layer

---

## FastMCP Features To Use

- **OpenTelemetry tracing** — **FastMCP 3.0.0**
- **Tool timeouts** — **FastMCP 3.0.0**
- **Pagination for large component lists** — **FastMCP 3.0.0**

---

## Scope

This task covers:

- runtime observability
- timeout strategy for MCP operations
- component listing ergonomics at scale
- operational diagnostics for real client sessions

This task does not cover:

- business redesign of tools
- visual Blender QA features

---

## Why This Matters For Blender AI

When a model “gets lost,” the root cause may be:

- bad prompt state
- a wrong tool choice
- a hidden timeout
- a giant listing
- a server-side failure

Observability and operational guardrails make those distinctions clearer and shorten the feedback loop for product improvement.

---

## Success Criteria

- The platform becomes easier to debug and monitor.
- Long operations have clearer execution boundaries.
- Large component listings stop being an operational liability.
- The project gains better visibility into real-world LLM usage patterns.

---

## Umbrella Execution Notes

This remains the umbrella task. The original scope stays unchanged.

### Atomic Delivery Waves

1. Bootstrap OpenTelemetry on top of FastMCP’s native spans.
2. Define explicit timeout contracts per runtime boundary and feed them into TASK-088 runtime adaptation.
3. Enable pagination for large MCP component lists.
4. Standardize payload pagination for large structured tool outputs.
5. Expose operational diagnostics so maintainers can see active profile, phase, jobs, and timeout state.

Implementation is decomposed into:

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-093-01](./TASK-093-01_Telemetry_Model_and_OpenTelemetry_Bootstrap.md) | Add telemetry foundations and OpenTelemetry bootstrap |
| 2 | [TASK-093-02](./TASK-093-02_Tool_and_Task_Timeout_Policy.md) | Define timeouts for tools, tasks, and RPC boundaries |
| 3 | [TASK-093-03](./TASK-093-03_Pagination_Rollout_for_Component_and_Data_Listings.md) | Add pagination to large listings and payloads |
| 4 | [TASK-093-04](./TASK-093-04_Operational_Status_and_Diagnostics_Surface.md) | Expose operational diagnostics and runtime status |
| 5 | [TASK-093-05](./TASK-093-05_Operations_Tests_and_Documentation.md) | Add operations-focused tests and documentation |
