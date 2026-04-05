# TASK-139-01: Runtime Contract Profile Model and Resolution

**Parent:** [TASK-139](./TASK-139_Model_Family_Specific_Vision_Contract_Profiles_For_External_Runtimes.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Introduce one typed contract-profile concept for external vision runtimes and
resolve that profile deterministically from explicit configuration plus
model-family matching rules.

## Business Problem

Current runtime selection already distinguishes:

- local vs external backend families
- OpenRouter vs Google AI Studio transport/provider identity

But it still does not distinguish the question that now matters for staged
compare reliability:

- which prompt/schema/parser contract should this model family receive?

That missing layer is why OpenRouter Google-family models still fall into the
generic OpenAI-compatible contract path.

## Repository Touchpoints

- `server/adapters/mcp/vision/config.py`
- `server/adapters/mcp/vision/runtime.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `_docs/_VISION/README.md`

## Acceptance Criteria

- the runtime config has an explicit contract-profile concept for external
  vision
- the selected contract profile is resolved deterministically
- the selected contract profile is available to downstream prompting/backend/
  parsing layers without ad hoc model-name re-parsing at every call site

## Docs To Update

- `_docs/_VISION/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`

## Changelog Impact

- include in the parent umbrella changelog entry when shipped

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-139-01-01](./TASK-139-01-01_Contract_Profile_Vocabulary_And_Typed_Config_Surface.md) | Define the explicit profile vocabulary and typed config surface |
| 2 | [TASK-139-01-02](./TASK-139-01-02_Model_Family_Detection_And_Override_Precedence.md) | Define deterministic profile selection rules from overrides and model-family matching |
