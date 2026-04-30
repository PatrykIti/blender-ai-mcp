# AGENTS.md

## Project Purpose

`blender-ai-mcp` is a split Blender control system for LLMs:

- `server/` exposes FastMCP tools and translates them to RPC calls.
- `blender_addon/` runs inside Blender and executes the actual `bpy` operations.
- `server/router/` is a supervisor layer that corrects, expands, and routes LLM tool calls through metadata and workflows.

The project exists to avoid raw-code Blender automation. The intended product surface is a stable, deterministic tool API with strong inspection, recovery, and workflow support.

## Repo Map

- `server/domain/`: abstract tool interfaces and core models. Keep framework-free.
- `server/application/tool_handlers/`: RPC-backed application handlers that implement domain interfaces.
- `server/adapters/mcp/areas/`: FastMCP tool definitions grouped by area.
- `server/adapters/rpc/`: socket RPC client used by handlers.
- `server/infrastructure/`: DI and config.
- `server/router/`: router, metadata, classifiers, workflow engine, vector store, and MCP integration helpers.
- `blender_addon/application/handlers/`: Blender-side handlers using `bpy`.
- `blender_addon/infrastructure/rpc_server.py`: threaded RPC server that schedules work safely on Blender's main thread.
- `tests/unit/`: fast tests with mocked Blender/RPC.
- `tests/e2e/`: Blender-backed end-to-end tests.
- `_docs/`: canonical design/task/history docs. Read the area-specific docs before structural changes.

## Architecture Rules

- Preserve Clean Architecture direction: `adapters -> application -> domain`.
- Do not import FastMCP, socket code, or Blender APIs into `server/domain/`.
- Keep Blender-specific logic inside `blender_addon/`.
- MCP adapters should stay thin. Business logic belongs in handlers or router components, not inside `@mcp.tool` wrappers.
- Dependency wiring belongs in `server/infrastructure/di.py`.
- Router additions must remain metadata-driven where possible.

## Runtime Boundaries

Read `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md` before changing FastMCP integration, LaBSE usage, router policy, or verification flows.

The intended responsibility split is:

- **FastMCP platform layer**: discovery, visibility, prompts, elicitation, background tasks, versioned/public MCP surfaces.
- **LaBSE semantic layer**: workflow matching, multilingual semantic retrieval, synonym handling, learned parameter reuse.
- **Router policy layer**: deterministic execution safety, mode/selection fixes, clamping, correction policy, ask/block/override decisions.
- **Inspection/assertion layer**: Blender truth and verification via scene/mesh/object inspection and future assertion tools.

Do not let these roles blur together:

- Do not use LaBSE as the authority for scene truth or execution safety.
- Do not use the router as the primary discovery/catalog-shaping mechanism when FastMCP platform features should handle that.
- Do not treat semantic confidence as proof that a Blender result is correct; rely on inspection/assertion tools for that.
- Prefer structured state reporting and verification over prose when correctness matters.

## Environment Notes

- Python `3.11+` is the practical baseline for full repo functionality.
- Router semantic features rely on `sentence-transformers`, `lancedb`, and `pyarrow`.
- LaBSE is heavy; shared DI instances and lazy initialization are intentional. Do not accidentally reintroduce per-test or per-call model loading.
- Blender `5.0` is the tested target. The addon declares Blender `4.0+`, but 4.x is best effort.

## Commands

- Install deps: `poetry install --no-interaction`
- Run server locally: `poetry run python server/main.py`
- Build addon zip: `python scripts/build_addon.py`
- Pre-commit install: `poetry run pre-commit install --hook-type pre-commit --hook-type pre-push`
- Full repo checks: `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files` or `poetry run pre-commit run --all-files --show-diff-on-failure`
- Type checks: `poetry run mypy`
- Unit tests: `PYTHONPATH=. poetry run pytest tests/unit/ -v`
- Unit test collection count: `poetry run pytest tests/unit --collect-only`
- E2E tests: `python3 scripts/run_e2e_tests.py`
- E2E collection count: `poetry run pytest tests/e2e --collect-only`

## Coding Standards

- Fully type Python code.
- Code, code comments, identifiers, commit messages, and technical contracts
  should be in English. User-facing planning notes may use Polish only when the
  task or discussion explicitly calls for it.
