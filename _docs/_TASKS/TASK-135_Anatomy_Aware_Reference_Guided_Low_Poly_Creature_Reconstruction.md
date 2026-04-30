# TASK-135: Anatomy-Aware Reference-Guided Low-Poly Creature Reconstruction

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Category:** Reconstruction / Guided Creature Reliability
**Estimated Effort:** Large
**Dependencies:** TASK-128, TASK-157
**Follow-on After:** [TASK-128](./TASK-128_Reference_Guided_Creature_Build_Surface_And_Perception_Reliability.md)

## Objective

Move the product from generic creature blockout guidance to anatomy-aware
low-poly creature reconstruction from reference images, so an LLM operating the
MCP server can take realistic front/side animal references and build a low-poly
version that preserves major body proportions and segment structure instead of
only matching the broad silhouette.

## Business Problem

`TASK-128` is the right reliability foundation, but it intentionally stops
short of the stronger user outcome:

- shaped creature prompting and handoff
- deterministic silhouette metrics
- optional coarse part-aware perception

That improves generic creature blockout, but it does not yet close the gap for
requests such as:

- "recreate this realistic animal as low poly"
- "keep the real-world proportions"
- "preserve limb structure, not just one leg blob"
- "keep recognizable forelimb/hindlimb segmentation and major joints"

The current product ceiling is therefore still too low for anatomy-aware
reference-driven reconstruction:

- the guided story remains blockout-oriented rather than reconstruction-oriented
- planned `TASK-128` metrics are still focused on coarse silhouette and a small
  first-pass body-part vocabulary
- there is no explicit product contract for what counts as a successful
  low-poly anatomical reconstruction
- there is no promoted runtime path that ties perception evidence to a
  reconstruction-grade write-side build strategy

## Current Runtime Baseline

The repo already has the foundations this umbrella should build on:

- `llm-guided` search-first bootstrap and goal-scoped reference intake
- typed `guided_handoff` and guided visibility shaping
- staged `reference_compare_*` and `reference_iterate_stage_checkpoint(...)`
  loops
- bounded modeling, mesh, inspection, measure/assert, and correction macros
- the `TASK-128` direction for creature-oriented prompting, silhouette metrics,
  and optional part-aware perception

This matters because the follow-on should extend the current guided/reference
product path, not replace it with an unrelated one-shot generator story.

## Generic Gate Dependency

This umbrella is the first creature-specific consumer of
[TASK-157](./TASK-157_Goal_Derived_Quality_Gates_And_Deterministic_Verification.md).
The creature work should not hardcode one squirrel checklist into the runtime.
Instead:

- the LLM may propose creature-specific gates from the prompt and references
- the server normalizes those gates into the generic gate vocabulary from
  `TASK-157`
- deterministic scene/spatial/mesh/reference evidence decides whether the gate
  passed
- the creature domain supplies templates, defaults, relation semantics, and
  target-specific policy for common quadruped mammals
- creature-specific prompts and future perception outputs may seed gate
  proposals or shape-profile evidence, but this umbrella does not pull SAM,
  CLIP, or another heavy perception adapter into the baseline implementation

## Current Capability Ceiling

If `TASK-128` lands completely, the product should be materially better at:

- generic low-poly creature blockout
- silhouette-driven proportion repair
- coarse part-aware hints for areas such as head, ear, snout, torso, tail, and
  paw

But that is still below the desired bar for anatomy-aware low-poly
reconstruction from realistic references. The missing capability is not
"realism" in shading/detail. The missing capability is structurally preserving
how the animal is put together at low-poly fidelity.

## Current Drift To Resolve

The follow-on gap to close is:

- real guided squirrel runs can still finish as primitive-only blockouts that
  contain the expected object names but lack key visual details such as eyes,
  visible part seating, and a curved tail silhouette
- the public guided story does not yet promise or define anatomy-aware
  reconstruction for common creature builds
- the expected fidelity bar is not yet explicit:
  - preserve major masses only
  - versus preserve major anatomical segments and joints at low-poly fidelity
