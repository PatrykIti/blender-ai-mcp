# LLM Guide v2: Spatial Intelligence Layer for Blender MCP

## Purpose

This document reframes "LLM guide mode" as a **spatial intelligence layer**
that fits the current `blender-ai-mcp` architecture.

The goal is not to add one vague "scene graph AI" beside the existing system.
The goal is to make the current MCP product surface more spatially legible to
LLMs by adding **typed, machine-readable spatial state**, **typed spatial
relations**, and **bounded next-step handoffs**.

If done well, the model stops behaving like a text guesser and starts behaving
like a constrained operator that can:

- identify which object or object-set is the current structural scope
- understand which parts are supposed to be attached, separated, supported, or
  symmetric
- reason about what is visible from the current view family
- pick the right correction family instead of improvising random transforms
- hand off into mesh or sculpt refinement with much better spatial context

This must happen without regressing the key product constraint of
`llm-guided`:

- the surface must stay small
- the default loop payloads must stay bounded
- richer spatial detail must be available on demand, not pushed everywhere by
  default

---

## Problem Statement

LLMs do not understand 3D space natively.

Typical failures:

- they confuse left/right, front/back, inside/outside
- they over-trust names instead of measured geometry
- they hallucinate relations instead of computing them
- they use prose like "a bit closer" instead of typed deltas or explicit
  relations
- they choose the wrong correction family because they do not know whether the
  problem is:
  - position
  - orientation
  - scale/proportion
  - support/contact
  - overlap
  - attachment
  - visibility/occlusion

The system therefore must build spatial understanding for the model explicitly.

But it must do that in a way that avoids the old failure mode:

- too many tools
- too much payload
- too much undifferentiated context

Spatial intelligence must therefore be **adaptive and layered**, not just
"more stuff".

---

## Architectural Fit

This repo already has the right high-level split. The spatial intelligence
layer should strengthen those boundaries, not blur them.

### FastMCP Platform Layer

FastMCP should own:

- what spatial tools or structured artifacts are exposed
- how they are phased or surfaced on `llm-guided`
- prompt and discovery shaping

### Router Policy Layer

The router should own:

- deterministic correction policy
- safe parameter normalization
- bounded tool-family selection
- ask/block/override decisions

### Inspection / Assertion Layer

This layer should own:

- actual measured spatial truth
- current relation state
- attachment/support/contact/overlap verdicts
- view-space facts when camera-aware tools are added

### Vision Layer

Vision should remain:

- interpretation support
- silhouette and view-family assistance
- non-authoritative evidence

It must not become the truth source for geometry correctness.

That matches the current repository boundaries in
`_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`.

---

## Current Baseline Already in Repo

The repo is not starting from zero. Several important building blocks already
exist:

### Typed Scope and Loop State

- `guided_handoff`
- `guided_reference_readiness`
- `assembled_target_scope`
- `truth_bundle`
- `truth_followup`
- `correction_candidates`
- `refinement_route`
- `refinement_handoff`

These already act like the first spatial reasoning envelope for staged
reference-guided work.

### Typed Spatial Truth

The repo already has measured/asserted spatial primitives such as:

- `scene_get_bounding_box`
- `scene_measure_dimensions`
- `scene_measure_gap`
- `scene_measure_alignment`
- `scene_measure_overlap`
- `scene_assert_contact`
- `scene_assert_containment`
- `scene_assert_symmetry`
- `scene_assert_proportion`

The contact layer already distinguishes mesh-surface truth from bbox fallback
when possible.

### View-Coupled Iteration

The staged compare/iterate path already provides:

- deterministic capture presets
- multi-view checkpoint compare
- ranked correction handoff
- inspect/validate escalation
- silhouette-driven hints

### Bounded Repair Families

The repo already has bounded spatial repair tools such as:

- `macro_relative_layout`
- `macro_attach_part_to_surface`
- `macro_align_part_with_contact`
- `macro_place_symmetry_pair`
- `macro_place_supported_pair`
- `macro_cleanup_part_intersections`
- `macro_adjust_relative_proportion`

This is a strong foundation.

---

## What Is Still Missing

The system still lacks a few high-value spatial artifacts that would make the
LLM much more reliable.

The missing pieces are not "more prose" or "bigger prompts".
They are **typed spatial state surfaces**.