- Tool docstrings are part of the product. Keep them explicit, accurate, and aligned with actual behavior.
- Prefer meaningful error strings over uncaught exceptions. The server should not crash on normal tool misuse.
- Follow naming patterns already used in the repo: `scene_*`, `modeling_*`, `mesh_*`, `router_*`, etc.
- Repo formatting/linting/type-checking is enforced through `pre-commit`. Keep `ruff`, `mypy`, JSON/TOML/YAML validation, GitHub workflow validation, and router metadata schema validation green.
- Do not weaken established domain/runtime contracts just to satisfy the type checker. If a contract is intentionally optional or dynamic, preserve it and narrow at call sites or use explicit helper functions/casts where needed.
- Do not add production fallbacks only to satisfy tests. Update the real
  contract, test fixture, wrapper, or mock so it matches shipped behavior.
- Keep schemas, enums, defaults, result envelopes, and normalization helpers in
  the owning contract/service module. Adapters may translate or re-export, but
  should not duplicate contract logic.
- Validate external, MCP, router, and RPC payloads schema-first. Reject unknown
  or unsupported fields where a contract is meant to be strict, and preserve
  explicit compatibility adapters when legacy payloads must still work.
- For RPC-backed handlers, prefer explicit result-unwrapping/narrowing helpers over changing `RpcResponse` semantics.
- Router metadata JSON now uses one deliberate type vocabulary for schema validation: `string`, `int`, `float`, `bool`, `enum`, `array`, `vector3`, `object`, `scalar`.

## Tool Surface Conventions

- Prefer mega tools for the MCP-facing surface when an area already uses them.
- Keep internal single-action handlers when the router or workflows still need them, even if the public MCP wrapper is consolidated behind a mega tool.
- Current important mega tools include `scene_context`, `scene_create`, `scene_inspect`, `mesh_select`, `mesh_select_targeted`, and `mesh_inspect`.
- Read `_docs/AVAILABLE_TOOLS_SUMMARY.md` and `_docs/_MCP_SERVER/README.md` before changing tool exposure.
- For any new or materially changed public MCP tool, transport surface, guided
  visibility rule, external-provider path, or mutating RPC action, document the
  runtime/security contract in the task or implementation notes:
  - visibility level: public, hidden/internal, guided-phase-only, or router-only
  - read-only vs mutating behavior and expected Blender mode/selection impact
  - session/auth assumptions for stdio, Streamable HTTP, and local Blender RPC
  - parameter validation, reject-unknown behavior, and compatibility shims
  - side-effect boundaries, timeout/resource limits, and recovery behavior
  - secret/provider-key handling, redaction, and log/debug payload limits
- Do not create parallel discovery, visibility, or handoff flows when the
  existing FastMCP platform, router metadata, guided mode, or reference-stage
  contracts can be extended.

## Change Playbook: Adding Or Updating A Tool

When adding a new tool or materially changing an existing one, update all relevant layers:

1. Domain interface in `server/domain/tools/`.
2. Application handler in `server/application/tool_handlers/`.
3. Blender handler in `blender_addon/application/handlers/`.
4. Addon registration in `blender_addon/__init__.py`.
5. MCP adapter in `server/adapters/mcp/areas/`.
6. DI wiring in `server/infrastructure/di.py` if a new handler/provider is needed.
7. Dispatcher mapping in `server/adapters/mcp/dispatcher.py` if the router or internal execution path depends on it.
8. Router metadata in `server/router/infrastructure/tools_metadata/**/<tool>.json` if the tool should be router-aware.
9. Unit tests in `tests/unit/`.
10. E2E tests in `tests/e2e/` when Blender behavior changes.
11. Documentation in `README.md`, `_docs/_CHANGELOG/`, and the relevant `_docs/` files. Update root `CHANGELOG.md` only when release-note / semantic-release content itself changes.

Use `_docs/_ROUTER/TOOLS/README.md` as the checklist for router-facing tools.

## Change Playbook: Router Or Workflow Work