- the current and planned creature vocabularies are still too coarse for limb
  structure, such as upper/lower forelimb and upper/lower hindlimb segments
- the current and planned metric bundles are still too coarse for segment-level
  proportion drift, limb placement, and joint-band placement
- the guided/reference loop still lacks explicit relation semantics for common
  creature attachments and body-part seating, such as:
  - ear to head
  - eye to head
  - snout to head
  - tail to torso/back
  - forelimb to torso
  - hindlimb to pelvis/torso
- the current corrective path does not yet clearly distinguish:
  - intentional organic attachment or seating
  - expected embedded/transition zones
  - bad floating gaps
  - bad free intersections that really should be cleaned up
- the write-side build story is still framed as bounded guided modeling, not as
  a reconstruction-oriented contract with a clear "all required body parts are
  present and proportionally plausible" completion bar
- evaluation/regression planning does not yet define representative
  anatomy-aware front/side creature scenarios as a shipped product target

## Business Outcome

If this umbrella is done correctly, the repo gains:

- one explicit product story for anatomy-aware low-poly creature
  reconstruction from front/side references
- a first promoted target class for reconstruction-oriented guided sessions:
  common quadruped mammals, with species-specific variation allowed inside one
  generic contract
- a clearer low-poly fidelity bar that preserves major body structure instead
  of only broad silhouette likeness
- a more useful path for realistic-reference-to-low-poly requests where the
  result should retain recognizable body-part segmentation
- a stronger bridge between perception evidence, guided handoff, and future
  write-side reconstruction surfaces aligned with the repo's broader
  reconstruction direction
- a clearer relation-aware story for when parts should attach, seat, remain
  separate, or be treated as erroneous overlaps during low-poly creature work

## Product Design Requirements

### Business Quality Bar

The creature output is acceptable only when it visibly reads as a low-poly
creature assembled from grounded references, not merely as named primitives.

| Quality Area | Minimum Bar | Latest Squirrel Failure |
|--------------|-------------|-------------------------|
| Required details | Required visible roles such as eyes/snout/ears exist unless explicitly waived | no eyes were created |
| Required seams | Head/body, tail/body, limb/body, snout/head, and eye/head gates are seated or intentionally embedded | multiple parts floated or only bbox-touched |
| Shape profile | Major reference-driven profiles are represented, for example a curved squirrel tail | tail was one vertical oval |
| Form refinement | Primary parts are profiled enough to read as low-poly anatomy | body/limbs remained sphere blobs |
| Completion truth | Final status is based on gate verification, not prose | "no intersections" was treated as done |

### Vision Mode

- Define creature-oriented part-relation semantics in addition to part labels,
  so the vision/perception layer can describe not only "what part this is" but
  also the expected relation to neighboring structure:
  - attached
  - seated
  - partially embedded / rooted
  - articulated
  - mirrored pair
  - intentionally separate
- Add relation-aware findings for common creature cases such as:
  - ear seated too high / too detached from head
  - eye floating off the skull instead of being seated
  - snout disconnected from head mass
  - tail detached from body root
  - limb attached to the wrong band or floating away from the torso
- Define which relation mismatches should count as:
  - acceptable low-poly anatomical transitions
  - true attachment errors
  - true cleanup/intersection errors

### Loop System

- Extend the creature loop so it can report relation-aware failures rather than
  only generic gap/overlap findings
- Define relation-aware decision rules for when the loop should prefer:
  - `macro_attach_part_to_surface`
  - `macro_align_part_with_contact`
  - `macro_cleanup_part_intersections`
  - a modeling/mesh-first reshape instead of a macro move
- Prevent overlap-only truth from dominating cases where slight embedding or
  seating is the intended anatomical result
- Add staged loop expectations for assembled creature checkpoints that verify:
  - all required parts exist
  - the part is on the correct body region
  - the part has the intended relation to that region

### `llm-guided` Profile

- Update creature-oriented prompt assets and guided handoff stories so they
  teach relation semantics explicitly instead of only "keep parts separate"
- Make the guided creature story tell the model which parts should remain
  separate objects while still being attached/seated in space
