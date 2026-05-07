# TASK-136: Reference-Guided Architecture and Building Reconstruction

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Category:** Reconstruction / Architecture and Hard Surface
**Estimated Effort:** Large
**Follow-on After:** [TASK-118](./TASK-118_Scene_Render_World_And_Configuration_Wave.md), [TASK-120](./TASK-120_Macro_Tool_Layer_And_Guided_Surface_Collapse.md), [TASK-122](./TASK-122_Hybrid_Vision_Truth_And_Correction_Macro_Wave.md), [TASK-124](./TASK-124_Guided_Session_Goal_And_Reference_Orchestration.md), [TASK-130](./TASK-130_Default_Guided_Surface_Bootstrap_Consistency.md), [TASK-157](./TASK-157_Goal_Derived_Quality_Gates_And_Deterministic_Verification.md), [TASK-163](./TASK-163_Vision_Orchestrator_Feedback_Strategy_Normalization_And_Optional_Perception_Adapters.md)

## Objective

Extend the shipped first-pass `building` guided/runtime substrate into a
reconstruction-grade architecture path, so an LLM operating the MCP server can
rebuild small and medium structures from plans, elevations, sections, or photo
references while preserving footprint, openings, structural rhythm, roof form,
and major proportions.

## Business Problem

The repo already supports many bounded architectural subproblems and the first
generic `building` overlay:

- placement and relative layout
- cutouts, recesses, and openings
- dimension checks and grouped scene inspection
- low-level modeling and mesh editing

That shipped substrate is useful, but it does not yet add up to a
reconstruction-grade product path for architecture-specific reference work.

The missing business capability is not "can Blender do hard-surface work?" but
"can the guided MCP product help the model rebuild buildings and architectural
modules from references without rediscovering the whole strategy each time?"

Current limitations are:

- no dedicated architecture prompt asset or architecture-specific prompt
  recommendation path on `llm-guided`
- no explicit product contract for architectural reconstruction fidelity
- the current building guided flow is still coarse relative to the intended
  architecture sequence, because it stops at generic building masses and
  secondary parts instead of explicitly modeling shell/opening/roof/support
  phases
- relation semantics, facade rhythm, and opening-grid expectations are still
  too generic for reconstruction from plans/elevations
- the owner-lane docs and regression plan do not yet point cleanly at the
  current building runtime seams that already ship

## Current Runtime Baseline

The repo already has strong foundations this umbrella should build on:

- `llm-guided` search-first bootstrap and goal-scoped reference intake
- a shipped `building` domain profile with guided flow/role selection, bounded
  visibility ordering, and building-specific required checks
- staged `reference_compare_*` and `reference_iterate_stage_checkpoint(...)`
  flows
- closed `TASK-157` quality-gate templates and verifier lanes, including
  building `attachment_seam` / `opening_or_cut` behavior
- closed `TASK-163` reference-understanding and orchestrator-feedback seams on
  the existing `reference_images(...)`, `router_*`, and checkpoint surfaces
- grouped scene inspection/configuration from `TASK-118`
- bounded hard-surface and layout macros such as cutout, placement, contact,
  and proportion repair
- prompt-driven guided sessions and shaped visibility/search behavior
- building owner-lane tests in guided flow/search/visibility plus the current
  building gate transport and Blender-backed E2E proof lanes

The follow-on should extend that product foundation into the architecture
domain. It should not reopen the old flat-catalog model or bypass the guided
surface.

## Generic Gate Dependency

This umbrella should consume
[TASK-157](./TASK-157_Goal_Derived_Quality_Gates_And_Deterministic_Verification.md)
instead of introducing a separate hardcoded architecture-only gate system.
Building goals should be able to derive flexible gates such as roof seating,
opening grids, facade rhythm, footprint ratios, support contacts, and roofline
profiles, while the server normalizes and verifies those gates through the
generic gate contract.

## Current Capability Ceiling

Today the product can support:

