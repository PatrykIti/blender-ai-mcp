# 321. TASK-163 harness closeout and MLX RU proof

Closed the final `TASK-163-07` proof lane and resolved the local MLX
reference-understanding blocker.

## What Changed

- added a real live `reference-understanding` mode to `scripts/vision_harness.py`
- introduced the nested blocker leaf `TASK-163-07-01` for the local MLX RU
  failure, then resolved it
- identified the local MLX blocker as output truncation on the RU contract and
  raised the local RU output budget to a minimum of `900` tokens
- kept the existing RU contract strict while improving local failure diagnostics
- validated both local and external live RU proof on the shared squirrel
  reference image
- closed `TASK-163-07` and the umbrella `TASK-163`

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_prompting.py tests/unit/adapters/mcp/test_vision_parsing.py tests/unit/adapters/mcp/test_vision_local_backend.py tests/unit/scripts/test_script_tooling.py -q`
- `poetry run python scripts/vision_harness.py --backend mlx_local --mode reference-understanding --goal "classify the attached low-poly squirrel reference for bounded Blender planning" --reference _docs/_TEST_IMAGES/squirrel-front.png --mlx-model mlx-community/Qwen3-VL-4B-Instruct-4bit`
- `poetry run python scripts/vision_harness.py --backend openai_compatible_external --mode reference-understanding --goal "classify the attached low-poly squirrel reference for bounded Blender planning" --reference _docs/_TEST_IMAGES/squirrel-front.png --external-provider openrouter --external-contract-profile generic_full --openrouter-model qwen/qwen3-vl-32b-instruct --openrouter-api-key-env OPENROUTER_API_KEY`