- Shape prompt/handoff/recommendation language so the model does not interpret
  every detected overlap on creature parts as something to clean up blindly

### Tool Surface

- Define a relation-aware macro selection policy for assembled creature parts
- Evaluate whether the current macro layer is enough once relation semantics
  are explicit, or whether the repo needs bounded creature-specific
  attachment/seating helpers beyond today's generic pair macros
- Ensure structured loop outputs can carry relation type, intended attachment
  zone, and recommended correction family instead of only raw pair overlap/gap
  facts

## Scope

This umbrella covers:

- defining the product contract for anatomy-aware low-poly creature
  reconstruction from front/side references
- defining the first target domain and fidelity bar for reconstruction-ready
  creature work
- expanding the creature/anatomy vocabulary beyond coarse whole-part labels so
  low-poly reconstruction can reason about major segment structure
- defining reconstruction-relevant metric/hint outputs for proportions,
  segment lengths, limb placement, and coarse joint placement while preserving
  the current perception/truth boundary
- defining creature-specific part-relation semantics and relation-aware macro
  selection for assembled low-poly anatomy
- shaping guided handoff, visibility, search, prompts, and evaluation around a
  reconstruction-oriented creature path rather than only a generic blockout
  path
- defining how this reconstruction story should connect to future bounded
  write-side reconstruction surfaces when that work is promoted

This umbrella does **not** cover:

- photoreal materials, fur, or render-detail reproduction
- exact zoological correctness for every species
- arbitrary multi-view photogrammetry or unrestricted one-shot 3D
  reconstruction
- making vision outputs authoritative scene truth
- forcing heavyweight segmentation or GPU-heavy models into the default runtime
- rigging, animation, or motion reconstruction

## Acceptance Criteria

- the repo has one explicit public story for anatomy-aware low-poly creature
  reconstruction on `llm-guided`
- the first promoted reconstruction target class is explicit and regressionable
  instead of remaining implied in prose examples
- the shipped contract defines what low-poly anatomical preservation means for
  that target class, including major required body regions and segment
  boundaries where applicable
- the guided/reference loop can represent missing, merged, misplaced, or
  misproportioned major anatomical segments without collapsing everything into
  generic silhouette feedback
- the guided/reference loop can represent expected part relations for major
  creature attachments and can distinguish wrong floating gaps from acceptable
  seated/attached transitions
- the product defines when attachment/seating issues should prefer
  `macro_attach_part_to_surface` or `macro_align_part_with_contact` instead of
  defaulting to generic overlap cleanup
- guided handoff/recommendation/search shaping can steer the model toward a
  reconstruction-oriented creature path rather than only a generic blockout
  path
- docs, runtime behavior, evaluation criteria, and regression coverage describe
  the same shipped capability and the same explicit limitations
- `TASK-128` closure is no longer implicitly treated as equivalent to
  anatomy-aware creature reconstruction delivery

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
- future reconstruction-oriented MCP/tool surfacing under `server/adapters/mcp/`
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

## Repository Touchpoint Table

| Path / Module | Scope | Expected Work |
|---------------|-------|---------------|
| `server/adapters/mcp/contracts/reference.py` | Reference loop contracts | Add creature gate summaries and completion blockers once `TASK-157` contracts exist |
| `server/adapters/mcp/contracts/quality_gates.py` | Generic dependency | Consume normalized gate types for creature-specific templates |
| `server/adapters/mcp/areas/reference.py` | Checkpoint assembly | Include creature gate status, missing visual roles, and seam/profile blockers in compare/iterate results |
| `server/adapters/mcp/session_capabilities.py` | Guided state | Persist creature gate plan, role cardinality, stale gate versions, and next gate actions |
| `server/application/services/spatial_graph.py` | Truth mapping | Map creature seam relations to `attachment_seam` and `support_contact` gate evidence |
| `server/adapters/mcp/areas/scene.py` | Bounded macros | Use attach/align/arc/profile macros as gate repair tools |
| `server/adapters/mcp/areas/mesh.py` | Form refinement | Expose bounded mesh tools during the creature refinement gate window |
| `server/adapters/mcp/areas/modeling.py` | Primitive and transform | Keep primary/secondary creation role-aware and mark affected gates stale |
| `server/adapters/mcp/discovery/search_documents.py` | Search shaping | Bias creature gate blockers toward attachment, arc-tail, eye/detail, and mesh-profile tools |
| `server/router/infrastructure/tools_metadata/` | Metadata | Add gate-oriented hints for creature repair/refinement tools |
| `blender_addon/application/handlers/mesh_handler.py` | E2E-backed behavior | Update only if mesh refinement gates require new Blender operations |
| `blender_addon/application/handlers/modeling_handler.py` | E2E-backed behavior | Update only if profile/appendage macros need new primitive or transform support |
| `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md` | Prompt guidance | Teach dynamic gates, required seams, eyes/detail, tail chain, and refinement window |
| `_docs/_MCP_SERVER/README.md` | Public contract | Document creature gate status and repair recommendations |
| `_docs/_TESTS/README.md` | Test lanes | Document creature gate unit/E2E regression commands |