- bounded hard-surface prop work
- isolated openings or placement repairs
- a generic building overlay with `footprint_mass`, `main_volume`, `roof_mass`,
  `facade_opening`, and `support_element` roles
- building gate blockers such as `roof_wall` seams and `opening_or_cut`
  failures on the staged checkpoint path
- manual low-poly architecture tasks when the operator already knows the tool
  path

That is still below the desired outcome for architecture reconstruction from
references. What is missing is a domain contract that understands buildings as
structured systems:

- footprint and vertical massing
- repeated bays/modules
- walls, openings, supports, and roof form
- dimensional rhythm and alignment

## Current Drift To Resolve

The follow-on gap to close is:

- the public guided story still treats architecture as a first-pass building
  overlay instead of an explicit reconstruction-grade domain
- the repo still lacks a dedicated architecture prompt asset and
  recommendation/handoff wording for plans, elevations, sections, and facade
  rhythm
- current vision/reference handling still needs architecture-specific
  interpretation for plan/elevation/section reasoning, opening grids, and roof
  profiles on top of the closed RU substrate
- the current building flow/control plane is too coarse for the intended
  shell/openings/roof/support sequencing, so this umbrella must extend the
  existing guided-step model instead of pretending it does not exist
- the loop output does not yet express enough building-specific failures such
  as:
  - missing or duplicated openings
  - wrong bay spacing
  - floor-height drift
  - roof pitch or roofline mismatch
  - support misplacement
- the guided/reference loop does not yet encode relation semantics for common
  architectural attachments and interfaces, such as:
  - opening cut into wall shell
  - roof seated on wall mass
  - beam supported by posts/columns
  - stair/arch element meeting its support
- the current corrective path does not yet clearly distinguish:
  - intentional boolean penetration / cutout
  - expected seated/support contact
  - acceptable modular interface contact
  - bad overlap or floating separation that really needs cleanup
- `llm-guided` does not yet have a dedicated architecture-specific prompt
  asset, recommendation path, handoff wording, and search-bias behavior
- there is no explicit tool-surface roadmap for reconstruction-heavy
  architecture tasks such as opening grids, repeated supports, roof generators,
  facade rhythm, and modular structural rebuilds
- the current task docs and proof lanes do not yet cleanly map to the shipped
  owner seams that now own building guided flow, session control, reference
  checkpoint shaping, and architecture-adjacent regression

## Business Outcome

If this umbrella is done correctly, the repo gains:

- one explicit product story for reference-guided architecture reconstruction
- a first promoted reconstruction target class for:
  - small buildings
  - facade modules
  - towers, huts, wells, gates, and similar structures
  - reusable architectural asset modules
- a cleaner bridge between references, staged loop guidance, and deterministic
  hard-surface/building corrections
- a clearer path from "reference image or plan" to "bounded reconstruction
  session" instead of ad hoc tool rediscovery
- a relation-aware story for architectural interfaces so the product can tell
  the difference between expected cut/support/seat behavior and true geometric
  failure

## Product Design Requirements

### Vision Mode

- Support architecture-aware reference interpretation across:
  - top/plan references
  - front and side elevations
  - perspective concept/reference photos when orthographic references are not
    available
- Define a reusable architecture vocabulary for:
  - footprint
  - facade
  - bay/module
  - opening
  - wall shell
  - roof type
  - support/post/column/beam
  - stair/arch/chimney/tower elements where applicable
- Add deterministic architecture-oriented metrics and findings such as:
  - footprint ratio and depth/width drift
  - wall height and floor-band spacing
  - opening count, placement, and spacing
  - symmetry and centerline drift
  - roof pitch, ridge height, and overhang mismatch
  - support spacing and facade rhythm mismatch
- Define architecture-specific relation semantics for major interfaces:
  - cut into
  - seated on
  - supported by
  - spans between
  - aligned to grid/module
  - intentionally separate
- Add capture/reporting profiles suited to architecture:
  - plan/top view
  - front elevation
  - side elevation
  - roofline/upper silhouette
  - opening grid / facade checkpoint views

### Loop System

