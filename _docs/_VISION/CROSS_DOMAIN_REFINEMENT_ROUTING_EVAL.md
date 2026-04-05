# Cross-Domain Refinement Routing Eval

This document is the regression guide for deterministic cross-domain
refinement-family routing.

Its purpose is to keep one explicit answer to:

- which domains should stay on `macro` / `modeling_mesh`
- which domains may justify `sculpt_region`
- how to review `refinement_route` and `refinement_handoff`
- what later regressions should be treated as policy failures

## Review Order

For refinement-routing review, inspect outputs in this order:

1. `loop_disposition`
2. `refinement_route`
3. `refinement_handoff`
4. `correction_candidates`
5. `truth_followup`
6. `correction_focus`
7. `vision_contract_profile` when the compare path was external

Why:

- `loop_disposition` still decides whether free-form building should continue
- `refinement_route` decides which bounded tool family should own the next step
- `refinement_handoff` tells the operator or client what deterministic family
  path is actually being recommended
- the remaining fields explain the evidence behind that decision

## Scenario Matrix

### 1. Hard-Surface / Electronics

Examples:

- phone housing
- panel fit
- button alignment
- PCB enclosure

Expected routing:

- `refinement_route.selected_family == "macro"` or `"modeling_mesh"`
- `refinement_handoff.selected_family != "sculpt_region"`

Reason:

- these problems are usually driven by:
  - placement
  - clear dimensions
  - cutouts
  - hard edges
  - explicit bbox/contact relationships

### 2. Building / Architecture

Examples:

- tower taper
- roof silhouette
- wall / window proportion
- facade alignment

Expected routing:

- `refinement_route.selected_family == "macro"` or `"modeling_mesh"`
- sculpt should not be the default family

Reason:

- architectural corrections are usually structural or planar, not local
  organic-form refinement

### 3. Garment / Soft Accessory

Examples:

- hood silhouette
- sleeve mass
- soft fold shaping
- cape or cloth-like accessory smoothing

Expected routing:

- `refinement_route.selected_family == "sculpt_region"` can be valid
- `refinement_handoff.recommended_tools` should stay in the deterministic
  sculpt-region subset

Reason:

- these are local soft-form and silhouette refinement cases, not pairwise
  assembly corrections

### 4. Organ / Anatomy

Examples:

- heart surface
- lung lobe shaping
- soft anatomical bulge
- tumor or organic mass refinement

Expected routing:

- `refinement_route.selected_family == "sculpt_region"` can be valid
- hard-surface modeling fallback should not dominate by default

Reason:

- anatomy refinement is typically local-form and smooth-surface oriented

### 5. Creature / Character Local Form

Examples:

- cheek silhouette
- muzzle shape
- soft muscle or fat profile
- non-low-poly organic character massing

Expected routing:

- `refinement_route.selected_family == "sculpt_region"` can be valid
- but only when strong assembly/macro signals are absent

### 6. Low-Poly Creature / Assembled Model

Examples:

- low-poly squirrel
- stylized animal blockout
- character assembled from separate objects

Expected routing:

- `refinement_route.selected_family == "macro"` or `"modeling_mesh"`
- sculpt should remain a non-default recommendation

Reason:

- low-poly assembly and silhouette work still benefits more from:
  - macros
  - deterministic transforms
  - bounded mesh/modeling edits
  than from free-form surface refinement

## Policy Failures To Watch

Treat these as routing regressions:

- hard-surface or low-poly assembly cases defaulting to `sculpt_region`
- garment/anatomy/organic local-form cases never reaching `sculpt_region`
- `refinement_handoff` recommending tools outside the bounded sculpt-region set
- `refinement_route` disagreeing with obvious truth/macro evidence without a
  deterministic reason
- `refinement_handoff` reintroducing brush-style or event-style sculpt paths
- external compare runs silently shifting from `google_family_compare` back to
  `generic_full` during the same reproduced scenario

## Prompting Guidance

For cross-domain operator prompts:

- check `refinement_route` before choosing the next tool family
- if `refinement_route.selected_family == "sculpt_region"`, review
  `refinement_handoff.recommended_tools` before any sculpt step
- if the selected family is `macro` or `modeling_mesh`, do not jump to sculpt
  just because a shape mismatch exists
- when the compare path is external, check `vision_contract_profile` before
  blaming routing results on transport/provider failures alone
- keep viewport/camera review and truth checks as the authority over whether a
  refinement actually fixed the problem
