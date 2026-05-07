# TASK-138: Anatomy-Aware Reference-Guided Biped and Fantasy Character Reconstruction

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Category:** Reconstruction / Characters and Anatomy
**Estimated Effort:** Large
**Dependencies:** TASK-037, TASK-120, TASK-122, TASK-124, TASK-135, TASK-157, TASK-163

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

- character-like goals still fall through the creature-oriented prompt/search
  fallback instead of reaching a dedicated character domain story
- no explicit product contract for character reconstruction fidelity
- no humanoid anatomy vocabulary in the guided/reference loop
- no loop design for torso/limb/head/hands/feet stages
- no explicit boundary between body reconstruction and garment/armor/rig
  follow-ons

## Current Runtime Baseline

The repo already has foundations this umbrella should build on:

- `llm-guided` goal/reference intake and staged compare/iterate loops
- the current prompt catalog and guided-session bootstrap can detect
  character-like wording, but only by routing it through the existing creature
  prompt asset and the current `generic` / `creature` / `building`
  domain-profile split
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

- the public guided story still routes many character-like goals through the
  creature fallback instead of defining biped/fantasy reconstruction as a
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
- the guided/reference loop does not yet encode relation semantics for major
  body-part and attachment cases such as:
  - head seated on neck/torso block
  - arm attached to shoulder band
  - leg attached to pelvis/hip block
  - hand/foot seated at limb ends
  - fantasy appendage rooted to the intended body region
  - armor/garment seated on the body instead of floating or intersecting
- the current corrective path does not yet clearly distinguish:
  - expected seated or articulated attachment
  - acceptable low-poly transition/embedding zones
  - bad floating gaps
  - bad cleanup-worthy intersections
- the loop contract does not yet express character-specific reconstruction
  failures or staging
- `llm-guided` has no dedicated character prompt asset, guided-handoff recipe,
  `guided_flow_state.flow_id`, or search-bias path; the current fallback still
  points character-like goals at creature-oriented surfaces
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
- a relation-aware body/attachment story so the product can distinguish
  intended body-part seating from true geometry failures

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
- Define character-specific relation semantics for:
  - seated on
  - attached to
  - articulated from
  - mirrored pair
  - rooted appendage
  - body-mounted garment/armor
  - intentionally separate prop
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
- Add relation-aware loop findings so character corrections can distinguish:
  - intended limb seating vs detached floating limb
  - acceptable neck or shoulder transition vs bad collision cleanup
  - armor seated on body vs armor intersecting the body incorrectly
  - appendage rooting vs appendage floating
- Integrate truth-first follow-up for:
  - symmetry
  - dimensions/proportions
  - contact/overlap
  - staged readiness before a later armature handoff

### `llm-guided` Profile

- Add character-specific prompt assets and recommendation paths
- Define character-specific guided handoff recipes so the model does not treat
  humanoids as generic creatures or generic organic masses
- Make the character guided story explicit about body-part relation semantics,
  so the model knows which elements should attach, seat, articulate, remain
  mirrored, or remain intentionally separate
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
- Define a relation-aware correction and macro-selection policy so character
  loops can choose between attach/align/support/cleanup/reshape operations from
  explicit body semantics instead of raw overlap alone
- Keep any new tools bounded and domain-shaped instead of exposing a free-form
  character-sculpt workflow as the default public story

## Scope

This umbrella covers:

- character-specific prompt, handoff, and search shaping
- biped/fantasy anatomy-aware reference interpretation and metric design
- loop-system outputs for staged body reconstruction
- body-part relation semantics and relation-aware correction policy for body,
  appendages, garments, and armor
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
- the loop can represent expected seated/attached/articulated relations for
  major body parts and can distinguish them from true floating/collision
  failures
- the loop contract can steer staged reconstruction across torso/limb/head and
  attachment phases
- `llm-guided` can recommend and expose a character-oriented guided handoff path
- docs, runtime behavior, and evaluation criteria describe the same bounded
  character capability and its limitations

## Repository Touchpoints

- Treat the table below as the canonical exact owner map when a touchpoint needs
  narrower file-level scope than this flat inventory.