## First Execution Slices

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-135-01](./TASK-135-01_Creature_Blockout_Completion_Contract_And_Required_Detail_Gates.md) | Prevent primitive-only creature runs from completing when required visual details or seated required seams are missing |
| 2 | [TASK-135-02](./TASK-135-02_Curved_Tail_And_Organic_Appendage_Build_Path.md) | Turn curved/bushy tails into an explicit tail-chain and arc-building path instead of one detached oval |
| 3 | [TASK-135-03](./TASK-135-03_Low_Poly_Form_Refinement_Mesh_Window_And_Profile_Macros.md) | Add a bounded mesh/modeling refinement window after primitive placement so low-poly forms can be profiled instead of left as blobs |

## Test Matrix

| Layer | Tests To Add / Update |
|-------|------------------------|
| Unit gate templates | Creature template adds required roles and seams for common quadruped mammals |
| Unit role/cardinality | `eye_pair`, `ear_pair`, `foreleg_pair`, and `hindleg_pair` require complete pairs |
| Unit seam verification | `floating_gap` blocks completion for required creature seams |
| Unit search/visibility | Active creature gate exposes only bounded relevant repair/refinement tools |
| Unit reference loop | `reference_iterate_stage_checkpoint(...)` reports gate blockers and refuses completion |
| Unit macro contracts | Attach/align/arc/profile macros expose structured gate-repair evidence |
| E2E macro | Tail/body, limb/body, snout/head, and eye/head seam repairs satisfy gate checks |
| E2E vision creature | Primitive-only squirrel without eyes, seated seams, and curved tail fails final completion |
| E2E guided runtime | Creature flow advances from primitive placement to refinement gate without broad catalog exposure |
| Docs tests | Prompt/MCP/test docs describe the same creature gate semantics |

## Docs To Update

- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TESTS/README.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- focused unit coverage under `tests/unit/adapters/mcp/` for guided handoff,
  prompt exposure, search shaping, reference contracts, and reconstruction
  reporting surfaces
- focused unit coverage under `tests/unit/router/` if reconstruction-oriented
  session shaping or contract behavior crosses the router boundary
- representative `tests/e2e/vision/` coverage for front/side
  anatomy-aware creature reconstruction scenarios
- relation-aware regression coverage for part-attachment cases such as ear/head,
  eye/head, snout/head, tail/body, and limb/body seating
- representative `tests/e2e/router/` coverage for reconstruction-oriented
  guided handoff and session recovery flows

## Changelog Impact

- add a dedicated `_docs/_CHANGELOG/*` entry when the first meaningful
  implementation slice under this umbrella ships

## Status / Board Update

- promote this as a board-level follow-on after `TASK-128`
- this umbrella now has first execution slices for completion gates, curved
  tail/appendage construction, and low-poly form refinement
- use `TASK-157` as the generic gate substrate and keep this task focused on
  creature-specific templates, evidence, and tooling
- use this umbrella to separate "generic creature blockout reliability" from
  "anatomy-aware low-poly reconstruction from realistic references"
