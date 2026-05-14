# TASK-140-06: OpenRouter Model-Capability-Aware Vision Runtime

**Parent:** [TASK-140](./TASK-140_Expand_External_Vision_Contract_Profiles_Across_Qwen_Anthropic_OpenAI_And_NVIDIA.md)
**Status:** 🚧 In Progress
**Priority:** 🔴 High

## Objective

Make the OpenRouter-backed external vision runtime model-capability aware
instead of relying on one static `VISION_MAX_TOKENS` cap and hand-written
family heuristics.

Recent operator runs with `openai/gpt-5.4-nano` showed that the model/provider
can advertise large context/output limits, while the repo still sent a bounded
`max_tokens=600` request and only discovered provider/schema constraints after
runtime failure. The next step is therefore API-first model capability
resolution:

- query OpenRouter model metadata when using `VISION_EXTERNAL_PROVIDER=openrouter`
- derive model/provider capabilities from the response
- use those capabilities to select output budget and parameter/profile posture
- fall back to a local registry only when the OpenRouter model catalog is
  unavailable, incomplete, or intentionally bypassed

## Repository Touchpoints

- `server/adapters/mcp/vision/runtime.py`
- `server/adapters/mcp/vision/config.py`
- `server/adapters/mcp/vision/backends.py`
- `server/adapters/mcp/vision/openrouter_models.py`
- `server/adapters/mcp/vision/prompting.py`
- `server/adapters/mcp/vision/runner.py`
- `server/infrastructure/config.py`
- `tests/unit/adapters/mcp/test_openrouter_model_capabilities.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_runner.py`
- `tests/e2e/vision/test_openrouter_qwen_json_mode.py`
- `scripts/run_streamable_openrouter.sh`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TASKS/README.md`

## Acceptance Criteria

- OpenRouter model metadata is the primary source for active model capabilities
  when available
- the runtime captures and exposes the relevant capability fields for the
  active model:
  - `context_length`
  - `top_provider.max_completion_tokens`
  - input/output modalities
  - supported parameters such as `response_format`, `structured_outputs`,
    `tools`, and reasoning-related parameters
- request assembly uses those capabilities to decide:
  - whether `json_schema`, `json_object`, or a narrower compare profile is safe
  - whether strict structured output should be attempted
  - whether response-healing should be sent
  - the final `max_tokens` used for the request
- static fallback data exists for selected known models, but it is secondary to
  OpenRouter API data
- logs and public diagnostics explain:
  - model id
  - source of capability data (`openrouter_api`, `fallback_registry`,
    `env_override`, or `unknown`)
  - model max input/output where known
  - final requested output token cap
  - selected `vision_contract_profile`
- explicit env overrides still win when an operator intentionally forces a
  profile or cap

## Implementation Notes

- this slice already has landed progress under:
  - `TASK-140-06-01` for the bounded `/models` metadata client
  - `TASK-140-06-03` for the first fallback capability registry entries
- the remaining work stays focused on:
  - capability-driven request policy in `vision/runtime.py`,
    `vision/backends.py`, and `vision/prompting.py`
  - diagnostics and closeout in the existing runtime/docs seams
- keep OpenRouter capability handling API-first when available, but preserve
  the current typed fallback/override precedence instead of rebuilding the
  capability contract ad hoc at each call site

## Runtime / Security Contract Notes

- do not make the runtime dependent on live OpenRouter metadata availability;
  fallback registry and explicit overrides must remain bounded and typed
- keep capability diagnostics free of secrets while still explaining the source
  of the chosen budget/profile posture
- if request-policy tightening narrows structured-output behavior, document the
  operator-visible change in both runtime diagnostics and docs

## Tests To Add/Update

- Unit:
  - `tests/unit/adapters/mcp/test_vision_runtime_config.py`
  - `tests/unit/adapters/mcp/test_vision_external_backend.py`
  - `tests/unit/adapters/mcp/test_vision_prompting.py`
  - `tests/unit/adapters/mcp/test_vision_runner.py`
- E2E / optional live:
  - extend opt-in OpenRouter coverage under `tests/e2e/vision/`
  - keep live tests gated behind explicit env flags and API keys

## Changelog Impact

- add a dedicated `_docs/_CHANGELOG/*` entry when this capability-aware
  OpenRouter runtime work ships

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-140-06-01](./TASK-140-06-01_OpenRouter_Model_Metadata_Client_And_Capability_Contract.md) | Add one bounded OpenRouter model metadata client and a typed capability contract |
| 2 | [TASK-140-06-02](./TASK-140-06-02_Capability_Driven_Vision_Request_Policy.md) | Use resolved capabilities to choose output budget and safe request parameters |
| 3 | [TASK-140-06-03](./TASK-140-06-03_Static_Fallback_Model_Capability_Registry_And_Overrides.md) | Add local fallback capability data and explicit operator override precedence |
| 4 | [TASK-140-06-04](./TASK-140-06-04_Diagnostics_Harness_Docs_And_Closeout_For_Model_Capabilities.md) | Expose diagnostics, add harness/docs coverage, and close out the implementation slice |

## Progress Update

- `TASK-140-06-03` is complete for the first known fallback model,
  `openai/gpt-5.4-nano`
- `TASK-140-06-01` is complete for the first API-first OpenRouter catalog
  resolution slice:
  - the runtime now has one bounded `/models` lookup path that normalizes
    catalog fields into `VisionModelCapabilities`
  - lookup runs lazily at first OpenRouter vision request and keeps fallback
    registry data when the catalog is unavailable
- Richer request-policy use of the capability object, env override taxonomy,
  harness diagnostics, and final closeout remain open under the other
  `TASK-140-06` leaves

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_vision_external_backend.py tests/unit/adapters/mcp/test_vision_prompting.py tests/unit/adapters/mcp/test_vision_runner.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_openrouter_model_capabilities.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- opt-in OpenRouter live coverage under `tests/e2e/vision/` when explicit env flags and API keys are available

## Status / Board Update

- remains nested under `TASK-140`
- stays `🚧 In Progress` while `TASK-140-06-02` and `TASK-140-06-04` remain open after the already-landed `06-01` and `06-03` slices
