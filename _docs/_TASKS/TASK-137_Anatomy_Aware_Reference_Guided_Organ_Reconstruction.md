# TASK-137: Anatomy-Aware Reference-Guided Organ Reconstruction

**Status:** ⏳ To Do
**Priority:** 🟠 High
**Category:** Reconstruction / Organic Anatomy
**Estimated Effort:** Large
**Dependencies:** TASK-038, TASK-120, TASK-122, TASK-124, TASK-157, TASK-158, TASK-163

## Objective

Move the product from generic organic-shape tooling to anatomy-aware
reference-guided organ reconstruction, so an LLM operating the MCP server can
build simplified but structurally faithful organ models from reference images
or medical-style diagrams while preserving major masses, chambers, lobes,
cavities, and connection landmarks at an explicitly bounded fidelity level.

## Business Problem

The repo already has meaningful organic foundations:

- metaballs
- sculpt tools
- lattice-based deformation
- reference-guided staged correction loops

That is enough to make organic forms, but not enough to make organ
reconstruction a real product capability.

The missing business capability is not "can the system sculpt blobs?" but:

- can it understand organ-specific structure from references
- can it guide reconstruction in anatomy-aware stages
- can it keep the product boundary safe and explicit for medical-style content

Current limitations are:

- no promoted organ-specific prompt/handoff/search story
- no anatomy-aware product contract for organ reconstruction fidelity
- no organ-focused vision vocabulary or metric set
- no staged loop design for masses, lobes, chambers, ports, and cavities
- no explicit boundary between safe educational/visualization reconstruction and
  medical diagnosis or patient-specific reconstruction claims

## Current Runtime Baseline

The repo already has strong ingredients this umbrella should build on:

- organic modeling support from `TASK-038`
- `llm-guided` goal/reference intake
- staged `reference_compare_*` and `reference_iterate_stage_checkpoint(...)`
- refinement taxonomy that already distinguishes anatomy and organic domains
- truth-first inspect/measure/assert patterns

This follow-on should build a bounded product path on top of those pieces. It
should not blur into medical inference or unbounded clinical promises.

## Substrate Ownership And Adjacent Tracks

This umbrella is a domain consumer of already-landed guided/runtime substrates,
not a place to reopen them:

- consume the closed `TASK-157` gate/verifier substrate for gate intake,
  normalization, transport, and deterministic completion blocking
- consume the closed `TASK-158` RU contract/handoff seams for typed
  `reference_understanding` parsing, session linkage, and bounded guided
  exposure on existing surfaces
- consume the closed `TASK-163` strategy/orchestrator seams for
  `reference_orchestrator_feedback`, `reference_strategy_state`, optional
  support evidence, and existing transport projections
- stay separate from domain-consumer siblings:
  - `TASK-135` low-poly creatures
  - `TASK-136` architecture/buildings
  - `TASK-138` bipeds and fantasy characters

## Current Capability Ceiling

Today the repo can support:

- manual organ-like proxy modeling
- organic form shaping
- creature/organic visual correction loops at a coarse level

That is still below the desired bar for organ reconstruction from references.
What is missing is a domain contract for:

- organ class and fidelity expectations
- anatomy-aware perception outputs
- staged reconstruction loops
- safe limits on what the product is and is not claiming

## Current Drift To Resolve

The follow-on gap to close is:

- the public guided story does not yet define organ reconstruction as a
  first-class guided domain
- there is no explicit separation between:
  - generic organic form modeling
  - anatomy-aware organ reconstruction
- current and planned perception outputs are not yet designed around organ
  structures such as:
  - lobes
  - chambers
  - cavities
  - inlet/outlet landmarks
  - paired-organ symmetry or asymmetry expectations
- the guided/reference loop does not yet encode relation semantics for organ
  structures such as:
  - lobe fused into organ mass
  - chamber/cavity embedded inside shell
  - vessel/port attached at a landmark
  - paired organs intentionally separate but proportionally related
- the current corrective path does not yet clearly distinguish:
  - expected organic continuity / fusion
  - expected embedded cavity relations
  - expected attachment of ports or vessels
  - bad floating gaps or bad cleanup-worthy intersections
- the loop contract does not yet express organ-specific reconstruction failures
- `llm-guided` has no organ-specific prompt asset, handoff, or search-bias path
- the repo has no explicit safe product boundary for reference-guided organ
  reconstruction versus diagnosis, pathology inference, or patient-specific use

## Business Outcome

If this umbrella is done correctly, the repo gains:

