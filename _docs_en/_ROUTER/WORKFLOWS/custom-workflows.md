# Custom Workflows (YAML/JSON)

Custom workflows let the Router expand a single intent into a deterministic sequence of tool calls.
You add them by dropping a YAML/JSON file into the custom workflows directory.

---

## Where to Put Files

Place workflow files here:

`server/router/application/workflows/custom/`

Supported extensions:

- `.yaml` / `.yml` (recommended)
- `.json`

---

## How Expansion Works (Mental Model)

Workflow expansion is a pipeline:

1. computed parameters
2. loops + `{var}` interpolation
3. `$CALCULATE(...)` / `$AUTO_*` / `$variable` resolution
4. `condition` evaluation + context simulation

Adaptation (confidence-based filtering) happens before `condition` (two filters).

Full explanation: [workflow-execution-pipeline.md](./workflow-execution-pipeline.md)

---

## Authoring Docs

- Tutorial (step-by-step): [creating-workflows-tutorial.md](./creating-workflows-tutorial.md)
- Full YAML syntax guide: [yaml-workflow-guide.md](./yaml-workflow-guide.md)
- Expression reference (`{var}`, `$CALCULATE`, `$AUTO_*`, `condition`): [expression-reference.md](./expression-reference.md)

---

## Tips

- Use `loop:` + `{var}` to avoid copy/paste for repeated elements.
- If a step must be controlled only by `condition` (not semantic filtering), add `disable_adaptation: true`.
- Prefer small, composable workflows over huge monoliths; use tags/optional steps for “nice-to-have” features.

