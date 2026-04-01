# Responsibility Boundaries: FastMCP, LaBSE, Router, Inspection

This document defines the intended responsibility split for the LLM runtime stack in `blender-ai-mcp`.

It exists to prevent architectural drift while the project grows its FastMCP platform, semantic matching, router intelligence, and Blender inspection surface.

---

## Why This Document Exists

This project now contains four different kinds of intelligence:

- MCP platform behavior
- semantic understanding
- deterministic execution correction
- Blender state inspection

If those layers blur together, the system becomes harder to:

- trust
- tune
- debug
- migrate safely to FastMCP 3.x

The goal is to make each layer explicit and keep the stack coherent as the product expands.

---

## Layer 1: FastMCP Platform Layer

### Role

FastMCP is the **platform and presentation layer** for the MCP product surface.

It should be responsible for:

- tool discovery
- tool visibility
- session-aware capability shaping
- API surface transformation
- prompt delivery
- user elicitation
- background task UX
- versioned client surfaces
- structured interaction contracts at the MCP boundary

### It Is Good At

- deciding what the client can see
- making large catalogs manageable
- adapting the public surface for different client types
- carrying interaction patterns such as prompts, structured clarifications, and long-running jobs

### It Is Not The Authority For

- semantic intent understanding
- scene truth
- geometry correctness
- Blender execution safety

### Design Rule

If the question is:

- “what should be exposed?”
- “what should be discoverable?”
- “how should clients interact with this surface?”

the answer belongs primarily to FastMCP.

---

## Layer 2: LaBSE Semantic Layer

### Role

LaBSE is the **semantic retrieval and generalization layer**.

It should be responsible for:

- multilingual workflow matching
- semantic workflow reranking
- synonym and phrasing generalization
- learned parameter mapping reuse
- semantic modifier interpretation

### It Is Good At

- matching intent across languages
- handling prompt paraphrases
- retrieving likely workflows or mappings when wording varies
- supporting learned semantic memory

### It Is Not The Authority For

- the final public tool catalog
- exact tool safety policy
- scene-state truth
- geometry validation
- whether a correction actually succeeded

### Design Rule

If the question is:

- “what did the user probably mean?”
- “which workflow or modifier is semantically closest?”

LaBSE is appropriate.

If the question is:

- “what is actually true in Blender?”
- “is this operation safe?”
- “did the fix work?”

LaBSE must not be the source of truth.

### Current Enforcement Notes

- general MCP tool discovery is owned by FastMCP search and visibility controls
- semantic parameter memory is allowed only when the prompt is relevant to the target parameter
- semantic workflow results are workflow-retrieval input, not proof of truth or policy approval

---

## Layer 3: Router Policy And Safety Layer

### Role

The router is the **deterministic policy layer** between LLM intent and Blender execution.

It should be responsible for:

- mode correction
- selection correction
- safe parameter normalization
- clamping
- guardrails and blocking
- confidence-based workflow adaptation
- explicit override policy
- converting intent into safer tool sequences

### It Is Good At

- applying deterministic precondition fixes
- protecting Blender from obvious misuse
- enforcing operational policy
- handling correction/ask/block decisions

### It Is Not The Authority For

- raw semantic retrieval
- public MCP exposure strategy
- final scene correctness by itself

The router may use semantic inputs, but it should not become a fuzzy all-purpose brain.

### Design Rule

If the question is:

- “how do we execute this safely?”
- “what deterministic correction can we apply?”
- “should we auto-fix, ask, or block?”

the router owns that decision.

Speculative reinterpretation must be tightly governed by confidence and risk policy.

---

## Layer 4: Inspection And Assertion Layer

### Role

The inspection/assertion layer is the **truth and verification layer**.

It should be responsible for:

- current scene state
- object dimensions and origin
- topology and attribute state
- hierarchy and material/node inspection
- render-based visual QA
- future assertions about alignment, contact, symmetry, containment, and correctness

### It Is Good At

- reporting what actually exists in Blender
- validating whether expected conditions are true
- feeding reliable state back into the router or client LLM

### It Is Not The Authority For

- semantic intent matching
- API discovery
- public-surface shaping

### Design Rule

If the question is:

- “what is the actual state right now?”
- “did the operation produce the intended result?”
- “are these objects aligned / intersecting / inside / symmetric?”

