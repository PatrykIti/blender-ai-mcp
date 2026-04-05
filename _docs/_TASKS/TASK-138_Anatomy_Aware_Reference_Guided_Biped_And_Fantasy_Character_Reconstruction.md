# TASK-138: Anatomy-Aware Reference-Guided Biped and Fantasy Character Reconstruction

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Category:** Reconstruction / Characters and Anatomy
**Estimated Effort:** Large
**Dependencies:** TASK-037, TASK-120, TASK-122, TASK-124, TASK-135
**Follow-on After:** [TASK-135](./TASK-135_Anatomy_Aware_Reference_Guided_Low_Poly_Creature_Reconstruction.md)

## Objective

Move the product from generic creature reliability and coarse organic
reconstruction toward anatomy-aware biped and fantasy-character reconstruction,
so an LLM operating the MCP server can build human-like or fantasy humanoid
characters from references while preserving torso, pelvis, head, limb
segments, symmetry, and major attachment regions at a bounded low- to
mid-fidelity level.

## Business Problem

The repo is moving in the right direction for guided creature work and
cross-domain refinement, but humanoid and fantasy-character reconstruction is a
different class of problem:

- bilateral symmetry matters much more
- limb segment proportions are more specific
- torso/pelvis/shoulder relationships matter more
- head, hands, and feet have their own fidelity tiers
- garments, armor, horns, tails, wings, and props create domain boundaries

The missing business capability is not "can the system build a character-like
shape?" but "can it reconstruct a human-like or fantasy-humanoid structure from
references in a domain-aware, staged, and bounded way?"

Current limitations are:

- no promoted biped/fantasy-character prompt/handoff/search story
- no explicit product contract for character reconstruction fidelity
- no humanoid anatomy vocabulary in the guided/reference loop
- no loop design for torso/limb/head/hands/feet stages
- no explicit boundary between body reconstruction and garment/armor/rig
  follow-ons

## Current Runtime Baseline

The repo already has foundations this umbrella should build on:

- `llm-guided` goal/reference intake and staged compare/iterate loops
- cross-domain refinement taxonomy, including anatomy and organic classes
- creature-oriented reliability work under `TASK-128`
- anatomy-aware creature reconstruction direction under `TASK-135`
- symmetry, proportion, modeling, mesh, and bounded correction macros
- rigging tooling in the repo, even though it is not yet the guided
  reconstruction story

This follow-on should extend those foundations into a biped-specific guided
product path instead of assuming creature logic alone will generalize well
enough.

## Current Capability Ceiling

Today the repo can support:

- generic creature/organic blockout
- bounded symmetry and proportion fixes
- manual character-like mesh construction when the operator already knows the
  tool path

That is still below the desired bar for character reconstruction from
references. What is missing is a domain contract for:

- anatomy-aware biped structure
- fidelity tiers for body, face, hands, feet, and attachments
- staged loop guidance and evaluation
- future rigging handoff readiness

## Current Drift To Resolve

The follow-on gap to close is:

- the public guided story does not yet define biped/fantasy reconstruction as a
  first-class domain
- there is no explicit separation between:
  - generic creature reconstruction
  - humanoid/biped reconstruction
- current and planned vocabularies are too coarse for major humanoid structure:
  - torso
  - pelvis
  - upper/lower arm
  - hand
  - upper/lower leg
  - foot
  - neck/head
- current and planned metrics are too coarse for:
  - head-to-body ratio
  - shoulder/pelvis width
  - elbow/knee placement
  - limb segment ratios
  - bilateral symmetry drift
- the loop contract does not yet express character-specific reconstruction
  failures or staging
- `llm-guided` has no character-oriented prompt asset, handoff, or search-bias
  path
- the repo has no explicit domain boundary for:
  - body vs garment
  - body vs armor
  - body vs fantasy appendages
  - reconstruction vs later armature handoff

## Business Outcome

If this umbrella is done correctly, the repo gains:

- one explicit product story for reference-guided biped/fantasy-character
  reconstruction
- one bounded target class for low- and mid-fidelity character reconstruction
- a clearer bridge from references to body-structure reconstruction before
  garment, armor, props, or rigging follow-ons
- a stronger path for stylized and fantasy humanoids that still need
  recognizable human-like structure

## Product Design Requirements

### Vision Mode

- Support biped-aware reference interpretation across:
  - front and side character sheets
  - turnaround-style concept art where usable
  - neutral standing references and bounded pose-normalized variants