- one explicit product story for organ reconstruction from references
- one bounded first-pass domain for educational, visualization, and
  concept-accurate organ models
- a safer and clearer boundary for what the product is not doing in medical
  contexts
- a more useful path from biological/medical reference images to structured
  Blender reconstruction sessions
- a relation-aware story for organ reconstruction so the product can distinguish
  expected organic attachment/embedding from true geometric failure

## Product Design Requirements

### Vision Mode

- Define supported organ/reference classes and their first-pass fidelity bars,
  such as:
  - single-mass organs
  - lobed organs
  - chambered organs
  - paired organs
- Support organ-aware reference interpretation across:
  - front/side/top references
  - simplified anatomical plates
  - sectional or cross-sectional diagram references where applicable
- Define a reusable organ/anatomy vocabulary for:
  - lobe
  - chamber
  - cavity
  - inlet/outlet/port
  - paired symmetry anchors where applicable
- Define organ-specific relation semantics for:
  - fused into mass
  - embedded cavity/chamber
  - attached inlet/outlet
  - paired but separate
  - intentionally asymmetric
- Add deterministic organ-oriented metrics and findings such as:
  - gross dimensions and volume proxy ratios
  - lobe/chamber proportions
  - cavity/chamber placement
  - curvature and asymmetry regions
  - inlet/outlet landmark placement
  - paired-organ size/symmetry checks where relevant

### Loop System

- Design staged organ reconstruction loops around phases such as:
  - primary mass
  - lobe/chamber definition
  - cavity and port landmarks
  - surface refinement
  - final validation
- Extend the loop contract so it can report organ-specific failures such as:
  - missing lobe or chamber
  - collapsed cavity
  - wrong landmark placement
  - wrong paired-organ ratio
  - excess asymmetry or missing asymmetry where anatomy expects one
- Add relation-aware loop findings so organ corrections can distinguish:
  - expected fusion vs bad surface collision
  - expected cavity embedding vs disconnected hollow shell
  - expected vessel/port attachment vs floating branch geometry
- Integrate truth-first follow-up for:
  - dimensions
  - symmetry/asymmetry checks
  - shell/cavity presence where measurable
  - topology readiness before later refinement

### `llm-guided` Profile

- Add organ-specific prompt assets and recommendation paths
- Define organ-specific guided handoff recipes so the model does not treat
  organs as just generic blobs or creature parts
- Make the organ guided story explicit about relation semantics, so the model
  knows which regions should merge, embed, attach, or remain separate
- Bias guided search toward the relevant organic tool families for natural
  requests such as:
  - rebuild this heart from diagrams
  - make a low-detail liver preserving lobes
  - reconstruct a kidney pair with the right silhouette and orientation
- Define explicit bounded fidelity tiers such as:
  - teaching proxy
  - visualization proxy
  - concept-accurate mid-detail model

### Tool Surface

- Evaluate which current tools already cover the domain and which gaps require
  new bounded surfaces
- Likely organ-oriented tool-surface gaps include bounded support for:
  - lobe/chamber mass setup
  - cavity shell creation
  - controlled inlet/outlet landmark setup
  - paired-organ mirroring with anatomy-aware exceptions
  - bounded organ refinement and cleanup handoffs
- Define a relation-aware correction policy so organ loops can choose between
  attach/embed/reshape/cleanup-style corrections from explicit organ semantics
  instead of raw overlap alone
- Keep any new surfaces bounded and anatomy-oriented; do not reopen raw
  free-form sculpting as the default public story

## Scope

This umbrella covers:

- organ-specific prompt, handoff, and search shaping
- organ-aware reference interpretation and metric design
- loop-system outputs for staged organ reconstruction
- organ-specific relation semantics and relation-aware correction policy
- safe product-boundary design for medical-style reference use
- docs, evaluation criteria, and regression planning for the domain

This umbrella does **not** cover:

- medical diagnosis or pathology interpretation
- patient-specific surgical planning
- DICOM/CT/MRI ingestion as a first-pass product surface
- regulatory or clinical-grade claims
- histology/microscopy reconstruction
- unbounded high-resolution sculpt workflows

## Acceptance Criteria

- the repo has one explicit guided product story for anatomy-aware organ
  reconstruction
- the first target class and fidelity bar are explicitly bounded and
  regressionable
- vision/reference outputs can express organ-specific findings rather than only
  generic organic mismatches
- the loop can represent expected organ relations such as fusion, embedding,
  port attachment, and paired separation instead of flattening them into generic
  overlap/gap cleanup