the answer belongs to inspection/assertion tools, not to LaBSE and not to speculative router logic.

---

## Target System Contract

The intended system contract is:

- **FastMCP** decides what is visible and how interaction is structured.
- **LaBSE** decides what is semantically similar.
- **Router** decides what is safe and how execution should be corrected.
- **Inspection / Assertion** decides what is true and whether the result is acceptable.

For correction policy specifically:

- normalized confidence and explicit risk classes should feed one router policy decision
- that decision should resolve to `auto-fix`, `ask`, or `block`
- operator-visible policy context should surface the chosen path and rationale

This separation should hold even when the same request touches all four layers.

## Sampling Assistant Guardrails

Sampling assistants do not introduce a fifth authority layer.
They are a bounded FastMCP-mediated helper mechanism that must remain subordinate to the existing split above.

Allowed first responsibilities:

- summarize structured inspection payloads
- compress large diagnostics into compact next-step guidance
- draft repair suggestions from router/runtime diagnostics

Forbidden first responsibilities:

- autonomous geometry-destructive planning
- hidden substitution for router safety policy
- scene-truth decisions without inspection contracts
- detached background reasoning outside an active MCP request

Design rule:

- assistants may help interpret inspection truth
- assistants may help draft recovery guidance from diagnostics
- assistants must not become the authority for safety approval, discovery ownership, or Blender truth

---

## Current State In This Repository

### FastMCP Layer

Current state: **partially aligned, needs major improvement**

- The server already has a strong MCP surface.
- However, the current runtime is still mostly a flat registered tool catalog.
- Discovery, visibility shaping, versioned surfaces, and other 3.x platform features are not yet the main organizing principle.

Interpretation:

- This layer is the main area that still needs structural improvement.

### LaBSE Layer

Current state: **mostly aligned**

- LaBSE is already used mainly for workflow matching, multilingual semantics, and parameter memory.
- Shared model loading via DI is already in place.
- This is directionally correct.

Interpretation:

- Keep LaBSE.
- Do not let it expand into discovery, truth, or safety roles.

### Router Layer

Current state: **good foundation, needs policy hardening**

- Mode switching, selection injection, alias normalization, and parameter clamping already exist.
- Workflow adaptation and confidence concepts already exist.
- Pattern overrides also exist.

Interpretation:

- The deterministic safety role is present.
- What still needs work is policy clarity:
  - when auto-fix is allowed
  - when the system should ask
  - when override behavior is too speculative
  - how corrections are audited and validated

### Inspection / Assertion Layer

Current state: **strong inspection, incomplete assertion**

- Inspection is already one of the strongest parts of the repo.
- The system has rich tools for context, topology, modifiers, constraints, bounds, origins, and view-based inspection.
- However, assertions are still weaker than inspections.

Interpretation:

- The project already has a strong truth layer foundation.
- It now needs explicit assertion tools and postcondition-based validation.

---

## Practical Rules For Contributors

- Do not use LaBSE to solve a problem that FastMCP discovery/visibility should solve.
- Do not use semantic similarity as proof of scene correctness.
- Do not silently convert speculative semantic guesses into automatic Blender writes unless the correction policy clearly allows it.
- Prefer structured inspection outputs over prose when correctness matters.
- Prefer elicitation over silent reinterpretation in medium-confidence cases.
- Treat inspection and future assertion tools as the final authority on Blender state.

---

## Related Docs

- [README](./README.md)
- [ROUTER_ARCHITECTURE.md](./ROUTER_ARCHITECTURE.md)
- [WORKFLOWS/workflow-execution-pipeline.md](./WORKFLOWS/workflow-execution-pipeline.md)
- [TASK-083](../_TASKS/TASK-083_FastMCP_3x_Platform_Migration.md)
- [TASK-084](../_TASKS/TASK-084_Dynamic_Tool_Discovery.md)
- [TASK-089](../_TASKS/TASK-089_Typed_Contracts_and_Structured_Responses.md)
- [TASK-095](../_TASKS/TASK-095_LaBSE_Semantic_Layer_Boundaries.md)
- [TASK-096](../_TASKS/TASK-096_Confidence_Policy_for_Auto_Correction.md)
- [TASK-097](../_TASKS/TASK-097_Transparent_Correction_Audit_and_Postconditions.md)