The highest-value gaps are:

1. A compact **scope graph** for the active object-set or collection
2. A compact **relation graph** for spatial relationships between objects
3. A compact **view graph** for what is visible, occluded, centered, or off-screen
4. A compact **repair planner surface** that turns truth into minimal next-step families
5. A better **sculpt handoff context** so sculpt is used on the right scope for the right reason

### Current Shipped Baseline

The first TASK-143 slice is now present in the product surface:

- `scene_scope_graph(...)` ships as a separate read-only scope artifact
- `scene_relation_graph(...)` ships as a separate read-only relation artifact
- `assembled_target_scope` now carries deterministic object-role hints
- `truth_bundle`, `truth_followup`, and `correction_candidates` reuse the same
  scope/relation derivation layer instead of keeping all of that logic private
  to the checkpoint wrapper

Those graph artifacts stay intentionally separate from the default
`reference_compare_*` / `reference_iterate_*` payloads. The guided loop can
call them on demand when a step needs richer spatial state.

---

## Design Principles

### 1. Typed State Beats Prose

The model should receive spatial facts in typed form, not infer them from long
descriptions.

Bad:

```text
The ear looks a little too far to the left and maybe a bit detached.
```

Better:

```json
{
  "pair": "Body -> Ear_L",
  "relation_kind": "embedded_attachment",
  "gap_relation": "separated",
  "gap": 0.024,
  "alignment": {
    "x": -0.12,
    "z": 0.08
  },
  "attachment_verdict": "floating_gap"
}
```

### 2. Structural Anchors Must Be Explicit

For multi-object creature scopes, the system should expose which object is the
current structural anchor.

That is already partially true in `assembled_target_scope.primary_target`.
The next step is to expose more relation context around that anchor.

### 3. Relations Must Be Computable

Use typed relations such as:

- `attached_to`
- `supported_by`
- `left_of`
- `right_of`
- `above`
- `below`
- `inside`
- `intersecting`
- `symmetric_with`
- `aligned_to`

These relations should be derived from truth tools, not guessed from prompts.

### 4. Vision Assists; Truth Decides

Vision can say:

- "the silhouette still looks too wide"
- "the tail reads too small"

Truth should decide:

- whether two objects actually touch
- whether a pair still overlaps
- whether the part is attached or floating
- whether the view target is actually centered or occluded

### 5. Prefer Minimal Next-Step Surfaces

The model should not be forced to invent the next move from raw measurements.
The system should supply a bounded next-step family:

- inspect only
- macro repair
- modeling / mesh refinement
- sculpt-region refinement

That already exists partially via `refinement_route` and `refinement_handoff`.

### 6. Keep `llm-guided` Lightweight

The guided surface exists because large tool catalogs made the model worse, not
better.

So spatial intelligence should follow these rules:

- do not expose a large new graph/tool family by default on bootstrap
- do not dump a heavyweight graph into the default compare/iterate contracts
- prefer small read-only guided-facing tools or modules
- expose richer spatial detail only when the active goal/phase/handoff needs it

This does **not** mean "never add new tools".

It means:

- new atomics are valid when they expose one stable spatial fact from Blender
- new grouped tools or bounded macros are valid when they package those facts
  or actions into a better guided-facing product surface
- but repo growth and `llm-guided` growth are different things:
  - the repository may gain new low-level building blocks
  - `llm-guided` should expose only the smallest useful subset by default

That means:

- separate spatial tools/modules are preferable to stuffing more into
  `reference_compare_*` / `reference_iterate_*`
- the loop can call those spatial tools when needed
- but the current checkpoint contracts should stay focused on compare/iterate
  semantics

---

## Recommended v2 Spatial Artifacts

The best next step is not one monolithic "Scene Graph Generator".
It is a set of small, typed artifacts.

### 1. Scope Graph

Purpose:

- tell the model what the current spatial scope actually is
- distinguish structural anchors from accessories
- reduce bad local edits on the wrong object

Suggested artifact:

```json
{
  "scope_kind": "object_set",
  "primary_target": "Squirrel_Body",
  "object_names": ["Squirrel_Head", "Squirrel_Body", "Squirrel_Tail"],
  "object_roles": {
    "Squirrel_Body": "anchor_core",
    "Squirrel_Head": "attached_mass",
    "Squirrel_Tail": "attached_appendage"
  }
}
```

