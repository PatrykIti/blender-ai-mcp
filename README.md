# blender-ai-mcp

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://github.com/PatrykIti/blender-ai-mcp/pkgs/container/blender-ai-mcp)
[![CI Status](https://github.com/PatrykIti/blender-ai-mcp/actions/workflows/release.yml/badge.svg)](https://github.com/PatrykIti/blender-ai-mcp/actions)

**Modular MCP Server + Blender Addon for AI-Driven 3D Modeling.**

Enable LLMs (Claude, ChatGPT) to control Blender reliably. Built with **Clean Architecture** for stability and scalability.

---

## 🌟 Key Features

- **Scene Management**: List, delete, and clean objects.
- **Modeling Tools**: Create primitives, transform objects, apply modifiers.
- **Stable API**: Abstracted high-level tools instead of raw `bpy` access.
- **Dockerized**: Run the MCP server in a container without polluting your environment.

## 🚀 Quick Start

### 1. Install the Blender Addon
1. Download `blender_ai_mcp.zip` from the [Releases Page](../../releases).
2. Open Blender -> Edit -> Preferences -> Add-ons.
3. Click **Install...** and select the zip file.
4. Enable the addon. It will start a local server on port `8765`.

### 2. Configure your MCP Client (Cline / Claude Code)

We recommend using Docker to run the MCP Server.

**Cline Configuration (`cline_mcp_settings.json`):**

```json
{
  "mcpServers": {
    "blender-ai-mcp": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "BLENDER_RPC_HOST=host.docker.internal",
        "ghcr.io/patrykiti/blender-ai-mcp:latest"
      ],
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

*(Note: On Linux, replace `host.docker.internal` with `127.0.0.1` and add `--network host`)*.

---

## 📈 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=PatrykIti/blender-ai-mcp&type=Date)](https://star-history.com/#PatrykIti/blender-ai-mcp&Date)

---

## 🏗️ Architecture

This project uses a split-architecture design:
1.  **MCP Server (Python/FastMCP)**: Handles AI communication.
2.  **Blender Addon (Python/bpy)**: Executes 3D operations.

Communication happens via **JSON-RPC over TCP sockets**.

See [ARCHITECTURE.md](ARCHITECTURE.md) for deep dive.

## 🤝 Contributing

We welcome contributions! Please read [CONTRIBUTING.md](CONTRIBUTING.md) to understand our Clean Architecture standards before submitting a Pull Request.

## 👨‍💻 Author

**Patryk Ciechański**
*   GitHub: [PatrykIti](https://github.com/PatrykIti)

## 📜 License

MIT License.
