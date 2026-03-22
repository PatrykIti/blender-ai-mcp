# TASK-096: Confidence Policy for Auto-Correction

**Priority:** 🔴 High  
**Category:** Router Safety  
**Estimated Effort:** Medium  
**Dependencies:** TASK-087, TASK-095. Integration gate: TASK-085 for session-state-backed persistence/transparency rollout in TASK-096-05.  
**Status:** ✅ Done  

---

## Objective

Define a formal confidence-based policy that determines when the router may auto-correct, when it should ask, and when it must stop.

---

## Problem

Auto-correction is essential in Blender AI systems, but it becomes dangerous when the system does not clearly distinguish:

- a safe precondition fix
- a parameter normalization
- a speculative rewrite of user intent
- a pattern-based replacement with creative consequences

Without a confidence policy, the same router can feel “helpful” in one case and “mysteriously wrong” in another.

The risk grows as the project adds:

- more workflows
- more overrides
- more semantic matching
- more ways to reinterpret a tool call

---

## Business Outcome

Turn auto-correction into a governed product capability instead of an opaque collection of heuristics.

The system should make clear business distinctions between:

- safe automatic repair
- interactive clarification
- fail-fast blocking

That improves both trust and debuggability.

---

## Proposed Solution

Introduce an explicit confidence policy for router behavior.

Recommended operating model:

- **High confidence**: safe deterministic corrections may run automatically.
- **Medium confidence**: the system should prefer clarification, preview, or constrained escalation.
- **Low confidence**: the system should not reinterpret intent silently.
- **No confidence**: block or return a clear needs-input path.

This policy should apply not only to workflow matching, but also to:

- overrides
- intent repair
- semantic parameter reuse
- tool substitution

---

## Implementation Constraints

Follow [FASTMCP_3X_IMPLEMENTATION_MODEL.md](./FASTMCP_3X_IMPLEMENTATION_MODEL.md).

This policy must consume normalized confidence and explicit risk classes, not raw matcher-specific scores or implicit router heuristics.

Dependency rule:

- waves 1 through 4 are router-policy hardening work and should not be blocked on session-adaptive visibility rollout
- TASK-085 becomes a concrete integration gate only where this task persists policy context or exposes operator transparency through session state
- in practice, TASK-096-05 is the slice that consumes TASK-085 session-state primitives directly

Runtime wiring rule:

- when a new runtime policy component/provider is introduced, update dependency wiring in `server/infrastructure/di.py` explicitly
- do not introduce hidden singleton construction paths in adapters/handlers for policy components

---

## FastMCP Features / Approach Context

- **User Elicitation** — **FastMCP 2.10.0**  
  Use as the structured path for medium-confidence clarification.
- **Multi-select elicitation support** — **FastMCP 2.14.0**
- **Session-Scoped State** — **FastMCP 3.0.0**  
  Preserve confidence context and interaction phase across a session.

---

## Scope

This task covers:

- confidence-to-action policy
- escalation rules
- separation of auto-fix vs ask vs block behavior
- consistent business behavior across correction paths

This task does not cover:

- low-level implementation of every engine
- replacing the router

---

## Why This Matters For Blender AI

The key product question is not “can the router correct this?”

It is:

- “should it correct this automatically?”
- “how sure is it?”
- “what is the blast radius if it is wrong?”

That distinction is what separates a strong assistant from a surprising one.

---

## Success Criteria

- The router has an explicit confidence policy.
- Safe corrections are automatic only when confidence and risk justify it.
- Ambiguous cases move into structured clarification instead of silent reinterpretation.
- Auto-correction becomes more trustworthy because its decision policy is visible and consistent.

---

## Umbrella Execution Notes

This remains the umbrella task. The original scope stays unchanged.

### Atomic Delivery Waves

1. Classify correction types and blast radius.
2. Normalize confidence signals across matcher and correction engines.
3. Add one explicit policy engine for auto-fix, ask, or block decisions.
4. Route medium-confidence cases into typed clarification.
5. Persist the decision context and expose it for operators and tests through session-backed state once TASK-085 session primitives exist.
6. Add telemetry and docs for the resulting behavior.

Critical path note:

- TASK-096-01 through TASK-096-04 form the core router policy path
- TASK-096-05 is the session-integration path gated by TASK-085
- TASK-096-06 closes the loop after both policy and session-backed transparency are in place

Implementation is decomposed into:

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-096-01](./TASK-096-01_Correction_Taxonomy_and_Risk_Matrix.md) | Classify correction types and blast radius |
| 2 | [TASK-096-02](./TASK-096-02_Confidence_Scoring_Normalization_Across_Engines.md) | Normalize confidence signals across engines |
| 3 | [TASK-096-03](./TASK-096-03_Auto_Fix_Ask_Block_Policy_Engine.md) | Add a single policy engine for auto-fix, ask, or block decisions |
| 4 | [TASK-096-04](./TASK-096-04_Medium_Confidence_Elicitation_and_Escalation.md) | Route medium-confidence cases into structured clarification |
| 5 | [TASK-096-05](./TASK-096-05_Session_Memory_and_Operator_Transparency.md) | Persist and expose confidence context through the session |
| 6 | [TASK-096-06](./TASK-096-06_Policy_Tests_Telemetry_and_Documentation.md) | Add policy coverage, telemetry, and docs |
