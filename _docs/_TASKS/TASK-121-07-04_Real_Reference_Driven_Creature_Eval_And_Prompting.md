# TASK-121-07-04: Real Reference-Driven Creature Eval and Prompting

**Parent:** [TASK-121-07](./TASK-121-07_Vision_Guided_Iterative_Correction_Loop.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium

Used real squirrel/reference-oriented scenarios to validate the iterative
correction loop shape and published prompt guidance for practical
reference-driven creature building.

Delivered:

- opt-in real MLX creature/reference smoke coverage:
  - `tests/e2e/vision/test_reference_guided_creature_comparison.py`
- published prompt guidance:
  - `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- docs now explain the required env vars for running the real creature/reference
  comparison locally with front + side reference images