- Read `_docs/_ROUTER/README.md` and the relevant implementation/workflow docs before changing router behavior.
- Read `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md` before changing anything that touches FastMCP platform design, LaBSE responsibilities, router correction scope, or verification logic.
- Router logic is not just intent matching. It includes correction, override, workflow expansion, parameter resolution, adaptation, and firewall behavior.
- Preserve edit-mode selection state where possible. This is a documented project goal and already has explicit fixes/tasks around it.
- Keep metadata, workflow YAML, router engines, and tests in sync.
- Prefer deterministic rules plus metadata over prompt-only heuristics.
- For workflow execution semantics, use `_docs/_ROUTER/WORKFLOWS/workflow-execution-pipeline.md`.

## Change Playbook: Blender Addon Or RPC Work

- Keep networking and threading concerns in infrastructure, not in business handlers.
- Blender work must remain main-thread safe. The addon architecture relies on timer/main-loop scheduling for that.
- If you change RPC method names or payloads, update both sides together:
  - server application handler call
  - addon handler implementation
  - addon RPC registration
  - tests
  - docs

## Testing Expectations

- Before considering work done, run the relevant `pre-commit` hooks or the full `pre-commit run --all-files` when the change is broad.
- For meaningful repo-wide or cross-cutting changes, prefer the full command below so failures show the exact diff/context:
  - `poetry run pre-commit run --all-files --show-diff-on-failure`
- Choose validation by dependency shape, not by folder name alone. Pure
  contract/policy helpers usually need targeted unit tests; Router metadata
  changes need metadata/schema tests; Blender scene state, real geometry,
  transport behavior, guided visibility, and client-facing runtime behavior need
  E2E or integration coverage.
- When a task changes a public/tool/runtime contract, run the exact focused
  tests for that contract and record the command in the task closeout. Broad
  suites are useful only after the owner lane is covered.
- For server-side logic, default to unit tests first.
- For Blender behavior, add or update E2E coverage if the change affects real geometry, mode handling, selection handling, viewport output, router correction, or workflow execution.
- Router tests should avoid repeated heavy model initialization. Follow the shared/session-scoped patterns already used in tests.
- Before creating a manual commit, run the relevant validation or the configured
  pre-commit path unless the commit hook itself runs it. Always stage only the
  owned files and re-check the staged set before committing.

## Task Workflow

- Before starting implementation for any task, read:
  - the task file and its parent/subtasks/leaves under `_docs/_TASKS/`
  - related source modules and current owner functions/classes
  - related unit, integration, and E2E tests
  - relevant docs/contracts such as `_docs/_TESTS/README.md`,
    `_docs/_MCP_SERVER/README.md`, `_docs/_ADDON/README.md`,
    `_docs/_ROUTER/README.md`, `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`,
    and area-specific docs
- For non-trivial tasks, process-rule changes, broad docs/task rewrites, or work
  running alongside other active agents, prefer a dedicated branch/worktree so
  the change is isolated from unrelated in-progress edits.
- If a task is not broken down enough to implement safely, create or refine the
  physical task/subtask/leaf files first. Do not proceed from vague prose when
  the required owner, contract, tests, or runtime boundary is still ambiguous.
- Implement in dependency order. Do not silently downgrade agreed scope to an
  MVP; if the current task is too broad or blocked, split or mark explicit
  follow-on work in the task docs before narrowing implementation.
- Treat task docs as executable guidance for future implementers. A leaf should
  name the likely files, helper/function shape, data flow, error handling,
  contract deltas, test lane, validation command, docs updates, and acceptance
  proof.
- For docs-only task refinements, still validate with `git diff --check` and
  any targeted consistency grep/audit that proves the corrected contract is not
  contradicted elsewhere.

## Task Governance

- Treat `_docs/_TASKS/README.md` as the curated administrative board for promoted active work, promoted follow-on work, and selected completed milestones. It does not need to enumerate every historical descendant task file.
- Use one consistent planning hierarchy when the work merits it:
  - business umbrella task
  - technical subtask
  - deeper technical subtask when one branch needs its own execution track
  - leaf/micro-task when a branch still needs tighter implementation granularity
- Use one canonical task status vocabulary in task files:
  - `⏳ To Do`
  - `🚧 In Progress`
  - `✅ Done`
  - `⏭️ Superseded`
  - `❌ Cancelled`
