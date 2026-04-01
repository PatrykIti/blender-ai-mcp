# 185. Macro attach part to surface

Date: 2026-04-01

## Summary

Completed the first creature-correction macro leaf by adding
`macro_attach_part_to_surface` on top of the existing bounded relative-layout
stack.

## What Changed

- added `macro_attach_part_to_surface` to the scene MCP surface
- implemented it as a bounded server-side macro that reuses bbox/contact
  placement logic instead of introducing a new addon/RPC geometry path
- exposed structured delivery, provider inventory, compatibility policy, and
  guided build-surface visibility for the new macro
- added unit coverage for:
  - macro handler behavior
  - MCP wrapper behavior
  - structured delivery
  - provider inventory / guided surface visibility

## Why

The `TASK-122` macro wave needs a narrow surface-attachment tool before moving
on to more advanced creature-correction macros. This first slice gives the repo
one explicit "seat this part onto that body surface" action instead of forcing
the model to compose the more general relative-layout macro each time.
