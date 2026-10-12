# Support

> [!WARNING]
> **Project discontinued — this repository is no longer maintained.**
> `blender-ai-mcp` will not be developed further. It is being replaced by an entirely new and significantly better solution: much stronger 3D scene understanding, deeper and more reliable cooperation with Blender, far better workflow control, and more. The new add-on will be released soon.

**Support is no longer provided for this project.** Issues, questions, and feature requests are no longer triaged or answered, and no further fixes or releases will be made. The information below is kept only as a historical reference for anyone running the archived code on their own.

## Where to Ask / Report (Historical)

- **Bugs** and **feature requests**: GitHub Issues are no longer being triaged.
- **Security issues**: see `SECURITY.md`.

## Useful Details When Debugging On Your Own

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