- Design staged architecture reconstruction loops around phases such as:
  - footprint and base massing
  - wall shell
  - openings and structural supports
  - roof form
  - trim/modular detail
  - final dimensional validation
- Extend the loop contract so it can surface building-specific reconstruction
  findings instead of only generic mismatch prose
- Add relation-aware loop findings so architectural corrections can distinguish:
  - missing opening vs bad floating window object
  - intended roof seating vs collision cleanup
  - intended boolean recess vs accidental overlap
  - intended support contact vs unsupported floating element
- Integrate truth-first follow-up for:
  - dimensions
  - alignment
  - overlap/contact errors
  - repeated-module consistency
- Define when the loop should steer toward:
  - layout/cutout corrections
  - attach/support corrections
  - proportion/scale corrections
  - repeated-structure corrections
  - inspect/validate before further rebuild work

### `llm-guided` Profile

- Add architecture-oriented prompt assets and recommendation paths
- Define architecture-specific guided handoff recipes so the model does not
  treat building reconstruction like generic prop modeling
- Make the architecture guided story explicit about interface semantics, so the
  model knows when a wall/opening/roof/support relation should be treated as a
  cut, a seat, a support, or a true collision
- Bias guided search toward the relevant building tools for natural requests
  such as:
  - floor plan to low-poly building
  - recreate facade from front/side references
  - add windows/doors in the correct rhythm
  - rebuild roof shape and supports
- Define separate bounded stories for:
  - modular architectural assets
  - standalone small buildings
  - facade-only reconstruction

### Tool Surface

- Evaluate which existing tools already cover the domain well and which gaps
  need new bounded surfaces
- Likely architectural tool-surface gaps include bounded support for:
  - repeated opening placement
  - modular facade grids
  - roof primitives / roof profile reconstruction
  - support/beam/post arrays or repeated placements
  - wall shell generation from footprint-like inputs
  - deterministic duplication/spacing workflows for building modules
- Define a relation-aware macro/tool selection policy so architectural
  correction can choose between cutout/layout/attach/support/cleanup operations
  from explicit interface intent rather than raw overlap alone
- Keep new tools bounded and domain-shaped rather than reopening unrestricted
  modeling exposure

## Scope

This umbrella covers:

- architecture-specific prompt, handoff, and search shaping
- architecture-aware reference interpretation and metric design
- loop-system outputs for staged building reconstruction
- architecture-specific interface semantics and relation-aware correction policy
- architecture-oriented visibility/profile/tool-surface design
- domain docs, evaluation criteria, and regression planning

This umbrella does **not** cover:

- full CAD/BIM import or CAD-accurate document exchange
- city-scale urban planning workflows
- interior decoration and furnishing as a first-pass target
- photoreal rendering/material recreation
- unconstrained free-form architecture generation without bounded contracts

## Acceptance Criteria

- the repo has one explicit guided product story for architecture
  reconstruction
- the first target class of architectural reconstruction is explicitly bounded
  and regressionable
- vision/reference outputs can express building-specific findings rather than
  only generic shape feedback
- the loop can represent expected architectural interfaces and distinguish them
  from true overlap/floating failures
- the loop contract can steer staged reconstruction across shell/openings/roof
  work with deterministic follow-up
- `llm-guided` can recommend and expose an architecture-oriented handoff path
- docs, runtime behavior, and regression criteria describe the same bounded
  architecture capability and limitations

## Repository Touchpoints

