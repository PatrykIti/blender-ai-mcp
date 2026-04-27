# TASK-136: Reference-Guided Architecture and Building Reconstruction

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Category:** Reconstruction / Architecture and Hard Surface
**Estimated Effort:** Large
**Dependencies:** TASK-118, TASK-120, TASK-122, TASK-124, TASK-130

## Objective

Move the product from generic hard-surface building blocks and isolated
macro/layout tools to a true reference-guided architecture reconstruction
surface, so an LLM operating the MCP server can rebuild small and medium
structures from plans, elevations, sections, or photo references while
preserving footprint, openings, structural rhythm, roof form, and major
proportions.

## Business Problem

The repo already supports many bounded architectural subproblems:

- placement and relative layout
- cutouts, recesses, and openings
- dimension checks and grouped scene inspection
- low-level modeling and mesh editing

That is useful, but it does not yet add up to a coherent product path for
reference-guided architectural reconstruction.

The missing business capability is not "can Blender do hard-surface work?" but
"can the guided MCP product help the model rebuild buildings and architectural
modules from references without rediscovering the whole strategy each time?"

Current limitations are:

- no promoted architecture-specific prompt/handoff/search story on
  `llm-guided`
- no explicit product contract for architectural reconstruction fidelity
- no reference-analysis contract for plans/elevations/rooflines/opening grids
- no loop-system contract for staged shell/opening/roof/support validation
- no clear domain-specific boundary between generic hard-surface tools and
  reconstruction-oriented building workflows

## Current Runtime Baseline

The repo already has strong foundations this umbrella should build on:

- `llm-guided` search-first bootstrap and goal-scoped reference intake
- staged `reference_compare_*` and `reference_iterate_stage_checkpoint(...)`
  flows
- grouped scene inspection/configuration from `TASK-118`
- bounded hard-surface and layout macros such as cutout, placement, contact,
  and proportion repair
- prompt-driven guided sessions and shaped visibility/search behavior

The follow-on should extend that product foundation into the architecture
domain. It should not reopen the old flat-catalog model or bypass the guided
surface.

## Current Capability Ceiling

Today the product can support:

- bounded hard-surface prop work
- isolated openings or placement repairs
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

- the public guided story does not yet define architectural reconstruction as a
  first-class guided domain
- the repo has no promoted distinction between:
  - generic hard-surface editing
  - reference-guided building reconstruction
- current vision/reference handling is not yet designed around
  plan/elevation/section reasoning
- the loop output does not yet express building-specific failures such as:
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
- `llm-guided` does not yet have architecture-specific recommendation, handoff,
  and search-bias behavior
- there is no explicit tool-surface roadmap for reconstruction-heavy
  architecture tasks such as opening grids, repeated supports, roof generators,
  facade rhythm, and modular structural rebuilds

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

- `server/adapters/mcp/prompts/`
- `server/adapters/mcp/guided_mode.py`
- `server/adapters/mcp/session_capabilities.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/discovery/search_documents.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/vision/`
- `server/router/infrastructure/tools_metadata/`
- future architecture-oriented MCP/tool surfacing under `server/adapters/mcp/`
- `server/domain/tools/` and `server/application/tool_handlers/` if a new
  bounded reconstruction-facing surface is introduced
- `blender_addon/application/handlers/` if addon-side support becomes necessary
- `tests/unit/adapters/mcp/`
- `tests/unit/router/`
- `tests/e2e/router/`
- `tests/e2e/vision/`
- `_docs/_PROMPTS/`
- `_docs/_PROMPTS/DEMO_TASK_LOW_POLY_MEDIEVAL_WELL.md`
- `_docs/_VISION/`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TESTS/README.md`
- `_docs/_TASKS/README.md`

## Docs To Update

- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/DEMO_TASK_LOW_POLY_MEDIEVAL_WELL.md`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TESTS/README.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- focused unit coverage under `tests/unit/adapters/mcp/` for architecture
  prompt exposure, guided handoff, search shaping, and reference contracts
- focused unit coverage under `tests/unit/router/` if architecture-oriented
  session shaping or correction contracts cross the router boundary
- representative `tests/e2e/vision/` coverage for plan/elevation-driven
  architecture scenarios
- relation-aware regression coverage for wall/opening, roof/wall, beam/support,
  and facade-module interface cases
- representative `tests/e2e/router/` coverage for architecture-oriented guided
  handoff and staged recovery flows

## Changelog Impact

- add a dedicated `_docs/_CHANGELOG/*` entry when the first meaningful
  implementation slice under this umbrella ships

## Status / Board Update

- promote this as a board-level umbrella under reconstruction work
- keep it separate from creature/anatomy tracks so architecture can evolve
  around its own vision, loop, and tool-surface requirements
- do not treat current hard-surface or demo-prompt coverage as equivalent to
  delivered architecture reconstruction behavior
