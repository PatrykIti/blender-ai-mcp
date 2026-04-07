# TASK-146-02: Docker Dependency Group And Runtime Packaging Alignment

**Parent:** [TASK-146](./TASK-146_Guided_Runtime_Guardrails_Vision_Profile_And_Prompting_Hardening.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Depends On:** [TASK-121](./TASK-121_Goal_Aware_Vision_Assist_And_Reference_Context.md), [TASK-128](./TASK-128_Reference_Guided_Creature_Build_Surface_And_Perception_Reliability.md)

## Objective

Align the Docker runtime build with the actual dependency expectations of the
guided vision/perception path, so deployed images no longer quietly omit
packages that the active product flow expects.

## Repository Touchpoints

- `Dockerfile`
- `pyproject.toml`
- runtime/dependency docs
- build/test tooling around Docker images

## Acceptance Criteria

- Docker install strategy is deliberate and documented:
  - either the right Poetry groups are installed
  - or the relevant packages are moved to the right dependency scope
- deployed guided runtimes no longer miss packages that are part of the
  intended compare/perception path
- validation covers the chosen packaging strategy

## Docs To Update

- `README.md`
- `_docs/_VISION/README.md`
- `_docs/_TESTS/README.md`

## Tests To Add/Update

- unit/script coverage for Docker/runtime packaging assumptions
- any focused runtime smoke coverage justified by the chosen install strategy

## Changelog Impact

- include in the parent TASK-146 changelog entry when shipped

## Status / Board Update

- nested under TASK-146 as the runtime packaging repair slice