- the loop contract can steer staged reconstruction across mass, chamber/lobe,
  landmark, and validation phases
- `llm-guided` can recommend and expose an organ-oriented guided handoff path
- docs, runtime behavior, and evaluation criteria describe the same safe domain
  contract and limitations

## Repository Touchpoints

- `server/adapters/mcp/prompts/prompt_catalog.py`
- `server/adapters/mcp/prompts/provider.py`
- `server/adapters/mcp/prompts/rendering.py`
- likely new `_docs/_PROMPTS/REFERENCE_GUIDED_ORGAN_BUILD.md`
- `server/adapters/mcp/contracts/guided_flow.py`
- `server/adapters/mcp/contracts/router.py`
- `server/adapters/mcp/guided_mode.py`
- `server/adapters/mcp/session_capabilities.py`
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
- `server/adapters/mcp/areas/reference_images_runtime.py`
- `server/adapters/mcp/areas/reference_truth.py`
- `server/adapters/mcp/areas/reference_understanding.py`
- `server/adapters/mcp/areas/reference_feedback.py`
- `server/adapters/mcp/areas/router.py`
- `server/adapters/mcp/areas/modeling.py`
- `server/adapters/mcp/areas/mesh.py`
- `server/adapters/mcp/areas/sculpt.py`
- `server/adapters/mcp/areas/lattice.py`
- `server/router/infrastructure/tools_metadata/`
- `tests/unit/adapters/mcp/`
- `tests/unit/adapters/mcp/test_prompt_catalog.py`
- `tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py`
- `tests/unit/adapters/mcp/test_prompt_provider.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/tools/modeling/`
- `tests/unit/tools/mesh/`
- `tests/unit/tools/scene/`
- `tests/unit/tools/sculpt/`
- `tests/unit/tools/lattice/`
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
| `server/adapters/mcp/vision/prompting.py`, `server/adapters/mcp/vision/parsing.py`, `server/adapters/mcp/areas/reference_understanding.py`, and `server/adapters/mcp/areas/reference_feedback.py` | Organ-aware RU support | Add bounded organ vocabulary, fidelity hints, optional support-evidence handling, and medical-safe advisory interpretation on the existing RU seam |
| `server/adapters/mcp/contracts/quality_gates.py`, `server/adapters/mcp/contracts/reference.py`, `server/adapters/mcp/contracts/guided_flow.py`, and `server/adapters/mcp/contracts/router.py` | Domain contract | Declare organ gate vocabulary, staged blockers, prompt requirements, and any router/reference payload fields through the existing strict contracts |
| `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_images_runtime.py`, `server/adapters/mcp/areas/router.py`, and `server/adapters/mcp/areas/reference_truth.py` | Staged truth and public transport | Keep organ-specific failures, checkpoints, guided status, and attach/list/remove reference messaging on the current public surfaces instead of inventing an organ-only tool |
| `server/adapters/mcp/session_capabilities.py`, `session_capabilities_state.py`, `session_capabilities_flow.py`, `session_capabilities_runtime_glue.py`, and `guided_mode.py` | Guided state | Add organ-domain stage sequencing, required prompts, and bounded correction routing without replacing the current session model or diagnostics assembly |
| `server/adapters/mcp/transforms/visibility_policy.py` and `server/adapters/mcp/discovery/search_surface.py` | Guided surface | Shape the bounded organ tool window and organic/anatomy search cues on the live runtime surface |
| `server/adapters/mcp/areas/modeling.py`, `mesh.py`, `sculpt.py`, and `lattice.py` | Bounded reconstruction surface | Reuse or extend bounded organic/anatomy tools without turning free-form sculpt into the default public story |
| `server/adapters/mcp/prompts/prompt_catalog.py`, `provider.py`, `rendering.py`, and a future organ prompt asset | Prompt assets | Expose one safe organ-oriented guided story on the current prompt surface and keep required-prompt mapping on the declared prompt owners |
| `tests/unit/adapters/mcp/test_prompt_catalog.py`, `test_prompt_catalog_flow_mapping.py`, `test_prompt_provider.py`, `test_reference_images.py`, `test_guided_flow_state_contract.py`, `test_guided_mode.py`, `test_visibility_policy.py`, `test_search_surface.py`, `test_router_elicitation.py`, `test_contract_payload_parity.py`, `test_public_surface_docs.py`, `tests/unit/tools/modeling/test_modeling_tools.py`, `tests/unit/tools/mesh/test_mesh_organic.py`, `tests/unit/tools/sculpt/test_sculpt_tools.py`, `tests/unit/tools/lattice/test_lattice_handler.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, and `tests/e2e/vision/test_reference_understanding_runtime_surface.py` | Proof lanes | Prove safe domain boundaries, staged loop semantics, strict payloads, and bounded organ-surface behavior on the existing transport/runtime seams |

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-137-01](./TASK-137-01_Organ_Domain_Boundary_Vocabulary_And_Fidelity_Tiers.md) | Define the first safe organ target classes, anatomy vocabulary, and medical-scope guardrails |
| 2 | [TASK-137-02](./TASK-137-02_Guided_Organ_Loop_Relation_Semantics_And_Bounded_Surface.md) | Shape the guided organ loop, relation semantics, and bounded modeling/sculpt/lattice surface |
| 3 | [TASK-137-03](./TASK-137-03_Organ_Regression_Docs_And_Medical_Guardrail_Closeout.md) | Lock the domain with regression, docs, and explicit non-clinical closeout criteria |

## Test Matrix

| Slice | Primary Validation Lane | Why |
|------|--------------------------|-----|
| organ vocabulary and safe domain boundary | unit prompt/parser/reference lanes | the first risk is overclaiming or under-specifying medical/anatomy semantics |
| staged organ loop and bounded tool surface | unit guided-flow, visibility, search, sculpt, lattice, and reference lanes | the runtime must stay bounded while supporting organ-aware stages |
| transport and staged truth | integration gate-transport lane plus future organ E2E | blockers and domain-boundary messaging must survive the real response path |
| docs and operator safety | prompt/public-surface/test-doc audits | medical-safe limitations must match the shipped runtime contract |

## Runtime / Security Contract Notes

- organ reconstruction here is educational/visualization-oriented only; it is
  not diagnosis, pathology interpretation, or patient-specific planning
- keep `reference_understanding`, classifier scores, segmentation artifacts, and
  any later organ-aware perception advisory-only; gate pass/fail authority
  remains on the `TASK-157` verifier path
- do not expose unrestricted sculpt or high-resolution anatomy workflows as the
  default public story; stay within bounded modeling/sculpt/lattice slices
- do not add new public organ-only MCP tools unless a dedicated surface review
  promotes them

## Docs To Update

- `_docs/_PROMPTS/README.md`
- likely new `_docs/_PROMPTS/REFERENCE_GUIDED_ORGAN_BUILD.md`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TESTS/README.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_prompting.py`,
  `tests/unit/adapters/mcp/test_vision_parsing.py`,
  `tests/unit/adapters/mcp/test_prompt_catalog.py`,
  `tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py`,
  `tests/unit/adapters/mcp/test_prompt_provider.py`,
  `tests/unit/adapters/mcp/test_reference_images.py`,
  `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`,
  `tests/unit/adapters/mcp/test_guided_mode.py`,
  `tests/unit/adapters/mcp/test_visibility_policy.py`,
  `tests/unit/adapters/mcp/test_search_surface.py`,
  `tests/unit/adapters/mcp/test_router_elicitation.py`,
  `tests/unit/adapters/mcp/test_contract_payload_parity.py`, and
  `tests/unit/adapters/mcp/test_public_surface_docs.py` for organ prompt
  exposure, RU parsing/prompting, public payload projection, guided handoff,
  and search shaping
- `tests/unit/tools/modeling/test_modeling_tools.py`,
  `tests/unit/tools/mesh/test_mesh_organic.py`,
  `tests/unit/tools/sculpt/test_sculpt_tools.py`, and
  `tests/unit/tools/lattice/test_lattice_handler.py` for any new bounded
  organ-surface operations
- `tests/e2e/integration/test_guided_gate_state_transport.py`,
  `tests/e2e/vision/test_reference_understanding_runtime_surface.py`, and
  representative future `tests/e2e/vision/test_guided_organ_reconstruction.py`
  coverage for organ-reference scenarios and staged transport/runtime parity

## Changelog Impact

- add a dedicated `_docs/_CHANGELOG/*` entry when the first meaningful
  implementation slice under this umbrella ships

## Status / Board Update

- promote this as a board-level umbrella under reconstruction work
- keep it separate from creature and general organic-form tracks so the product
  boundary for organ reconstruction stays explicit
- do not treat existing metaball/sculpt capability as equivalent to delivered
  anatomy-aware organ reconstruction