- `server/adapters/mcp/contracts/guided_flow.py`
- `server/adapters/mcp/contracts/router.py`
- `server/adapters/mcp/prompts/prompt_catalog.py`
- `server/adapters/mcp/prompts/provider.py`
- `server/adapters/mcp/prompts/rendering.py`
- likely new `_docs/_PROMPTS/REFERENCE_GUIDED_CHARACTER_BUILD.md`
- `server/adapters/mcp/guided_mode.py`
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
- `server/adapters/mcp/areas/reference_feedback.py`
- `server/adapters/mcp/areas/reference_truth.py`
- `server/adapters/mcp/areas/reference_understanding.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_guided_flow_domain_profiles.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_prompt_catalog.py`
- `tests/unit/adapters/mcp/test_prompt_catalog_flow_mapping.py`
- `tests/unit/adapters/mcp/test_prompt_provider.py`
- `tests/unit/adapters/mcp/test_prompt_provider_flow_bundles.py`
- `tests/unit/adapters/mcp/test_router_elicitation.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_session_phase.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_quality_gate_contracts.py`
- `tests/unit/router/application/test_router_contracts.py`
- `tests/unit/router/infrastructure/test_mcp_tools_metadata_alignment.py`
- `tests/e2e/integration/`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/router/test_guided_manual_handoff.py`
- `tests/e2e/vision/`
- `_docs/_VISION/`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TESTS/README.md`
- `_docs/_TASKS/README.md`

## Repository Touchpoint Table

