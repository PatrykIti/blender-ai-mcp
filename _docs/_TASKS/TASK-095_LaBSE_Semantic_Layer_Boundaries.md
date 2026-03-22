# TASK-095: LaBSE Semantic Layer Boundaries

**Priority:** 🔴 High  
**Category:** Router Semantics  
**Estimated Effort:** Medium  
**Dependencies:** TASK-083 (policy / audit baseline). Integration gates: TASK-084 (discovery handoff), TASK-089 (inspection-contract handoff)
**Status:** ✅ Done

**Completion Summary:** This task is now closed. Discovery ownership is on FastMCP search, truth/verification stays on inspection contracts, semantic parameter memory is gated by parameter relevance before learned reuse, semantic workflow results carry explicit scope markers, and tests/telemetry/docs now make LaBSE boundary violations visible.

---

## Objective

Define and formalize the correct role of LaBSE inside the Blender AI MCP stack so that semantic matching remains useful without becoming an unstable source of truth for unrelated responsibilities.

---

## Problem

LaBSE is valuable, but only when used for the right job.

In a system like this, it is easy to let one multilingual embedding model gradually take on too many roles:

- workflow retrieval
- tool retrieval
- parameter matching
- intent repair
- validation
- scene interpretation

That creates a hidden architecture problem. A model that is good at semantic similarity can still be a poor authority for:

- exact tool choice
- execution safety
- geometry truth
- spatial correctness
- post-action validation

If those responsibilities blur together, the router becomes harder to reason about and harder to trust.

---

## Business Outcome

Keep LaBSE where it creates strong value and explicitly remove it from roles where deterministic logic or richer state contracts are the better product choice.

This makes the system:

- easier to tune
- easier to explain
- cheaper to evolve
- safer for Blender execution

---

## Proposed Solution

Position LaBSE as the semantic retrieval and reranking layer for:

- workflow matching
- multilingual prompt understanding
- learned parameter mapping
- synonym and phrasing generalization

At the same time, explicitly define that LaBSE is not the authority for:

- final tool exposure
- exact tool execution policy
- geometry correctness
- scene-state truth
- safety-critical auto-fixes

Those responsibilities should sit with FastMCP discovery controls, deterministic router rules, and structured scene inspection contracts.

---

## Implementation Constraints

Follow [FASTMCP_3X_IMPLEMENTATION_MODEL.md](./FASTMCP_3X_IMPLEMENTATION_MODEL.md).

This task has two dependency moments and they must stay explicit:

- the boundary policy / code-audit phase may start as soon as the FastMCP 3.x migration baseline is understood well enough to audit current call sites
- discovery handoff work waits for TASK-084 because it consumes the platform search surface
- truth / verification handoff work waits for TASK-089 because it consumes structured inspection contracts

Do not delay the policy and audit phase behind the downstream migration work it is meant to govern.

Discovery and visibility should hand off to the platform manifest and FastMCP search controls, not to router metadata or semantic overreach.

---

## FastMCP Features / Approach Context

- **Tool Search** — **FastMCP 3.1.0**  
  Use for general MCP discovery instead of overloading LaBSE with catalog discovery.
- **Tool Transformation / Visibility control** — **FastMCP 3.0.0**  
  Use for curated exposure instead of semantic over-selection.
- **Structured response contracts** — **3.x baseline**  
  Use for scene truth and validation instead of semantic inference.

---

## Scope

This task covers:

- role definition for semantic embeddings in the platform
- boundary-setting between semantic, deterministic, and state-truth layers
- product clarity around what LaBSE should and should not decide

This task does not cover:

- swapping LaBSE for another model immediately
- removing semantic matching from the router

---

## Why This Matters For Blender AI

Semantic similarity is excellent for “what did the user likely mean?”

It is not excellent for:

- “what is the true object state?”
- “is this operation safe?”
- “did the correction actually work?”

This separation is critical if the project wants both multilingual flexibility and deterministic Blender behavior.

---

## Success Criteria

- The project has an explicit semantic-role policy for LaBSE.
- Tool discovery and tool safety are no longer conceptually delegated to the embedding model.
- Workflow and parameter semantics stay multilingual and flexible.
- The router becomes easier to tune because semantic and deterministic responsibilities are clearly separated.

---

## Umbrella Execution Notes

This remains the umbrella task. The original scope stays unchanged.

### Atomic Delivery Waves

1. Audit current LaBSE call sites and publish the boundary policy before downstream handoff work proceeds.
2. Move general discovery onto FastMCP platform search.
3. Move truth and verification checks onto structured inspection contracts.
4. Keep LaBSE focused on workflow and parameter semantics.
5. Add tests and telemetry that make boundary violations visible.

Implementation is decomposed into:

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-095-01](./TASK-095-01_Semantic_Responsibility_Policy_and_Code_Audit.md) | Audit current LaBSE usage and define the formal responsibility policy |
| 2 | [TASK-095-02](./TASK-095-02_Discovery_Handoff_From_LaBSE_to_FastMCP_Search.md) | Move general discovery responsibility to FastMCP search |
| 3 | [TASK-095-03](./TASK-095-03_Truth_and_Verification_Handoff_to_Inspection_Contracts.md) | Move truth and verification decisions onto inspection contracts |
| 4 | [TASK-095-04](./TASK-095-04_Parameter_Memory_and_Workflow_Matching_Hardening.md) | Harden the allowed roles of LaBSE in workflow and parameter logic |
| 5 | [TASK-095-05](./TASK-095-05_Boundary_Tests_Telemetry_and_Documentation.md) | Add regression coverage, telemetry markers, and docs |
