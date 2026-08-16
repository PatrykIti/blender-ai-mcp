# 199. Refinement taxonomy and family selector

Date: 2026-04-03

## Summary

Started the cross-domain refinement-routing follow-on by adding a deterministic
taxonomy and refinement-family selector to hybrid loop responses.

## What Changed

- hybrid compare/iterate responses now expose `refinement_route`
- `refinement_route` currently classifies:
  - domain: `assembly`, `hard_surface`, `garment`, `anatomy`,
    `organic_form`, `generic_form`
  - family: `macro`, `modeling_mesh`, `sculpt_region`, `inspect_only`
- selector behavior is currently bounded by deterministic rules:
  - assembly or macro-heavy truth cases stay on `macro`
  - non-low-poly organic/anatomy/garment local-form cases can route to
    `sculpt_region`
  - low-poly and hard-surface/generic cases stay on `modeling_mesh`
- unit coverage now validates:
  - assembly -> `macro`
  - organic anatomy -> `sculpt_region`
  - low-poly creature -> `modeling_mesh`

## Why

The hybrid loop needed a deterministic answer to “which refinement family
should own the next step?” before sculpt can ever be exposed safely on guided
surfaces.
