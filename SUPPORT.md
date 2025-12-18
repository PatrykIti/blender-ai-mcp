# Support

## Where to Ask / Report

- **Bugs**: open a GitHub Issue using the **Bug Report** template.
- **Feature requests**: open a GitHub Issue using the **Feature Request** template.
- **Security issues**: follow `SECURITY.md` (private reporting).

If you are unsure which template fits, open a bug report and describe the expected vs actual behavior.

## What to Include (So We Can Help Fast)

Please include:
- OS (macOS/Windows/Linux) + CPU architecture
- Blender version (e.g., 5.0.0) + whether Blender is running in GUI/background
- Python version used for the MCP server
- How you run the MCP server (Docker command / `poetry run ...`)
- Router status (`ROUTER_ENABLED`, and output of `router_get_status` if applicable)
- Logs (`LOG_LEVEL=DEBUG` helps)
- Minimal reproduction steps (ideally a short numbered list)

## Common Troubleshooting

- Verify Blender addon is enabled and the RPC server is reachable (default port: `8765`).
- If using Docker on Linux, ensure host networking/host resolution is set correctly (see root `README.md` MCP client config examples).