Suggested future tool:

- `scene_scope_graph(...)`

This would be a read-only MCP artifact, not a new authority layer.

### 2. Relation Graph

Purpose:

- expose pairwise spatial relations in one compact object
- let the model reason over relations without manually stitching together
  individual measure/assert calls

Suggested artifact:

```json
{
  "pairs": [
    {
      "from_object": "Squirrel_Body",
      "to_object": "Squirrel_Head",
      "relation_kind": "segment_attachment",
      "gap_relation": "separated",
      "overlap_relation": "disjoint",
      "alignment": {
        "x": 0.02,
        "z": -0.11
      },
      "attachment_verdict": "floating_gap"
    }
  ]
}
```

Suggested future tool:

- `scene_relation_graph(...)`

This would likely be built on top of existing scene measure/assert tools plus
the same attachment taxonomy now used in `truth_followup`.

### Delivery Note

The scope graph and relation graph should be delivered as **separate read-only
artifacts**, not as a mandatory full payload inside every stage checkpoint
response.

The guided loop may:

- reference them
- call them on demand
- or later expose a compact summary derived from them

But the full graph should remain outside the default stage-checkpoint envelope.

### 3. View Graph

Purpose:

- tell the model what the camera or viewport is actually seeing
- reduce failures caused by occlusion, bad framing, or off-screen reasoning
- create a better bridge from geometry truth to render-based interpretation

Suggested artifacts:

- screen-space bbox / projected center
- visibility flags
- occlusion summary
- focus target coverage

Suggested future tools:

- `scene_project_to_view(object_name=..., camera_name=...|USER_PERSPECTIVE)`
- `scene_visibility_report(object_names=[...], camera_name=...)`

These would add real value for later sculpt handoff because the model could
know whether the region it wants to refine is actually visible and isolated.

### 4. Repair Planner Surface

Purpose:

- convert relation graph + truth graph into bounded next-step suggestions
- stop the LLM from choosing random transforms when the repair family is
  obvious

The repo already does part of this via:

- `truth_followup`
- `correction_candidates`
- `refinement_route`
- `refinement_handoff`

The next improvement would be to make that mapping even more explicit for:

- attachment
- support
- symmetry
- view-framing issues
- proportion drift

Suggested future artifact:

```json
{
  "repair_family": "macro",
  "recommended_tools": [
    "macro_align_part_with_contact"
  ],
  "repair_scope": {
    "part_object": "Squirrel_Tail",
    "reference_object": "Squirrel_Body"
  },
  "why": [
    "segment_attachment",
    "floating_gap",
    "no_overlap"
  ]
}
```

### 5. Sculpt Handoff Context

Purpose:

- make sculpt usable when it is justified, but only on the correct local scope
- prevent the model from using sculpt as a generic blind fix

The repo already has:

- `refinement_route`
- `refinement_handoff`
- `sculpt_region` as a bounded family in routing

The missing piece is richer context for *where* sculpt should happen.

Suggested future artifact:

```json
{
  "selected_family": "sculpt_region",
  "target_object": "Creature_Head",
  "region_reason": "local_form_deviation",
  "view_targets": ["front", "side"],
  "preconditions": [
    "target visible",
    "pair contact already acceptable",
    "major proportions already stabilized"
  ]
}
```

This would let the model know:

- sculpt is appropriate here
- but not before contact/attachment is fixed
- and not on the whole asset

---

## Proposed Concrete Tool Additions

These are the most valuable additions if the goal is "help the LLM orient in
3D better".

The intended model is:

- a **small number of guided-facing read-only tools**
- plus **goal-aware disclosure**
- not a broad new default family on the bootstrap surface

### Tier A: Highest ROI

1. `scene_scope_graph(...)`
   Returns structural scope, anchor, object roles, and current grouped target set.

2. `scene_relation_graph(...)`
   Returns typed pair relations for the current scope:
   contact, gap, overlap, attachment, support, alignment, symmetry-derived hints.

3. `scene_visibility_report(...)`
   Returns which requested objects are visible, partially visible, occluded, or off-frame from a selected view.

These three would materially improve LLM spatial reasoning immediately.

They should be exposed in a controlled way:

- not all at once on bootstrap by default
- only when the current goal/phase/handoff justifies them
- with one-step expansion from the current guided surface when needed

