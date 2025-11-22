# Blender AI MCP

## Project Overview

**blender-ai-mcp** is a modular system that enables AI models (via the Model Context Protocol) to control Blender for 3D modeling tasks. It bridges the gap between LLMs and Blender's complex API by providing a stable, high-level toolset.

## 🏗️ Architecture & Mandatory Standards

This project strictly adheres to **Clean Architecture**. Shortcuts are not permitted.

### 1. System Architecture (High Level)

```
[ AI Model ] <--> [ MCP Server (Python) ] <== RPC ==> [ Blender Addon (Inside Blender) ]
```

### 2. Server-Side Layering (Python)
The `server/` directory must follow these dependency rules (Dependencies point INWARD):

*   **Inner Circle: Domain (`server/domain/`)**
    *   **Content:** Enterprise Logic, Entities (Pydantic Models), **Abstract Interfaces** for Tools.
    *   **Rules:** NO external dependencies (no `fastmcp`, no `socket`, no `bpy`). Pure Python.
    *   **Example:** `class ISceneTool(ABC): ...`

*   **Middle Circle: Application (`server/application/`)**
    *   **Content:** Application Logic, Use Cases, Tool Handlers.
    *   **Rules:** Implements Domain interfaces. Orchestrates data flow. Depends ONLY on Domain.
    *   **Example:** `class SceneToolHandler(ISceneTool): ...`

*   **Outer Circle: Adapters (`server/adapters/`)**
    *   **Content:** Interface Adapters. `FastMCP` setup, `RpcClient` implementation.
    *   **Rules:** Converts external data (MCP requests) into internal format (Application calls).
    *   **Example:** `@mcp.tool` decorators that call `SceneToolHandler`.

*   **Infrastructure (`server/infrastructure/`)**
    *   **Content:** Frameworks, Drivers, Config, Logging.

### 3. Blender Addon Layering
*   **API Layer (`blender_addon/api/`)**: High-level functions acting as the "Application Layer" for Blender.
*   **RPC Layer (`blender_addon/rpc_server.py`)**: The delivery mechanism (Infrastructure).
*   **Core Rule:** Never write logic inside `rpc_server.py`. Delegate to `api/`.

---

## 📜 Coding Principles

### General Principles
*   **SOLID:**
    *   *SRP:* One tool = One specific job.
    *   *OCP:* Extend functionality by adding new tools, not by modifying stable ones.
    *   *DIP:* High-level modules (Application) should not depend on low-level modules (RPC Client). Both should depend on abstractions (Domain Interfaces).
*   **YAGNI:** Do not implement features "for later". Implement exactly what the Task requires.
*   **DRY:** Abstract common logic (e.g., RPC error handling, validation) into utilities.

### Python Best Practices
*   **Typing:** All function signatures must have Type Hints. Use `typing` and `pydantic`.
*   **Docstrings:** Google Style docstrings are **mandatory**. They are not just for humans; they are the **Context** for the AI using the tools.
*   **Error Handling:**
    *   Use Custom Exceptions in Domain/Application layers.
    *   Catch and format errors into user-friendly strings in the Adapter layer (for the AI).
    *   Never leak raw Python stack traces to the AI model.

### FastMCP & AI Tooling Best Practices
*   **Semantics:** Tool names and docstrings must be crystal clear. The AI reads `help(function)` to understand how to use it.
*   **Determinism:** Tools should produce predictable results.
*   **Robustness:** Tools must handle "hallucinated" arguments gracefully (e.g., validate input ranges, check if objects exist).
*   **Feedback:** Return descriptive strings.
    *   *Bad:* `True`
    *   *Good:* `"Successfully created Cube at (0,0,0) named 'Cube.001'"`

---

## 🛠️ Building and Running

### Prerequisites
*   Python 3.10+
*   Poetry
*   Blender 5.0+

### Installation
```bash
poetry install
# Install blender_addon/ as a ZIP in Blender
```

### Execution
```bash
# Start MCP Server
poetry run python server/main.py
```

## ✅ Development Workflow
1.  **Plan:** Read `_docs/_TASKS/`.
2.  **Design:** Define Interface in `server/domain/tools/`.
3.  **Implement (Server):** Create Handler in `server/application/`.
4.  **Implement (Addon):** Create Logic in `blender_addon/api/`.
5.  **Bind:** Connect Handler to RPC Client and Register in `server/adapters/mcp/`.
6.  **Verify:** Run Tests.
7.  **Document:**
    *   Update `_docs/_CHANGELOG/`. Create a new file for major changes, update `README.md` index.
    *   Update Semantic Documentation in `_docs/_ADDON/` and `_docs/_MCP_SERVER/`. Treat these directories as a Knowledge Base. Don't just dump everything in README; create specific topic files if needed.
    *   Update `_docs/_TASKS/` statuses.