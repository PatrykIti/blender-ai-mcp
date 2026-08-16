# FEATURES_LLM_GUIDE_V1

Research handoff brief for external LLMs and research agents.

Snapshot date: April 6, 2026.

This document is intentionally written in English so it can be pasted directly
into other models, research assistants, or institutional research workflows.

## Purpose

Use this file to explain what `blender-ai-mcp` already offers and to ask other
models to research how modern LLMs, VLMs, and related multimodal systems handle
3D spatial understanding, multi-view reasoning, scene structure, and geometry-
aware action planning.

The goal is not only to collect papers. The goal is to identify which research
directions can materially improve:

- the next version of the repo's `LLM guide`
- the MCP server's shaped public surface
- router decision logic and execution policy
- structured tool contracts for spatial work
- the compare, verify, and correction loop

## What This Project Is

`blender-ai-mcp` is a production-shaped MCP server for Blender.

It does not treat Blender automation as raw code generation. Instead, it
exposes a stable tool API and a structured runtime:

- `server/` provides the FastMCP tool surface.
- `server/router/` provides goal-first routing, deterministic policy,
  workflows, correction, and session context.
- `blender_addon/` executes the actual Blender `bpy` operations safely on
  Blender's main thread.

Core product idea:

- do not ask the model to improvise `bpy` scripts
- give the model a bounded tool surface
- keep execution deterministic where possible
- use inspection, measurement, and assertions as the truth layer
- use vision as an assistant, not as the final authority

## Current Architecture Boundaries

The repo explicitly separates four roles:

- FastMCP platform layer:
  discovery, visibility, prompts, elicitation, background task UX, versioned
  public MCP surfaces
- LaBSE semantic layer:
  multilingual workflow matching, semantic retrieval, synonym handling, learned
  parameter reuse
- Router policy layer:
  deterministic execution safety, correction, clamping, ask/block/override
  decisions, safer tool sequencing
- Inspection and assertion layer:
  actual Blender truth, scene state, measurement, validation, and future
  correctness checks

Important boundary:

- semantic confidence is not proof of geometric correctness
- vision output is not the final truth source
- deterministic inspection and assertion should remain authoritative when
  correctness matters

## What The MCP Server Already Offers

### 1. Goal-first guided operation

The default public surface is intentionally small and shaped for LLMs.

Core guided entry tools:

- `router_set_goal`
- `router_get_status`
- `browse_workflows`
- `reference_images`
- `search_tools`
- `call_tool`
- `list_prompts`
- `get_prompt`

Guided utility actions available on the shaped surface:

- `scene_get_viewport`
- `scene_clean_scene`

Grouped/public aliases already exist for easier use:

- `check_scene` for `scene_context`
- `inspect_scene` for `scene_inspect`
- `configure_scene` for `scene_configure`

### 2. Stable tool API instead of raw Blender code synthesis

The system is designed so models call validated tools with structured
parameters instead of generating open-ended Blender Python scripts.

This matters because Blender APIs are context-sensitive and brittle when mode,
selection, visibility, or object state are wrong.

### 3. Deterministic inspection, measurement, and assertion

The repo already contains a truth-first validation path, including tools such
as:

- `scene_measure_distance`
- `scene_measure_dimensions`
- `scene_measure_gap`
- `scene_measure_alignment`
- `scene_measure_overlap`
- `scene_assert_contact`
- `scene_assert_dimensions`
- `scene_assert_containment`
- `scene_assert_symmetry`
- `scene_assert_proportion`

This means the system can ask a model to build or refine something, but it can
also check what is actually true in Blender afterward.

### 4. Macro tool layer for bounded task-sized work

The preferred LLM-facing modeling layer is not the raw atomic tool layer.
Important current macro tools include:

- `macro_cutout_recess`
- `macro_relative_layout`
- `macro_attach_part_to_surface`
- `macro_align_part_with_contact`
- `macro_place_symmetry_pair`
- `macro_place_supported_pair`
- `macro_cleanup_part_intersections`
- `macro_adjust_relative_proportion`
- `macro_adjust_segment_chain_arc`
- `macro_finish_form`