### Tier B: Strong Follow-On

4. `scene_project_to_view(...)`
   Returns projected 2D center and screen-space bbox for one object in one view.

5. `scene_attachment_report(...)`
   Returns a compact attachment-specific readout for named pairs or relation groups.

6. `scene_support_graph(...)`
   Returns which parts are resting on or supported by which other parts.

### Tier C: Useful Once Sculpt Exposure Grows

7. `sculpt_region_context(...)`
   Returns the local region target, current supporting relations, visibility,
   and preconditions for bounded sculpt-region work.

8. `sculpt_region_handoff(...)`
   Machine-readable handoff payload that says:
   "sculpt is now appropriate here, on this object, for this local reason."

---

## Library and Dependency Posture

The spatial-intelligence roadmap does **not** require a large dependency wave on
day one.

The rule should be:

- if a library gives the first version of one of these modules a clear,
  immediate acceleration or simplification, use it
- if a library is only useful for a later, richer wave, keep it as an explicit
  future extension instead of making it part of the baseline too early

This keeps the architecture practical and avoids turning the v1 rollout into a
dependency project.

### Already Good Baseline Building Blocks

The repo already has strong lower-level ingredients for v1 work:

- Blender-side `bmesh`
- Blender-side `BVHTree`
- Blender-side `KDTree`
- existing measure/assert tools
- existing stage-capture and viewport tools

These are enough to start building:

- `TASK-143` scope/relation graph foundations
- `TASK-144` view/visibility diagnostics foundations
- `TASK-145` planner/sculpt-handoff contracts

without requiring a heavy external geometry stack immediately.

### Reasonable v1 Accelerators

These are the only external additions that currently look like clear
accelerators rather than architectural requirements:

- `scipy.spatial`
  - useful for pair filtering, distance helpers, and compact spatial math on
    the server side
  - good fit for `TASK-143` when relation derivation grows beyond trivial bbox
    comparisons
- `networkx`
  - useful if the internal implementation of scope/relation graphs becomes
    cleaner with a real graph structure
  - good fit for `TASK-143` as an implementation detail, not a product
    requirement

These should still be adopted only if they clearly simplify implementation or
runtime behavior. The product contract must not depend on them conceptually.

### Useful Follow-On Extensions, Not v1 Requirements

These are promising, but should be treated as later extensions:

- `trimesh`
  - valuable for richer mesh-level spatial queries, OBBs, clearance, convexity,
    watertight checks, and deeper relation inference
  - likely useful as a follow-on to `TASK-143`, not as a blocker for v1
- `shapely`
  - useful for 2D footprint reasoning in layout-heavy or architecture-heavy
    workflows
  - not a core dependency for the first scope/relation/view modules
- `Open3D`
  - potentially valuable for more advanced multi-mesh proximity or raycasting
    workflows
  - too heavy to treat as an initial requirement for these modules
- `libigl`
  - niche but potentially useful for later non-watertight containment or shape
    analysis work
  - not appropriate as a baseline dependency

### Not the Priority for These Modules

These are not where the first value is:

- deep-learning 3D semantic stacks such as OpenShape / Uni3D
- PointNet++ part segmentation
- large perception-first libraries aimed at RGB-D / scan understanding

Those may be useful in later semantic enrichment waves, but `TASK-143`,
`TASK-144`, and `TASK-145` are primarily about:

- typed spatial facts
- typed view-space facts
- typed planner/handoff contracts

not about making a learned model guess 3D structure that Blender already knows.

### Per-Module Guidance

- `TASK-143`
  - strongest fit: current Blender truth tools and typed contracts
  - optional accelerator: `scipy.spatial`
  - possible internal graph helper: `networkx`
  - later extension: `trimesh`
- `TASK-144`
  - strongest fit: existing camera/viewport/isolation/control stack plus
    Blender-side view math
  - external heavy geometry libraries are not the main story here
- `TASK-145`
  - strongest fit: contracts, planner policy, router/guided adoption
  - almost all value is in typed planner outputs and precondition logic, not in
    adding new heavy geometry libraries

So the intended posture is:

- start with the current repo foundations
- use small accelerators where they give real value immediately
- keep heavy libraries as explicit later extensions
- do not make dependency growth the bottleneck for shipping the first useful
  versions of these modules

