# TASK-121-04: Lightweight Vision Runtime and Evaluation

**Parent:** [TASK-121](./TASK-121_Goal_Aware_Vision_Assist_And_Reference_Context.md)  
**Status:** 🚧 In Progress  
**Priority:** 🔴 High

**Progress Update:** The runtime layer is now materially underway: `transformers_local`, `mlx_local`, and `openai_compatible_external` all exist behind the same bounded contract path, `mlx_local` has passed a first real smoke test, and the next work is shifting from backend plumbing toward real backend comparison, debug harnessing, and stronger prompt/parse policy for local models.

---

## Objective

Choose the lightweight vision runtime/model path and add enough evaluation and
governance to keep the feature bounded and trustworthy.

The runtime choice must stay pluggable so the repo can compare local open
models against stronger external endpoints without redesigning the contract
layer.

---

## Repository Touchpoints

- `server/adapters/mcp/sampling/`
- `server/infrastructure/config.py`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
- `_docs/_TESTS/README.md`
- `tests/unit/adapters/mcp/`
- `tests/e2e/`

---

## Leaf Breakdown

| Leaf | Purpose |
|------|---------|
| [TASK-121-04-01](./TASK-121-04-01_Small_Vision_Runtime_Selection_And_Execution_Policy.md) | Select the lightweight runtime/model strategy and define execution constraints |
| [TASK-121-04-02](./TASK-121-04-02_Evaluation_Harness_Goldens_And_Safety_Review.md) | Add evaluation datasets, goldens, and governance checks for the vision layer |

---

## Acceptance Criteria

- the vision layer has an explicit runtime/model strategy
- lightweight vision behavior is evaluated and governed before broad rollout
- backend pluggability exists from the start instead of hard-coding one model vendor/runtime

## Detailed Next Sequence

1. Add a debug harness/script for real backend comparison over the current
   capture/reference pipeline.
2. Harden local prompting so local models are explicitly optimized for one
   bounded JSON contract instead of open-ended description behavior.
3. Add parse-repair / fallback handling for local outputs that are fenced,
   partial, empty, or structurally close to the target JSON shape.
4. Build a repeatable backend matrix around:
   - `mlx_local`
   - `transformers_local`
   - `openai_compatible_external`
5. Capture qualitative and structured differences before choosing the first
   production-favored local path.
