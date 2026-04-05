# TASK-137: Anatomy-Aware Reference-Guided Organ Reconstruction

**Status:** ⏳ To Do
**Priority:** 🟠 High
**Category:** Reconstruction / Organic Anatomy
**Estimated Effort:** Large
**Dependencies:** TASK-038, TASK-120, TASK-122, TASK-124

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

## Product Design Requirements

### Vision Mode

- Define supported organ/reference classes and their first-pass fidelity bars,
  such as:
  - single-mass organs
  - lobed organs
  - chambered organs
  - paired organs
  - simple tubular biological structures
- Support organ-aware reference interpretation across:
  - front/side/top references
  - simplified anatomical plates
  - sectional or cross-sectional diagram references where applicable
- Define a reusable organ/anatomy vocabulary for:
  - lobe
  - chamber
  - cavity
  - inlet/outlet/port
  - stalk/branch entry points
  - paired symmetry anchors where applicable
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
- Integrate truth-first follow-up for:
  - dimensions
  - symmetry/asymmetry checks
  - shell/cavity presence where measurable
  - topology readiness before later refinement

### `llm-guided` Profile

- Add organ-specific prompt assets and recommendation paths
- Define organ-specific guided handoff recipes so the model does not treat
  organs as just generic blobs or creature parts
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
  - controlled organic branching or inlet/outlet setup
  - paired-organ mirroring with anatomy-aware exceptions
  - bounded organ refinement and cleanup handoffs
- Keep any new surfaces bounded and anatomy-oriented; do not reopen raw
  free-form sculpting as the default public story

## Scope

This umbrella covers:

- organ-specific prompt, handoff, and search shaping
- organ-aware reference interpretation and metric design
- loop-system outputs for staged organ reconstruction
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
- the loop contract can steer staged reconstruction across mass, chamber/lobe,
  landmark, and validation phases
- `llm-guided` can recommend and expose an organ-oriented guided handoff path
- docs, runtime behavior, and evaluation criteria describe the same safe domain
  contract and limitations

## Repository Touchpoints

- `server/adapters/mcp/prompts/`
- `server/adapters/mcp/guided_mode.py`
- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/discovery/search_documents.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/vision/`
- `server/router/infrastructure/tools_metadata/`
- future organ/anatomy-oriented MCP/tool surfacing under `server/adapters/mcp/`
- `server/domain/tools/` and `server/application/tool_handlers/` if a new
  bounded reconstruction-facing surface is introduced
- `blender_addon/application/handlers/` if addon-side support becomes necessary
- `tests/unit/adapters/mcp/`
- `tests/unit/router/`
- `tests/e2e/router/`
- `tests/e2e/vision/`
- `_docs/_PROMPTS/`
- `_docs/_VISION/`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TESTS/README.md`
- `_docs/_TASKS/README.md`

## Docs To Update

- `_docs/_PROMPTS/README.md`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TESTS/README.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- focused unit coverage under `tests/unit/adapters/mcp/` for organ prompt
  exposure, guided handoff, search shaping, and reference contracts
- focused unit coverage under `tests/unit/router/` if organ-oriented session
  shaping or correction contracts cross the router boundary
- representative `tests/e2e/vision/` coverage for organ-reference scenarios
- representative `tests/e2e/router/` coverage for organ-oriented guided handoff
  and staged recovery flows

## Changelog Impact

- add a dedicated `_docs/_CHANGELOG/*` entry when the first meaningful
  implementation slice under this umbrella ships

## Status / Board Update

- promote this as a board-level umbrella under reconstruction work
- keep it separate from creature and general organic-form tracks so the product
  boundary for organ reconstruction stays explicit
- do not treat existing metaball/sculpt capability as equivalent to delivered
  anatomy-aware organ reconstruction