- `server/adapters/mcp/prompts/prompt_catalog.py`
- `server/adapters/mcp/prompts/provider.py`
- `server/adapters/mcp/prompts/rendering.py`
- likely new `_docs/_PROMPTS/REFERENCE_GUIDED_ARCHITECTURE_BUILD.md`
- `_docs/_PROMPTS/README.md`
- `server/adapters/mcp/guided_mode.py`
- `server/adapters/mcp/contracts/guided_flow.py`
- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/session_capabilities_bootstrap.py`
- `server/adapters/mcp/session_capabilities_registry.py`
- `server/adapters/mcp/session_capabilities_state.py`
- `server/adapters/mcp/session_capabilities_flow.py`
- `server/adapters/mcp/session_capabilities_runtime_glue.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/transforms/quality_gate_verifier.py`
- `server/adapters/mcp/discovery/search_documents.py`
- `server/adapters/mcp/discovery/search_surface.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/contracts/quality_gates.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/areas/reference_checkpoint_compare.py`
- `server/adapters/mcp/areas/reference_images_runtime.py`
- `server/adapters/mcp/areas/reference_planner.py`
- `server/adapters/mcp/areas/reference_truth.py`
- `server/adapters/mcp/areas/reference_understanding.py`
- `server/adapters/mcp/areas/reference_view_diagnostics.py`
- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/areas/scene_guided_runtime.py`
- `server/adapters/mcp/areas/modeling.py`
- `server/adapters/mcp/areas/mesh.py`
- `server/adapters/mcp/areas/scene_spatial_graph.py`
- `server/application/services/spatial_graph.py`
- `server/router/infrastructure/tools_metadata/`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_quality_gate_verifier.py`
- `tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_scene_guided_scope_requirements.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/`
- `tests/unit/tools/scene/`
- `tests/e2e/integration/`
- `tests/e2e/vision/`
- `_docs/_VISION/`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TESTS/README.md`
- `_docs/_TASKS/README.md`

## Repository Touchpoint Table

| Path / Module | Scope | Expected Work |
|---------------|-------|---------------|
| `server/adapters/mcp/contracts/quality_gates.py` and `server/adapters/mcp/contracts/reference.py` | MCP/public contract | Extend the shipped building gate/reference vocabulary on the existing adapter-layer contract path without leaking FastMCP or router policy into `server/domain/` |
| `server/adapters/mcp/areas/reference.py`, `reference_checkpoint_compare.py`, `reference_images_runtime.py`, `reference_truth.py`, `reference_understanding.py`, and `reference_view_diagnostics.py` | Reference/checkpoint assembly | Treat `reference.py` as the thin orchestration facade and update the split owner seams that actually shape checkpoint, RU, and staged feedback payloads |
| `server/adapters/mcp/contracts/guided_flow.py`, `session_capabilities.py`, `session_capabilities_bootstrap.py`, `session_capabilities_registry.py`, `session_capabilities_state.py`, `session_capabilities_flow.py`, and `session_capabilities_runtime_glue.py` | Guided state/control plane | Extend the shipped building domain profile, bootstrap/readiness carry-forward, registry-driven role advancement, required checks, prompt requirements, and stale refresh behavior without inventing a second guided flow system |
| `server/adapters/mcp/transforms/visibility_policy.py` and `server/adapters/mcp/discovery/search_surface.py` | Guided search/visibility | Shape the bounded architecture tool window and building-specific search cues on the live runtime surface |
| `server/adapters/mcp/areas/scene.py`, `scene_guided_runtime.py`, `modeling.py`, and `mesh.py` | Bounded build surface | Keep `scene.py` as the MCP facade, update guided runtime glue where scoped enforcement lives today, and reuse or extend bounded layout/opening/support/roof tools only where the architecture flow actually needs them |
| `server/adapters/mcp/vision/` and `server/adapters/mcp/areas/reference_understanding.py` | Advisory support evidence | Consume the closed `TASK-163` RU/session seams for architecture hints without changing verifier authority |
| `server/application/services/spatial_graph.py` and `server/adapters/mcp/areas/scene_spatial_graph.py` | Relation semantics | Model wall/opening, roof/wall, beam/support, and facade rhythm interfaces in a way the verifier and staged truth surface can consume |
| `server/adapters/mcp/prompts/prompt_catalog.py`, `provider.py`, `rendering.py`, `_docs/_PROMPTS/README.md`, and a future architecture prompt asset | Prompt assets | Expose and teach an architecture-oriented guided story on the current MCP prompt surface, then keep prompt inventory docs aligned; treat `DEMO_TASK_LOW_POLY_MEDIEVAL_WELL.md` only as an optional adjacent bounded-example reference if wording or sequencing is intentionally reused |
| `tests/unit/adapters/mcp/`, `tests/unit/tools/scene/`, `tests/e2e/integration/`, and `tests/e2e/vision/` | Proof lanes | Prove architecture-domain state, search, truth, transport, and Blender-backed reconstruction behavior on the current owner seams instead of re-planning already-shipped building lanes |

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-136-01](./TASK-136-01_Building_Contract_Vocabulary_And_Gate_Templates.md) | Define the first architecture target class, vocabulary, gate templates, and staged shell/opening/roof contract |
| 2 | [TASK-136-02](./TASK-136-02_Guided_Building_Handoff_Search_And_Bounded_Surface.md) | Shape the guided building handoff, search, visibility, and bounded tool surface on current seams |
| 3 | [TASK-136-03](./TASK-136-03_Architecture_Regression_Docs_And_Closeout.md) | Lock the new architecture path with owner-lane regression, docs, and board/changelog closeout |

