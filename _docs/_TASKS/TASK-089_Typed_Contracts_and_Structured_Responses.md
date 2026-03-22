# TASK-089: Typed Contracts and Structured Responses

**Priority:** 🔴 High  
**Category:** FastMCP LLM Reliability  
**Estimated Effort:** Large  
**Dependencies:** TASK-083  
**Status:** ✅ Done

**Completion Summary:** This task is now closed. The structured-contract layer now covers the high-value scene, mesh, router, workflow, and execution-report surfaces; adapter return policy is centralized; contract-enabled tools use native structured delivery with compatibility strategy where needed; and tests/docs cover schemas, delivery behavior, and the current contract-enabled public surfaces.

---

## Objective

Move critical server responses from prose-heavy outputs toward explicit, typed, machine-readable contracts that are easier for LLMs to consume reliably.

---

## Problem

The project already has many strong inspection and context tools, but if their outputs are too string-oriented, the model has to parse human-oriented prose while also reasoning about geometry and workflow state.

That increases the chance of:

- partial parsing
- missed values
- inconsistent follow-up logic
- silent misinterpretation of scene state
- errors in spatial reasoning and validation

This is one of the core reasons an LLM can be “almost correct” but still drift.

---

## Business Outcome

Make server outputs easier to trust, automate against, and reuse in downstream reasoning.

Typed contracts should especially improve:

- context checks
- inspection flows
- validation steps
- repair and retry behavior
- workflow state handling

---

## Proposed Solution

Adopt structured response design as a product principle for critical tools and internal reasoning helpers.

The desired behavior is:

- important inspection tools return structured, stable payloads
- the LLM no longer depends on brittle text parsing for key state
- internal sampling-assisted reasoning helpers can also use validated structured output when client-mediated sampling is involved

This should begin with high-value context and inspection surfaces and then expand outward.

---

## Implementation Constraints

Follow [FASTMCP_3X_IMPLEMENTATION_MODEL.md](./FASTMCP_3X_IMPLEMENTATION_MODEL.md).

For this repo:

- domain and application handlers may keep returning dict/list state
- adapter-side contracts should define public shape
- structured payloads are the default for state-heavy tools
- stop serializing structured payloads to JSON text in MCP adapters as the first migration move
- do not introduce a custom renderer subsystem before native FastMCP structured delivery is used correctly

For router clarification flows:

- TASK-087 defines clarification semantics and the typed `needs_input` content model
- TASK-089 defines adapter-facing structured delivery, `structuredContent`, `outputSchema`, and execution-report envelopes that reference or embed those clarification models

Do not create a second clarification-question schema in this task family.

### MCP Contract Delivery DoD

For contract-enabled tools in this task scope:

- return machine-readable payloads through MCP `structuredContent`
- declare and maintain tool `outputSchema` aligned with the structured payload shape
- rely on FastMCP's native compatibility delivery where object-like returns already produce structured output plus traditional content
- add explicit text-only compatibility behavior only where a real client need remains after native delivery is used correctly

---

## FastMCP Features To Use

- **Tool output schemas / structured content support in the current FastMCP server tools surface** — **3.x baseline**
- **Structured output via `result_type` for client-mediated sampling flows** — **FastMCP 2.14.1**

---

## Scope

This task covers:

- structured response contracts for critical tools
- machine-readable state exchange
- reduction of prose parsing in important decision points

This task does not cover:

- adding new geometry operations
- introducing Code Mode or tool discovery by itself

---

## Why This Matters For Blender AI

Blender work is state-heavy and spatially sensitive.

If the model misunderstands:

- mode
- selection
- object bounds
- origin
- topology state
- workflow resolution state

then the next action may be logically consistent but still wrong in practice.

Structured response contracts reduce that gap.

---

## Success Criteria

- Critical server outputs become easier for LLMs to consume deterministically.
- Inspection and validation flows rely less on natural-language parsing.
- The project gains a cleaner foundation for spatial assertions and automated QA.
- The model’s follow-up decisions improve because the state contract is clearer.
- Structured contract surfaces consistently expose `structuredContent` + `outputSchema`, with explicit text fallback behavior for compatibility surfaces.

---

## Umbrella Execution Notes

This remains the umbrella task. The original scope stays unchanged.

### Atomic Delivery Waves

1. Define one shared contract catalog and adapter return policy.
2. Remove unconditional `json.dumps(...)` / prose-only return paths from contract-enabled adapters.
3. Convert scene context and scene inspection surfaces to stable structured payloads.
4. Standardize mesh introspection envelopes and paging fields.
5. Add structured router, workflow, and base execution-report contracts that later audit/postcondition work can extend.
6. Add schema tests and public docs for the new contract set.

Implementation is decomposed into:

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-089-01](./TASK-089-01_Contract_Catalog_and_Response_Guidelines.md) | Define the contract catalog and response design rules |
| 2 | [TASK-089-02](./TASK-089-02_Structured_Scene_Context_and_Inspection_Contracts.md) | Add structured contracts for scene context and inspection |
| 3 | [TASK-089-03](./TASK-089-03_Structured_Mesh_Introspection_Contracts.md) | Standardize mesh introspection contracts and paging |
| 4 | [TASK-089-04](./TASK-089-04_Router_Workflow_and_Execution_Report_Contracts.md) | Add typed contracts for router and execution reporting |
| 5 | [TASK-089-05](./TASK-089-05_Adapter_Dual_Format_Delivery_Strategy.md) | Define a dual-format transition strategy for clients |
| 6 | [TASK-089-06](./TASK-089-06_Contract_Tests_Schemas_and_Documentation.md) | Add schema tests and contract documentation |