- Define a reusable humanoid/fantasy anatomy vocabulary for:
  - head
  - neck
  - torso
  - pelvis/hip block
  - upper/lower arm
  - hand
  - upper/lower leg
  - foot
  - major fantasy appendages such as horn, tail, wing, ear variants, when
    explicitly in scope
- Add deterministic character-oriented metrics and findings such as:
  - head-to-body height ratio
  - shoulder width and pelvis width
  - arm and leg segment ratios
  - elbow and knee height-band placement
  - hand and foot size relative to body
  - neck length and head placement
  - bilateral symmetry drift
- Define fidelity-tier boundaries for:
  - coarse body blockout
  - hands/feet placeholder fidelity
  - face mass/blockout fidelity
  - optional fantasy appendage fidelity

### Loop System

- Design staged character reconstruction loops around phases such as:
  - torso and pelvis blockout
  - legs
  - arms
  - head and neck
  - hands and feet
  - silhouette cleanup
  - optional fantasy appendages
  - optional garment/armor attachment follow-on
- Extend the loop contract so it can report character-specific failures such as:
  - missing mirrored limb
  - limb ratio drift
  - shoulder/pelvis mismatch
  - collapsed hand/foot placeholders
  - appendage misplacement
  - body/gear overlap issues
- Integrate truth-first follow-up for:
  - symmetry
  - dimensions/proportions
  - contact/overlap
  - staged readiness before a later armature handoff

### `llm-guided` Profile

- Add character-specific prompt assets and recommendation paths
- Define character-specific guided handoff recipes so the model does not treat
  humanoids as generic creatures or generic organic masses
- Bias guided search toward the relevant tool families for natural requests
  such as:
  - rebuild this humanoid from front/side refs
  - make a low-poly fantasy guard preserving silhouette and anatomy
  - block out a stylized human with correct proportions before armor
- Define explicit bounded stories for:
  - body-first mannequin reconstruction
  - fantasy appendage follow-ons
  - garment/armor attachment after body structure is stable
  - later rigging handoff readiness

### Tool Surface

- Evaluate which current tools already cover the domain and which gaps require
  new bounded surfaces
- Likely character-oriented tool-surface gaps include bounded support for:
  - mirrored limb generation and refinement
  - segment-aware proportion correction
  - body-part placeholder generation for hands/feet/head masses
  - appendage placement and cleanup
  - garment/armor seating on a stable body surface
  - later armature-handoff readiness summaries
- Keep any new tools bounded and domain-shaped instead of exposing a free-form
  character-sculpt workflow as the default public story

## Scope

This umbrella covers:

- character-specific prompt, handoff, and search shaping
- biped/fantasy anatomy-aware reference interpretation and metric design
- loop-system outputs for staged body reconstruction
- explicit product boundaries for body, appendages, garments, armor, and later
  rigging handoff
- docs, evaluation criteria, and regression planning for the domain

This umbrella does **not** cover:

- actor likeness or portrait-level face capture
- hair grooming or high-detail hair cards
- cloth simulation as a first-pass product path
- full production rigging or animation delivery
- unconstrained hero-character sculpting workflows

## Acceptance Criteria

- the repo has one explicit guided product story for biped/fantasy-character
  reconstruction
- the first target class and fidelity tiers are explicitly bounded and
  regressionable
- vision/reference outputs can express body-part and symmetry findings rather
  than only generic creature or silhouette mismatches
- the loop contract can steer staged reconstruction across torso/limb/head and
  attachment phases
- `llm-guided` can recommend and expose a character-oriented guided handoff path
- docs, runtime behavior, and evaluation criteria describe the same bounded
  character capability and its limitations

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
- future character-oriented MCP/tool surfacing under `server/adapters/mcp/`
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

- focused unit coverage under `tests/unit/adapters/mcp/` for character prompt
  exposure, guided handoff, search shaping, and reference contracts
- focused unit coverage under `tests/unit/router/` if character-oriented
  session shaping or correction contracts cross the router boundary
- representative `tests/e2e/vision/` coverage for biped/fantasy-character
  reference scenarios
- representative `tests/e2e/router/` coverage for character-oriented guided
  handoff and staged recovery flows

## Changelog Impact

- add a dedicated `_docs/_CHANGELOG/*` entry when the first meaningful
  implementation slice under this umbrella ships

## Status / Board Update

- promote this as a board-level umbrella under reconstruction work
- keep it explicitly downstream of the creature anatomy branch so shared
  anatomy/perception lessons can carry over without conflating quadruped and
  humanoid domains
- do not treat generic creature guidance or existing rigging tools as
  equivalent to delivered biped/fantasy-character reconstruction behavior
