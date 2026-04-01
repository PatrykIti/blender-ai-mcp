# 129 - 2026-03-22: Router metadata schema alignment for full pre-commit validation

## Summary

Completed the router metadata/schema cleanup that was left as follow-up work after the Python typing baseline.

The router metadata JSON layer now uses one deliberate shared parameter type vocabulary:

- `string`
- `int`
- `float`
- `bool`
- `enum`
- `array`
- `vector3`
- `object`
- `scalar`

This removed older ad hoc aliases such as:

- `boolean`
- `integer`
- `number`
- `list[float]`
- `list[int]`
- `list[string]`
- `list[list[float]]`
- `list[list[int]]`
- `list[float] | string`
- `array | string`
- `string_or_list`
- `any`
- `dict`

## Updated files

- `server/router/infrastructure/tools_metadata/_schema.json`
- `server/router/infrastructure/tools_metadata/extraction/*.json`
- `server/router/infrastructure/tools_metadata/material/*.json`
- `server/router/infrastructure/tools_metadata/mesh/*.json`
- `server/router/infrastructure/tools_metadata/modeling/*.json`
- `server/router/infrastructure/tools_metadata/scene/*.json`
- `server/router/infrastructure/tools_metadata/text/*.json`
- `_docs/_TASKS/TASK-100_Router_Metadata_Schema_Alignment.md`
- `_docs/_TASKS/README.md`

## Validation

```bash
PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files
```

Result:

- full repo `pre-commit` suite passed
- `check-router-tool-metadata` passed