These tools already encode bounded geometric intent such as contact, alignment,
relative placement, symmetry, pair seating, and proportion correction.

### 5. Reference-guided visual comparison loop

The repo already supports staged reference-aware work through:

- `reference_images`
- `reference_compare_stage_checkpoint`
- `reference_iterate_stage_checkpoint`
- `scene_get_viewport`

Relevant structured outputs already include:

- `guided_reference_readiness`
- `truth_bundle`
- `truth_followup`
- `correction_candidates`
- `refinement_route`
- `refinement_handoff`
- `silhouette_analysis`
- `action_hints`

This means the project already has a hybrid loop:

- build something
- capture deterministic views
- compare current output against references
- combine vision feedback with truth/inspection findings
- recommend the next bounded correction

### 6. Multi-view and capture-profile thinking already exists

The current vision layer already works with bounded capture bundles and compact
vs rich capture profiles. The system therefore already assumes that single-view
inspection is often insufficient for trustworthy spatial judgment.

### 7. Pluggable vision runtime path

The repo already supports a pluggable vision layer with local and external
runtime paths. The exact model choice is not the main point of this brief.
The important point is that the product already has a place where visual
reasoning can be attached to the tool loop.

## Current Internal Hypothesis

The current repo direction assumes the following:

- general LLMs do not understand 3D space natively
- they often confuse left/right, depth, support, distance, and rotation
- they often overclaim spatial correctness from weak visual evidence
- they need explicit intermediate structure, bounded actions, and deterministic
  verification

External research should validate, refine, or challenge these assumptions with
evidence.

## Why This Research Is Needed

The repo already has strong infrastructure for:

- guided sessions
- tool discovery
- macro actions
- visual comparison
- truth-first verification

The open problem is higher-level spatial intelligence.

The current product still needs better answers to questions like:

- how should an LLM represent a 3D scene internally before acting
- how should a model combine text intent, multi-view images, object relations,
  and deterministic measurements
- which representations best bridge language and geometry:
  scene graph, relation graph, object slots, part graph, bounding boxes,
  contact graph, mesh-aware metrics, point clouds, or something else
- which research results are actually useful for a Blender tool-using agent,
  rather than only for benchmark demos

## Research Questions For External Models

Please research and answer the following.

### A. Research landscape

Find the strongest papers, benchmarks, and technical reports on:

- LLM or VLM spatial reasoning
- 3D scene understanding from language plus image input
- multi-view reasoning and view-consistent reasoning
- object-centric representations for geometry-aware planning
- embodied or agentic systems operating in 3D environments
- language interfaces to CAD, 3D modeling, robotics, or embodied simulators
- reasoning over relative position, orientation, scale, symmetry, support,
  contact, intersection, containment, and part-whole structure

### B. Institutions and labs

Identify which universities, institutes, labs, or industry research groups are
most active and credible in this area.

Focus on groups working on:

- multimodal spatial reasoning
- 3D-native model representations
- embodied reasoning
- language-conditioned scene understanding
- vision-language-action systems with geometric grounding

### C. Representation choices

Based on research evidence, what intermediate representation should a system
like `blender-ai-mcp` prefer when an LLM must reason about 3D structure?

Compare options such as:

- scene graphs
- object-relation graphs
- part hierarchies
- canonical coordinate frames
- camera-aware projections
- contact/support graphs
- silhouette and contour summaries
- bbox-only geometry summaries
- mesh-aware metrics
- multi-view latent summaries

For each option, explain:

- what it is good at
- what it misses
- whether it is realistic for a tool-using Blender agent

### D. Product-facing implications

For each strong research insight, explain how it could improve the repo's next
`LLM guide` and the MCP server/runtime around it.

Examples of possible improvement areas:

- better scene graph generation before execution
- stronger spatial prompt format
- better MCP-facing task decomposition for spatial requests
- better tool discovery, tool grouping, or public-surface shaping for 3D work
- better object identity tracking across stages and views
- explicit coordinate-frame and viewpoint handling
- multi-view consistency checks
- part-level planning for assembled objects
- better correction loops after compare/iterate stages
- better router policy for when to ask, auto-correct, measure, assert, or stop
- better division of labor between prompt logic, router logic, and truth tools
- choosing what must stay deterministic vs what can stay model-driven