---

## How This Helps LLMs in Practice

### Without Spatial Artifacts

The model has to reconstruct 3D state from:

- tool names
- object names
- a few individual measurements
- vision summaries

That is expensive and fragile.

### With Spatial Artifacts

The model can reason like this:

1. Read scope graph
2. Read relation graph
3. Identify anchor and failing pair
4. Pick bounded repair family
5. Apply one correction
6. Re-run relation graph and view graph
7. Escalate to sculpt only when:
   - structural attachment is already acceptable
   - proportions are not wildly wrong
   - the local region is visible and isolated enough

That is a much stronger product story than "give the model more prompt text".

---

## How This Fits the Current Guided Loop

The current loop can evolve like this:

```text
router_set_goal(...)
  ↓
guided_handoff
  ↓
reference_iterate_stage_checkpoint(...)
  ↓
assembled_target_scope
truth_bundle
truth_followup
correction_candidates
refinement_route
refinement_handoff
  ↓
scene_scope_graph(...)
scene_relation_graph(...)
scene_visibility_report(...)
  ↓
bounded macro / modeling / sculpt-region step
  ↓
repeat
```

This is additive.
It does not require throwing away the existing guided loop.

It also does not require turning the existing stage-checkpoint contracts into
another massive catch-all payload.

---

## What Not To Build

Avoid these traps:

### 1. A Fuzzy All-Purpose Scene Graph Brain

Do not create a second "AI layer" that invents scene truth in prose.
Make the graph derived from measured state.

### 2. Vision-As-Truth

Do not let image interpretation decide whether objects touch, overlap, or align.
Vision should inform, not certify.

### 3. Prompt-Only Spatial Reasoning

Do not treat relation words in prompts as the authoritative scene graph.
Prompt semantics can suggest intent; measured state must define reality.

### 4. Sculpt-As-Default Fix

Do not use sculpt as the first fallback for every visible mismatch.
Sculpt should be a bounded handoff after:

- scope is known
- attachment/support is acceptable
- major proportions are stable
- the target region is visible

---

## Recommended Roadmap

### Phase 1: Formalize Existing Spatial State

Goal:

- treat current scope/truth/correction payloads as the official spatial core

Work:

- document them more explicitly as the current spatial state model
- keep them typed and stable

### Phase 2: Add Read-Only Spatial Graph Tools

Goal:

- expose scope graph, relation graph, and visibility report as first-class
  read-side tools

Work:

- `scene_scope_graph(...)`
- `scene_relation_graph(...)`
- `scene_visibility_report(...)`

Important delivery rule:

- keep them as explicit read-only tools/modules
- use goal-aware disclosure on `llm-guided`
- do not make them unconditional bootstrap-visible tools for every task domain

### Phase 3: Strengthen Repair Planner Semantics

Goal:

- let LLMs reason over bounded repair families with less guesswork

Work:

- explicit repair-family payloads
- stronger relation-specific next-step recommendations
- relation-aware object role summaries

### Phase 4: Add Sculpt Handoff Context

Goal:

- allow the guided surface to reach sculpt responsibly

Work:

- `sculpt_region_context(...)`
- view-aware sculpt preconditions
- region-level handoff instead of broad "use sculpt now"

---

## Why This Is Valuable for This MCP Server

This direction adds value because it builds directly on the repo's strengths:

- typed MCP contracts
- truth-first inspection/assertion
- bounded macros
- guided handoff
- staged compare/iterate loops
- deterministic refinement-family routing

It does **not** require a redesign into a generic agent framework.

It improves exactly the product problem that matters:

- helping the LLM know what exists
- where it is
- how it relates to other parts
- what the next safe correction family should be

That is the path that will make later mesh and sculpt workflows materially
better.

---

## Practical TL;DR

The right v2 design is:

- not "add one big Scene Graph Engine"
- but "expose typed spatial artifacts that make the current guided loop easier
  for LLMs to reason about"
- while keeping `llm-guided` small and using on-demand expansion for richer
  spatial context

The most valuable next additions are:

1. `scene_scope_graph(...)`
2. `scene_relation_graph(...)`
3. `scene_visibility_report(...)`
4. stronger repair-family payloads
5. `sculpt_region_context(...)`

If those exist, the model stops guessing space from text and starts reasoning
over structured 3D state.