- Keep the `**Status:**` field canonical only. Put completion dates, superseded links, reasons, or follow-on notes in dedicated fields instead of embedding them in the status text.
- Every new active task, subtask, or leaf must be actionable. At minimum include:
  - `Status`
  - `Priority`
  - `Objective`
  - `Repository Touchpoints`
  - `Acceptance Criteria`
- New or materially rewritten task files should also include, when applicable:
  - `Docs To Update` or equivalent documentation scope
  - `Tests To Add/Update` or equivalent testing scope
  - `Changelog Impact`
  - `Status / Board Update` or equivalent closeout note
- Nested tasks should use `Parent` while the parent remains open.
- Do not leave direct children open under a closed parent.
- If follow-on work remains after the parent is closed, convert it into an explicit follow-on task and mark it with `Follow-on After` instead of `Parent`. The closed parent must call out the follow-on explicitly, and `_docs/_TASKS/README.md` must track that follow-on as a standalone open item.
- If a parent is closed and older child files are kept only as historical planning slices, close them administratively as `✅ Done`, `⏭️ Superseded`, or `❌ Cancelled` and say so explicitly in the file.
- Umbrella tasks should additionally describe the business/problem framing and execution structure.
- Even very small leaves should still say which files/areas they touch and how completion will be validated. Do not leave active leaves as title-only placeholders.
- When task hierarchy or status changes, update the affected task files and `_docs/_TASKS/README.md` in the same branch so board state and task-file state do not drift.

## Task Specification Standards

When creating or materially rewriting task documentation, make the task useful
for a future implementer without requiring them to reverse-engineer the intent
from conversation history.

Umbrella tasks must include:

- business/problem framing and the concrete user-visible failure or opportunity
- business outcome and explicit non-goals
- relationship to existing board items, including whether the work is a generic
  substrate or a domain-specific consumer
- an execution structure table listing subtasks/leaves and their purpose
- a repository touchpoint table with path or module, expected ownership, and why
  the area is in scope
- a test matrix covering unit, integration/router, E2E/Blender, docs, and
  regression fixtures where applicable
- acceptance criteria written as observable product/runtime outcomes

Technical subtasks must include:

- `Parent`, `Status`, `Priority`, `Objective`, `Repository Touchpoints`, and
  `Acceptance Criteria`
- implementation notes grounded in concrete repo modules/classes/functions
- pseudocode for the intended control flow or contract shape when behavior is
  non-trivial
- security/runtime contract notes when the task touches public MCP tools,
  guided visibility, Streamable HTTP/stdio behavior, external providers,
  mutating Blender/RPC actions, file/path access, or secrets
- exact tests to add or update, including E2E tests whenever Blender scene
  state, geometry, visibility, guided flow, or client-facing runtime behavior
  changes
- documentation surfaces to update after implementation
- changelog impact and validation commands or validation category

Leaf or micro-task files must be small enough for one focused implementation
pass and should name the likely functions, contracts, fixtures, metadata files,
error cases, and validation commands that will change. They should not be
placeholders.

For quality-gate, guided-flow, or reconstruction tasks, keep this distinction
explicit:

- LLMs may propose domain-specific gates from the goal, references, and prompt
  context.
- The server must normalize those gates into a typed contract.
- The server must verify gate status with deterministic inspection/assertion or
  bounded vision evidence. Do not let prose confidence or semantic similarity
  become the authority for gate completion.

## Task Completion Checklist

- When a meaningful task/subtask/leaf is completed, do all applicable work in the same branch:
  - update the task status and add or refresh the completion summary
  - update `_docs/_TASKS/README.md` when the board or promoted milestone state changed
  - add a new `_docs/_CHANGELOG/*` entry and update `_docs/_CHANGELOG/README.md`
  - update the relevant `_docs/` area docs for the behavior that changed
  - run the relevant validation for the changed scope
- Validation is scope-dependent, not one-size-fits-all:
  - docs/process-only changes: run targeted audit/consistency validation
  - server/application/router changes: run unit tests first
  - Blender/runtime behavior changes: add or update E2E coverage when the behavior touches real scene state
- When closing any task/subtask/leaf, verify and record:
  - whether `_docs/_CHANGELOG/` needs a new historical entry
  - which `_docs/` surfaces were updated
  - which unit tests, E2E tests, and pre-commit checks were run or intentionally skipped
  - whether `_docs/_TASKS/README.md` and related parent/child statuses were updated