## Test Matrix

| Slice | Primary Validation Lane | Why |
|------|--------------------------|-----|
| building gate contract and vocabulary | unit quality-gate/reference lanes plus scene/spatial unit seams | shell/opening/roof/support semantics must remain normalized and verifier-owned |
| guided building flow/search/visibility | unit guided-flow, search, visibility, and prompt lanes | architecture discoverability must land on the current `llm-guided` surface |
| staged building truth and transport | integration gate-transport lane plus Blender-backed building E2E | blockers and recommendations must survive the real staged response path |
| docs and operator guidance | prompt/public-surface/test-doc audits | architecture docs must describe the same bounded product path the runtime emits |

## Runtime / Security Contract Notes

- consume the existing `reference_images(...)`, `router_*`, and staged
  checkpoint surfaces; do not add a new public architecture-only MCP tool
- keep `reference_understanding`, `classification_scores`, silhouette metrics,
  and segmentation artifacts advisory-only; gate pass/fail authority remains on
  the `TASK-157` verifier path
- architecture work here is bounded reconstruction support, not CAD/BIM import,
  survey-grade measurement, or code-compliance reasoning
- any new architecture-facing tool or macro must remain bounded and guided-step
  gated instead of reopening broad free-form hard-surface exposure

## Docs To Update

- `_docs/_PROMPTS/README.md`
- optional adjacent example if wording/sequencing is intentionally reused:
  `_docs/_PROMPTS/DEMO_TASK_LOW_POLY_MEDIEVAL_WELL.md`
- likely new `_docs/_PROMPTS/REFERENCE_GUIDED_ARCHITECTURE_BUILD.md`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TESTS/README.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py`
- `tests/unit/adapters/mcp/test_quality_gate_contracts.py`
- `tests/unit/adapters/mcp/test_quality_gate_intake.py`
- `tests/unit/adapters/mcp/test_quality_gate_verifier.py`
- `tests/unit/adapters/mcp/test_scene_guided_scope_requirements.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/tools/scene/test_spatial_graph_service.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`
- `tests/e2e/vision/test_goal_derived_gate_building_completion.py`
- `tests/e2e/vision/test_goal_derived_gate_support_symmetry_surfaces.py`

Adjacent shared regression when the architecture slice changes common guided
transport/public-surface behavior:

- `tests/e2e/integration/test_guided_surface_contract_parity.py`

## Changelog Impact

- add a dedicated `_docs/_CHANGELOG/*` entry when the first meaningful
  implementation slice under this umbrella ships

## Status / Board Update

- promote this as a board-level umbrella under reconstruction work
- keep it separate from creature/anatomy tracks so architecture can evolve
  around its own vision, loop, and tool-surface requirements
- do not treat current hard-surface or demo-prompt coverage as equivalent to
  delivered architecture reconstruction behavior
- keep `_docs/_TASKS/README.md` aligned with the strategic RU roadmap linkages
  while this umbrella stays promoted
