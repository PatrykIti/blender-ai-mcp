# TASK-122-03-07-01: Refinement Taxonomy and Domain Boundaries

**Parent:** [TASK-122-03-07](./TASK-122-03-07_Deterministic_Cross_Domain_Refinement_Routing_And_Sculpt_Exposure.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

## Objective

Define one deterministic taxonomy that maps correction needs to refinement
families across major Blender domains.

## Business Problem

Without an explicit taxonomy, the system will keep making one of two mistakes:

- push everything toward mesh/modeling because those tools are already visible
- or expose sculpt too broadly and let it erode deterministic hard-surface and
  low-poly workflows

The product needs one shared language for:

- what kind of correction this is
- what tool family should own it
- which families should stay hidden

## Required Taxonomy Outcome

At minimum the taxonomy should distinguish:

- assembly / contact / placement corrections
- proportion / scale corrections
- local hard-surface geometry corrections
- local organic / soft-form silhouette corrections
- symmetric paired refinements
- garment / cloth-like drape or soft-boundary refinements
- anatomy / organ / creature surface refinements

It should also define what is **not** a sculpt problem:

- hard-surface boolean/cutout layout
- explicit bbox/contact placement
- low-poly assembly gaps
- pairwise overlap cleanup

## Technical Direction

Produce one explicit mapping layer that can be referenced by:

- hybrid correction candidates
- guided-surface visibility policy
- prompt guidance
- future router policy

The taxonomy should be driven by observable signals already available in the
repo, such as:

- `truth_followup` item kinds
- ranked `correction_candidates`
- vision `shape_mismatches`
- vision `proportion_mismatches`
- object names / target scope composition
- whether current candidate payload is pairwise assembly-oriented or local-form
  oriented

## Repository Touchpoints

- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/vision/prompting.py`
- `server/adapters/mcp/vision/parsing.py`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`

## Acceptance Criteria

- one explicit taxonomy exists for refinement-family routing
- the taxonomy covers both hard-surface and soft/organic domains
- the taxonomy says which classes should never default to sculpt

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`

## Changelog Impact

- include in the parent follow-on changelog entry when shipped
