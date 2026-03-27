# TASK-121-04-01-02: Local Prompting and Parse-Repair Policy

**Parent:** [TASK-121-04-01](./TASK-121-04-01_Small_Vision_Runtime_Selection_And_Execution_Policy.md)  
**Status:** 🚧 In Progress  
**Priority:** 🔴 High

**Progress Update:** Shared prompt/parsing helpers now exist and local backends use a shorter, more task-oriented payload. Fenced JSON and input-echo outputs can now be normalized into the bounded contract shape. The parser also repairs summary-alias outputs like `{"comparison": "..."}` and explicitly flags unsupported label-map outputs. Preliminary MLX smoke reruns now show usable structured output on both `Qwen3-VL-4B-Instruct-4bit` and `Qwen3-VL-2B-Instruct-4bit`, but the smaller model still looks more prone to overconfident/hallucinatory issue generation.

---

## Objective

Define how local models should be prompted and how their imperfect outputs
should be repaired or rejected.

---

## Implementation Direction

- maintain a backend-aware prompt policy:
  - stricter prompt for `mlx_local`
  - stricter prompt for `transformers_local`
  - keep external prompt simpler where API-side structured output is stronger
- maintain one parse policy that can handle:
  - direct JSON
  - fenced JSON
  - JSON embedded in prose
  - input-echo outputs that should be converted into a bounded warning payload
  - summary-alias outputs that should be mapped into `goal_summary`
  - unsupported JSON shapes that should be marked as backend-output drift
- explicitly measure where parse-repair helps versus where it only masks weak
  model behavior

---

## Repository Touchpoints

- `server/adapters/mcp/vision/prompting.py`
- `server/adapters/mcp/vision/parsing.py`
- `server/adapters/mcp/vision/backends.py`
- `tests/unit/adapters/mcp/`
- `_docs/_VISION/`

---

## Acceptance Criteria

- local backend prompt policy is explicit and tested
- parse-repair behavior is explicit and tested
- the team can distinguish "runtime works" from "model output is actually useful"
