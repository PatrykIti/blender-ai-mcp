# Semantic Boundary Audit

Code-backed audit for `TASK-095-01`.

This document maps the current LaBSE / semantic call sites in the repo onto the intended responsibility split:

- FastMCP platform decides visibility and discovery exposure
- LaBSE decides semantic similarity and multilingual retrieval
- Router decides deterministic execution safety
- Inspection decides Blender truth

## Current Allowed Semantic Responsibilities

### 1. Tool Intent Classification

File:
- `server/router/application/classifier/intent_classifier.py`

Current role:
- embeds prompts with LaBSE
- searches tool embeddings in the vector store
- predicts semantically similar tools

Boundary assessment:
- Allowed only as intent classification / retrieval input
- Not allowed as final authority for public tool visibility or safety policy

### 2. Workflow Intent Classification

File:
- `server/router/application/classifier/workflow_intent_classifier.py`

Current role:
- embeds prompts and workflow texts with LaBSE
- performs semantic workflow matching and reranking
- supports multilingual workflow lookup

Boundary assessment:
- Allowed as workflow retrieval / ranking
- Not allowed as proof that the selected workflow is safe or correct in Blender state

### 3. Parameter Resolution Memory

File:
- `server/router/application/resolver/parameter_resolver.py`

Current role:
- uses classifier similarity for prompt-to-parameter relevance
- reuses learned parameter mappings through semantic matching
- decides whether a value is unresolved and should be clarified

Boundary assessment:
- Allowed for semantic memory and relevance scoring
- Not allowed as the truth layer for actual scene state or post-execution validation

### 4. Parameter Memory Store

File:
- `server/router/application/resolver/parameter_store.py`

Current role:
- stores learned parameter mappings with LaBSE-derived embeddings
- retrieves prior mappings through semantic similarity search
- keeps multilingual parameter reuse inside the resolver/store boundary

Boundary assessment:
- Allowed as semantic memory persistence and retrieval
- Not allowed as discovery/catalog authority
- Not allowed as proof that a stored value is still correct in current Blender state

### 5. Semantic Matcher (Ensemble)

File:
- `server/router/application/matcher/semantic_matcher.py`

Current role:
- wraps `WorkflowIntentClassifier` for ensemble matching
- contributes semantic workflow scores into the ensemble vote
- keeps semantic matching as one input among keyword/pattern signals

Boundary assessment:
- Allowed as semantic workflow similarity inside matcher composition
- Not allowed as the sole authority for workflow execution policy
- Not allowed to bypass platform-owned discovery/exposure decisions

### 6. Semantic Modifier Extraction

File:
- `server/router/application/matcher/modifier_extractor.py`

Current role:
- uses classifier similarity to match prompt phrases to workflow modifiers
- enables multilingual modifier extraction
- returns semantic modifier hints for workflow parameter overrides

Boundary assessment:
- Allowed as semantic modifier interpretation inside workflow/parameter semantics
- Not allowed as scene truth or verification evidence
- Not allowed to become a public tool-discovery mechanism

### 7. Semantic Workflow Matching

File:
- `server/router/application/matcher/semantic_workflow_matcher.py`

Current role:
- combines exact, pattern, and LaBSE-driven semantic matches
- returns confidence-oriented workflow match results

Boundary assessment:
- Allowed for workflow matching and generalization
- Not allowed as final authority for inspection, verification, or public catalog shaping

### 8. Ensemble Aggregation

File:
- `server/router/application/matcher/ensemble_aggregator.py`

Current role:
- aggregates semantic, keyword, and pattern contributions
- turns semantic confidence into workflow-level confidence classes

Boundary assessment:
- Allowed as semantic/deterministic aggregation inside workflow choice
- Not allowed to leak semantic confidence into scene truth assumptions

### 9. Workflow Adaptation Filtering

File:
- `server/router/application/engines/workflow_adapter.py`

Current role:
- uses classifier similarity to decide whether optional workflow steps are semantically relevant
- applies a semantic threshold only inside workflow adaptation
- keeps optional-step selection separate from Blender truth inspection

Boundary assessment:
- Allowed as semantic filtering for workflow adaptation
- Not allowed as proof that the adapted workflow result is correct
- Not allowed to replace explicit platform visibility/discovery controls

### 10. Router Semantic Orchestration

File:
- `server/router/application/router.py`

Current role:
- wires shared LaBSE-backed components into router orchestration
- initializes semantic matcher and modifier extractor via DI/shared classifier
- consumes semantic results as one input into router/workflow behavior

Boundary assessment:
- Allowed as orchestration of semantic components
- Not allowed to collapse the platform/discovery/truth boundaries back into one fuzzy decision layer
- Must keep semantic outcomes subordinate to deterministic policy and inspection truth

## Current Non-Semantic Layers That Must Stay Separate

### Platform / Exposure

Files:
- `server/adapters/mcp/platform/capability_manifest.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/transforms/naming.py`

Boundary rule:
- tool discovery, visibility, and public naming belong here, not in LaBSE-driven ranking

### Deterministic Safety

Files:
- `server/adapters/mcp/router_helper.py`
- `server/router/application/router.py`
- `server/router/application/engines/*`

Boundary rule:
- auto-fix, ask/block, override, mode correction, and execution safety belong here

### Blender Truth / Inspection

Files:
- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/areas/mesh.py`
- future `contracts/scene.py`, `contracts/mesh.py`

Boundary rule:
- scene truth and verification must come from inspection contracts, not semantic scores

## Audit Findings

### Healthy Current Usage

- LaBSE is already centered around workflow and tool similarity rather than direct Blender execution
- shared model loading through DI keeps heavy semantic infrastructure centralized
- parameter memory uses semantic similarity for reuse, which is within the allowed responsibility boundary
- workflow adaptation and modifier interpretation use semantic similarity as workflow-level guidance rather than Blender truth

### Boundary Risks To Watch

- semantic tool matching could be misread as discovery/catalog authority unless `TASK-084` stays platform-owned
- semantic confidence could drift into auto-correction policy unless `TASK-096` keeps explicit risk/decision logic separate
- workflow match confidence could be mistaken for execution truth unless `TASK-089` and `TASK-097` keep structured inspection/postcondition paths authoritative

## Explicit Policy

Allowed LaBSE roles in this repo:

- multilingual workflow retrieval
- semantic workflow reranking
- tool intent classification
- learned parameter reuse
- semantic relevance scoring for missing inputs

Disallowed LaBSE roles in this repo:

- final public tool exposure
- public search/discovery ownership
- deterministic correction policy
- scene-state truth
- post-execution verification
- proof that a correction succeeded

## Deferred Follow-Up

- `TASK-095-02`: move discovery ownership fully onto FastMCP search
- `TASK-095-03`: move truth / verification ownership fully onto structured inspection contracts
- `TASK-095-04`: harden parameter memory and workflow matching inside the allowed semantic scope