| Path / Module | Scope | Expected Work |
|---------------|-------|---------------|
| `server/adapters/mcp/vision/prompting.py`, `server/adapters/mcp/vision/parsing.py`, `server/adapters/mcp/areas/reference_understanding.py`, `server/adapters/mcp/areas/reference_feedback.py`, `server/adapters/mcp/contracts/quality_gates.py`, `server/adapters/mcp/transforms/quality_gate_verifier.py`, `server/adapters/mcp/contracts/reference.py`, and `server/adapters/mcp/contracts/guided_flow.py` | Character-aware RU, support metrics, and gate contract | Keep advisory vocabulary and gate seeding on the RU path, keep server-owned support metrics on `reference_feedback.py`, and keep authoritative pass/fail semantics on the verifier path while introducing the first `character` domain-profile contract |
| `server/adapters/mcp/contracts/router.py`, `server/adapters/mcp/guided_mode.py`, `server/adapters/mcp/session_capabilities.py`, `server/adapters/mcp/session_capabilities_bootstrap.py`, `server/adapters/mcp/session_capabilities_registry.py`, `server/adapters/mcp/session_capabilities_state.py`, `server/adapters/mcp/session_capabilities_flow.py`, and `server/adapters/mcp/session_capabilities_runtime_glue.py` | Guided handoff and state | Introduce one explicit character recipe / flow-id pair, role sequencing, prompt bundle wiring, registry-driven step advancement, and handoff wording without widening armature runtime behavior |
| `server/adapters/mcp/prompts/prompt_catalog.py`, `server/adapters/mcp/prompts/provider.py`, `server/adapters/mcp/prompts/rendering.py`, and a future `REFERENCE_GUIDED_CHARACTER_BUILD` prompt asset | Prompt assets | Expose a character-specific guided story instead of routing character-like goals through the creature prompt fallback |
| `server/adapters/mcp/transforms/visibility_policy.py`, `server/adapters/mcp/discovery/search_documents.py`, and `server/adapters/mcp/discovery/search_surface.py` | Guided surface and discovery | Bias the bounded body-first surface, search cues, and recovery path around the character recipe plus explicit appendage / garment follow-ons |
| `server/router/infrastructure/tools_metadata/modeling/modeling_create_primitive.json`, `server/router/infrastructure/tools_metadata/modeling/modeling_transform_object.json`, `server/router/infrastructure/tools_metadata/mesh/mesh_select.json`, `mesh_select_targeted.json`, `mesh_extrude_region.json`, `mesh_loop_cut.json`, `mesh_bevel.json`, `mesh_symmetrize.json`, `server/router/infrastructure/tools_metadata/scene/macro_attach_part_to_surface.json`, `macro_align_part_with_contact.json`, `macro_cleanup_part_intersections.json`, `macro_place_symmetry_pair.json`, `macro_place_supported_pair.json`, `macro_adjust_relative_proportion.json`, `macro_adjust_segment_chain_arc.json`, `server/router/infrastructure/tools_metadata/reference/reference_images.json`, `reference_compare_stage_checkpoint.json`, and `reference_iterate_stage_checkpoint.json` | Router metadata | Keep discovery text, related tools, and parameter alignment in sync with the character guided surface and validate that JSON/schema state through the repo metadata alignment lane |
| `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_feedback.py`, and `server/adapters/mcp/areas/reference_truth.py` | Staged truth, planner, and checkpoints | Surface character-domain blockers, support metrics, relation semantics, orchestrator feedback, and checkpoint envelopes on the existing reference/truth surfaces |
| `tests/unit/adapters/mcp/test_guided_mode.py`, `test_guided_flow_domain_profiles.py`, `test_guided_flow_state_contract.py`, `test_prompt_catalog.py`, `test_prompt_catalog_flow_mapping.py`, `test_prompt_provider.py`, `test_prompt_provider_flow_bundles.py`, `test_router_elicitation.py`, `test_search_surface.py`, `test_session_phase.py`, `test_visibility_policy.py`, `test_vision_parsing.py`, `test_vision_prompting.py`, `test_quality_gate_contracts.py`, `tests/unit/router/application/test_router_contracts.py`, `tests/unit/router/infrastructure/test_mcp_tools_metadata_alignment.py`, `tests/e2e/router/test_guided_manual_handoff.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, `tests/e2e/integration/test_guided_surface_contract_parity.py`, `tests/e2e/vision/test_reference_understanding_runtime_surface.py`, `tests/e2e/vision/test_reference_stage_truth_handoff.py`, and future character-focused `tests/e2e/vision/` lanes | Proof lanes | Prove domain selection, prompt bundling, search/visibility shaping, metadata alignment, router contracts, router handoff, staged transport, runtime surface parity, reference feedback envelopes, and future body-first character reconstruction boundaries on the current seams |

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-138-01](./TASK-138-01_Humanoid_Contract_Symmetry_And_Fidelity_Tiers.md) | Define the first humanoid/fantasy target classes, body vocabulary, symmetry rules, and fidelity tiers |
| 2 | [TASK-138-02](./TASK-138-02_Guided_Character_Flow_Appendage_And_Garment_Boundaries.md) | Shape the guided body-first flow, appendage/armor boundaries, and bounded tool surface |
| 3 | [TASK-138-03](./TASK-138-03_Character_Regression_Docs_And_Rig_Handoff_Closeout.md) | Lock the domain with regression, docs, and explicit rig-handoff boundary proof |

## Test Matrix

| Slice | Primary Validation Lane | Why |
|------|--------------------------|-----|
| humanoid vocabulary, symmetry, and fidelity tiers | unit prompt/parser/reference plus verifier-support lanes | the first failure mode is generic-creature drift or incorrectly treating RU/support metrics as authoritative character truth |
| guided character flow and bounded surface | unit guided-flow, domain-profile, prompt-bundle, visibility, search, metadata-alignment, and router-handoff lanes | body-first reconstruction must stay separate from appendage/garment follow-ons and later rigging handoff without changing armature runtime contracts |
| staged truth and transport | integration gate-transport lane, router handoff regression, plus future character E2E | staged blockers, domain-specific envelopes, and handoff semantics must survive the real response path |
| docs and operator guidance | prompt/public-surface/test-doc audits | character scope and rig-handoff boundaries must match the shipped runtime story |

## Runtime / Security Contract Notes

- keep character reconstruction on existing `reference_images(...)`, `router_*`,
  and staged checkpoint surfaces; do not add a new public character-only MCP
  tool without dedicated review
- keep `reference_understanding`, classifier scores, silhouette metrics, and
  segmentation artifacts advisory-only; gate pass/fail authority remains on the
  `TASK-157` verifier path
- body reconstruction, garment/armor seating, appendage handling, and later
  armature handoff must stay explicitly separated; this umbrella does not ship a
  full rigging workflow
- do not expose unconstrained hero-character sculpting as the default public
  path

## Docs To Update

- `_docs/_PROMPTS/README.md`
- likely new `_docs/_PROMPTS/REFERENCE_GUIDED_CHARACTER_BUILD.md`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TESTS/README.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- focused unit coverage under `tests/unit/adapters/mcp/` for character RU
  parsing/prompting, guided domain-profile selection, prompt-bundle exposure,
  router handoff, search shaping, visibility, and reference/gate contracts
- focused metadata-alignment coverage in
  `tests/unit/router/infrastructure/test_mcp_tools_metadata_alignment.py`
  whenever router metadata JSON files change for the character surface
- router handoff regression coverage in
  `tests/e2e/router/test_guided_manual_handoff.py`
- representative future `tests/e2e/vision/` coverage for
  biped/fantasy-character scenarios plus integration coverage for staged
  transport

## Changelog Impact

- add a dedicated `_docs/_CHANGELOG/*` entry when the first meaningful
  implementation slice under this umbrella ships

## Status / Board Update

- promote this as a board-level umbrella under reconstruction work
- keep it explicitly downstream of the creature anatomy branch so shared
  anatomy/perception lessons can carry over without conflating quadruped and
  humanoid domains
- if later work needs real `server/adapters/mcp/areas/armature.py` or armature
  runtime changes, promote that as a separate follow-on instead of widening
  this body-first family
- do not treat generic creature guidance or existing rigging tools as
  equivalent to delivered biped/fantasy-character reconstruction behavior