### E. Evaluation and benchmarking

Recommend how this repo should evaluate spatial intelligence improvements.

The evaluation proposal should include:

- benchmark task types
- failure categories
- metrics
- what can be judged by vision
- what must be judged by deterministic tool truth
- how to test multi-view consistency
- how to test part placement, support, contact, overlap, symmetry, and
  proportion

## Non-Goals And Constraints

Please do not recommend any of the following as the primary solution:

- replacing deterministic Blender truth with pure VLM judgment
- returning to raw `bpy` code generation as the main interface
- exposing the full atomic tool inventory as the default public surface
- using semantic similarity as proof that a geometric result is correct

Recommendations should respect the existing product direction:

- bounded public surface
- goal-first routing
- macro tools for common geometric work
- inspection and assertions as the truth layer
- vision as assistant, not oracle

## Required Output Format From External Models

Use this output structure.

### 1. Executive summary

Provide a short research-based summary of what current evidence says about LLM
and VLM competence in 3D spatial reasoning.

### 2. Evidence table

For each important paper, report:

- title
- authors
- year
- venue or source
- link
- problem type
- modality:
  text-only, image-text, video-text, point-cloud, mesh, embodied, other
- representation used
- benchmark or evaluation setup
- main strengths
- main limitations
- direct relevance to `blender-ai-mcp`

### 3. Institution map

List the most relevant labs or institutions and explain why each matters.

### 4. Product mapping

Create a table:

- research insight
- why it matters
- which current repo subsystem it maps to:
  MCP surface, prompting, router, workflow layer, macro tools, vision layer,
  inspection, assertions
- estimated implementation difficulty:
  low, medium, high
- expected product impact:
  low, medium, high

### 5. Recommended changes to the next `LLM guide`

Provide concrete proposed changes, not only general advice.

Examples:

- new intermediate representation rules
- new prompt constraints
- new spatial reasoning phases
- new compare/verification requirements
- new structured outputs to request from models

Also provide a separate subsection:

- recommended MCP server changes
- recommended router-policy changes
- recommended truth/verification additions
- recommended tool-surface or macro-surface changes

### 6. Evaluation plan

Propose a practical evaluation plan for this repo, including what to measure in
unit tests, E2E runs, reference-guided loops, and benchmark-style experiments.

### 7. Open risks

List the top unresolved risks and the strongest research gaps that still affect
product design.

## Suggested Comparison Method Across 3 Models

Run the same brief against 3 strong external models with web access.

Compare them on:

- citation quality
- recency of evidence
- relevance to actual 3D tool-using agents
- whether they confuse image understanding with true 3D understanding
- whether they distinguish benchmark performance from product usefulness
- whether they respect deterministic-truth constraints
- whether their recommendations are implementable in this repo

After that, produce one merged synthesis:

- shared conclusions across all 3 models
- unique high-value ideas found by only one model
- contradictions between models
- proposed shortlist of changes for `LLM_GUIDE_V3`

## Ready-To-Use Prompt

You are helping evaluate how `blender-ai-mcp` should evolve its spatial
reasoning and `LLM guide` strategy.

Treat the content of this document as the authoritative project brief.

Your task is to perform a serious research scan of papers, labs, benchmarks,
and technical directions related to LLM/VLM understanding of 3D space,
multi-view reasoning, geometry-aware planning, and structured spatial
representation.

Do not give generic AI commentary. Ground your answer in specific papers,
specific institutions, and concrete product implications.

You must distinguish between:

- image-level description
- true multi-view or 3D reasoning
- semantic matching
- deterministic geometric verification

You must respect this product constraint:

- in `blender-ai-mcp`, vision assists interpretation, but deterministic
  inspection, measurement, and assertion remain the truth layer

Your recommendations must be actionable for both:

- the next `LLM guide`
- the MCP server and router logic that execute the guide in practice

Return the answer in the exact structure requested in the section
"Required Output Format From External Models".
