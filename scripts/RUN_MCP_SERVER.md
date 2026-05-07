# run_mcp_server

`scripts/run_mcp_server.sh` is the macOS-first interactive launcher for this
repo.

It is intended for a user who wants the launcher to:

- explain what prerequisite is being checked
- detect whether it is already installed
- show the current version when available
- offer install / update / skip choices
- derive the final MCP launch plan
- start the Docker-guided MCP profile with the matching optional classifier
  settings

Version 1 is intentionally **macOS-first**. Linux and Windows follow-ons are
planned under `TASK-165`, but they are not yet operator-supported here.

## Entry Points

- top-level interactive launcher:
  - `scripts/run_mcp_server.sh`
- Python implementation:
  - `scripts/run_mcp_server.py`
- lower-level Docker/OpenRouter helper reused by the launcher:
  - `scripts/run_streamable_openrouter.sh`
- local SigLIP2 classifier sidecar helper:
  - `scripts/run_reference_classifier_sidecar.sh`
  - this helper starts only the classifier sidecar and stays in the foreground
  - it does not launch the FastMCP server by itself

## What The Launcher Does

Current flow:

1. Detect macOS / Python baseline
2. Check Poetry
3. Check Docker Desktop
4. Optionally install MLX support for local models
5. Optionally install `vision` dependencies for the local classifier sidecar
6. Ask for runtime/profile choices
7. Ask for OpenRouter model / API key if needed
8. Ask whether to enable the optional classifier and whether it should
   auto-start locally
9. Show the final launch plan
10. Start the Docker-guided MCP profile

## First Run

```bash
./scripts/run_mcp_server.sh
```

If you run `scripts/run_reference_classifier_sidecar.sh` directly, expect only
the classifier sidecar on `:9200`. The combined FastMCP + Docker-guided launch
belongs to `scripts/run_mcp_server.sh` or the lower-level
`scripts/run_streamable_openrouter.sh`.

The launcher is interactive. It will prompt before:

- opening Docker Desktop install/update guidance
- running the Poetry installer
- running `poetry install --with ...`
- launching the final MCP server

## Docker On macOS

The launcher uses the official Docker Desktop for Mac operator path:

- if Docker Desktop is missing, it can open the official install page
- if `/Users/.../Downloads/Docker.dmg` exists, it can run the documented
  command-line install path after confirmation
- if Docker Desktop is installed but the daemon is not reachable, it can open
  the Docker app and wait for you to continue

## Optional Dependency Groups

The launcher distinguishes:

- `mlx`
  - local MLX model support
- `vision`
  - local classifier-sidecar dependencies such as `transformers` + `torch`

It only offers to install the groups that are actually missing.

## Profile Scope

The current launcher focuses on the Docker-guided OpenRouter profile already
used in this repo.

It does not yet expose every possible runtime permutation. That broader
installer family is tracked under `TASK-165`.

## Notes

- if you refuse an install or update step, the launcher keeps your current
  state and explains the consequence
- the launcher is intended to be explicit, not silent
- the lower-level helpers in `scripts/` still exist and can be called directly
  when you want a narrower operator path
