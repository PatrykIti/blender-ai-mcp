# 170. Reference-guided creature eval and prompting

Date: 2026-03-30

## Summary

Finished the first repo-tracked creature/reference guidance layer on top of the
new checkpoint-compare surfaces.

## What Changed

- added opt-in real MLX coverage for creature/reference comparison:
  - `tests/e2e/vision/test_reference_guided_creature_comparison.py`
- added a ready-to-paste prompt guide:
  - `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- documented the env vars needed to run the real creature/reference comparison
  locally with front + side squirrel reference images
- marked `TASK-121-07-04` done and closed the `TASK-121-07` track

## Why

The repo already had bounded checkpoint compare surfaces, but practical
reference-driven creature work still needed two missing pieces:

- a concrete prompt/playbook for staged low-poly creature building
- one opt-in real-model validation path that uses real squirrel checkpoint
  images plus user-supplied front/side references
