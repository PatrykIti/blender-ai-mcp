# TASK-121-04-02-03: Real Viewport Smoke Scenario and Scoring Heuristic Tuning

**Parent:** [TASK-121-04-02](./TASK-121-04-02_Evaluation_Harness_Goldens_And_Safety_Review.md)  
**Status:** 🚧 In Progress  
**Priority:** 🟡 Medium

**Progress Update:** The repo now includes both a real viewport smoke scenario (`default_cube_to_picnic_table`) and a set of real viewport progression scenarios (`squirrel_head_to_face`, `squirrel_face_to_body`, `squirrel_head_to_body`) sourced from manual Blender captures, plus two additional real view families for the same squirrel progressions: direct top `USER_PERSPECTIVE` captures and fixed camera-perspective captures. On those 6 new variants, `Qwen3-VL-2B-Instruct-4bit` stays `strong` and currently scores `1.0` on all 6, while `Qwen3-VL-4B-Instruct-4bit` stays cleaner but currently lands at `0.875` on 2/6 because the heuristic does not always reward its shorter phrasing.

---

## Objective

Tune the evaluation/scoring layer so real viewport smoke scenarios are judged
more accurately and do not overreward noisy model behavior.

---

## Business Problem

On real viewport smoke scenarios, the model can produce a genuinely useful
summary while the current heuristic classifier still marks the direction as
`unknown`. At the same time, smaller models can score well even when they add
unnecessary issues/checks that are not useful for easy scene-replacement cases.

That means the current score can hide two different quality problems:

- undercounting valid concise descriptions
- overrewarding noisy or weakly grounded extra analysis

---

## Implementation Direction

- extend direction heuristics for real viewport smoke phrasing such as:
  - replacement of a simple/default object by a more goal-relevant object
  - large scene/object change without explicit words like `improved`
- add scenario-specific scoring knobs so easy smoke cases can penalize:
  - gratuitous issue generation
  - gratuitous follow-up checks
- keep this tuned specifically for real viewport smoke scenarios rather than
  polluting the macro/reference scoring path with one-size-fits-all heuristics

---

## Repository Touchpoints

- `server/adapters/mcp/vision/evaluation.py`
- `tests/unit/adapters/mcp/test_vision_evaluation.py`
- `tests/fixtures/vision_eval/default_cube_to_picnic_table/`
- `_docs/_VISION/README.md`
- `_docs/_TASKS/`

---

## Acceptance Criteria

- the real viewport smoke scenario scores better reflect useful concise output
- easy smoke scenarios no longer silently reward noisy issue/check generation
- the repo records the distinction between smoke-case quality and macro-case quality