- If a task is closed but intentionally leaves follow-on work, record that explicitly in the completion summary and track the follow-on as its own open task.

## Documentation Expectations

For meaningful product changes, update docs in the same branch:

- `README.md` for user-facing capabilities or commands.
- `_docs/_CHANGELOG/*.md` for historical work tracking in this repo, plus `_docs/_CHANGELOG/README.md` index maintenance when adding a new entry.
- `CHANGELOG.md` only for semantic-release / release-note tracking. Do not use it as the default implementation changelog for task work.
- `_docs/AVAILABLE_TOOLS_SUMMARY.md` for tool inventory changes.
- `_docs/_MCP_SERVER/README.md` for MCP surface changes.
- `_docs/_ADDON/README.md` for addon-side API changes.
- `_docs/_ROUTER/*` for router/workflow behavior changes.
- `_docs/_TESTS/README.md` when test architecture or counts materially change.
- `_docs/_TASKS/README.md` and the relevant task file if the work completes or advances a tracked task.

## Changelog Policy

- `_docs/_CHANGELOG/*.md` is the historical repository changelog for task-level and product-level work. Use it to record meaningful implementation, behavior, architecture, testing, or documentation changes.
- When adding a new `_docs/_CHANGELOG/*.md` entry, also update `_docs/_CHANGELOG/README.md`.
- Root `CHANGELOG.md` is reserved for semantic-release / release-note output. It is not the default work log for task execution or internal change tracking.

## Multi-Agent Work

- When tooling for parallel agents is available and the work splits cleanly, use it for independent audits, independent task subtrees, docs-vs-code verification, and validation passes.
- When the user explicitly allows or asks for multi-agent work, split larger doc/task/admin changes into parallel audit, implementation, and verification slices when the write scopes do not overlap.
- Keep one owning/coordinating agent responsible for shared assumptions, merge order, and the final consistency pass.
- Do not have multiple agents edit the same file concurrently unless there is an explicit merge plan.
- Prefer parallel agent usage for:
  - auditing separate task families
  - checking docs and code against each other
  - preparing changelog/index updates while other work proceeds
  - narrowing test scope in parallel with documentation cleanup
- If a change affects both historical tracking and release notes, update both locations for their respective purposes instead of trying to collapse them into one file.
- The coordinating agent owns the final integrated state of:
  - `AGENTS.md`
  - `_docs/_TASKS/README.md`
  - parent/child task statuses
  - `_docs/_CHANGELOG/` and documentation consistency

## Current Strategic Direction

The active direction in `_docs/_TASKS/README.md` is shifting from basic tool coverage to higher-level LLM reliability and reconstruction:

- workflow extraction and router improvements
- `mesh_build` for write-side reconstruction
- `node_graph` for material and geometry-node rebuilds
- image asset management
- scene render/world configuration
- animation and drivers support

If your change touches these areas, read the corresponding task docs first. They already contain design constraints and expected file touch points.

## High-Value Docs

- Root overview: `README.md`
- Architecture: `ARCHITECTURE.md`
- Contribution rules: `CONTRIBUTING.md`
- Development commands: `_docs/_DEV/README.md`
- Test strategy: `_docs/_TESTS/README.md`
- Tool inventory: `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- MCP surface: `_docs/_MCP_SERVER/README.md`
- Addon surface: `_docs/_ADDON/README.md`
- Router system: `_docs/_ROUTER/README.md`
- Runtime boundaries: `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
- Prompting patterns for LLM clients: `_docs/_PROMPTS/README.md`

## Practical Guidance For Agents

- Before changing a tool, inspect both the MCP adapter and the Blender handler. Many apparent server changes are really cross-boundary contracts.
- Before changing router behavior, inspect metadata and tests, not just Python code.
- Before changing router metadata, keep `_schema.json`, metadata files, and metadata-loader/tests aligned so `check-router-tool-metadata` continues to pass.
- Before adding a new public tool, check whether it should instead be an action on an existing mega tool.
- Before adding a new workflow feature, check the existing task docs. Several future features are already predesigned there and should not be reinvented ad hoc.
- If a typing cleanup touches contracts, prefer making intent explicit with concrete types, guards, casts, or helper functions instead of silently broadening/narrowing product behavior.
