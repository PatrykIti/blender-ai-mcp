# TASK-013: Viewport Output Modes & Docker Temp Mapping

**Status:** ✅ Complete  
**Priority:** Medium  
**Phase:** Phase 2 - Scene Tools  
**Dependencies:** TASK-009 (Extend Viewport Control), TASK-005 (Dockerize Server)  
**Created Date:** 2025-11-26  
**Completion Date:** 2025-11-26

---

## 🎯 Objective

Extend the `scene_get_viewport` tool so LLMs can choose how viewport images are returned (pure base64, file path, or rich markdown), while keeping Clean Architecture boundaries intact and supporting Docker deployments where `/tmp` inside the container is mapped to a host-visible directory.

The goal is to make the tool equally usable for:
- Vision-capable LLMs that want direct base64 image data.
- Non-vision LLMs and users who need a file path on the host.
- Rich UIs that benefit from markdown with an inline preview and explicit file path.

---

## 📋 Requirements

### 1. Tool API & Output Modes
- Add a new parameter to the MCP tool:
  - `output_mode: Literal["IMAGE", "BASE64", "FILE", "MARKDOWN"] = "IMAGE"`.
- Behavior per mode:
  - `IMAGE` (default):
    - Return a FastMCP `Image` resource, preserving existing behavior for clients like Cline.
  - `BASE64`:
    - Return **only** the base64-encoded JPEG (or a minimal wrapper structure/string clearly indicating it's pure base64), suitable for direct feeding into a Vision module.
    - Do **not** write any files or include markdown/data URLs.
  - `FILE`:
    - Write the decoded image into a temp directory.
    - Return a human-readable message that includes the **absolute host-visible file path**, but no inline markdown image or `data:` URL.
  - `MARKDOWN`:
    - Preserve the richer Roo Code behavior: write the file, maintain a `viewport_latest.jpg`, and return a markdown string with:
      - A clear text header describing where the image was saved.
      - A `data:image/jpeg;base64,...` URL that UIs/LLMs with Vision can render inline.
      - A note with the host-visible path for users who need to open the file manually.
- Document the new parameter and behaviors in the tool docstring so LLMs can self-select the right mode based on their capabilities.

### 2. Clean Architecture Boundaries
- **Domain Layer (`server/domain/tools/`)**
  - Keep `ISceneTool.get_viewport` focused on core semantics: returning base64 image data (and optionally simple metadata), without any knowledge of `output_mode`, markdown, or filesystem paths.
  - If an explicit request model is introduced (e.g. `SceneViewportRequest`), restrict it to logical parameters (`width`, `height`, `shading`, `camera_name`, `focus_target`) and **exclude** output formatting concerns.
- **Application Layer (`server/application/handlers/`)**
  - Ensure handlers still operate solely on domain abstractions and RPC calls.
  - Do not introduce dependencies on `tempfile`, `pathlib`, environment variables, or Docker specifics.
- **Adapter Layer (`server/adapters/mcp/`)**
  - Implement `output_mode` handling here, after retrieving base64 from the handler.
  - Centralize all output formatting (plain base64, file paths, markdown/data URLs) in the MCP tool function, keeping it deterministic and robust against invalid arguments (e.g. unknown `output_mode` → friendly error string).

### 3. Temp Directory & Docker Mapping
- Introduce an infrastructure-level helper for temp directory resolution, e.g. in `server/infrastructure/tmp_paths.py`:
  - Responsibilities:
    - Determine the **internal** temp directory (inside the container) used for writing files.
    - Determine the corresponding **external/host** directory path that should be shown to users.
  - Configuration via environment variables (names can be adjusted during implementation but must be documented):
    - `BLENDER_AI_TMP_INTERNAL_DIR` – optional. If set, use this as the base internal temp directory. Otherwise, default to `tempfile.gettempdir()`.
    - `BLENDER_AI_TMP_EXTERNAL_DIR` – optional. If set, this is the host-visible directory corresponding to the internal temp dir; if not set, fall back to the internal path.
  - The helper should provide:
    - A stable subdirectory (e.g. `blender-ai-mcp`) under the chosen base path.
    - Utilities to construct both internal and external full paths for a given filename (e.g. `viewport_YYYYMMDD_HHMMSS.jpg` and `viewport_latest.jpg`).
- Ensure **no** direct `os.environ` access, `tempfile`, or `pathlib` usage leaks into Domain/Application; keep this confined to infrastructure and the MCP adapter.

### 4. MCP Adapter Implementation (`scene_get_viewport`)
- Update the MCP tool signature to include `output_mode` and use dependency injection to obtain the scene handler as today.
- After receiving base64 from the handler:
  - For `BASE64`: return base64 as specified above.
  - For `FILE` and `MARKDOWN`:
    - Use the temp directory helper to compute both internal and external paths.
    - Decode the base64 and write the image bytes to the internal path.
    - Maintain a `viewport_latest.jpg` alongside timestamped files for convenience.
    - Build the returned string using the **external** path so that, when Docker bind mounts are configured, the path is directly usable on the host.
- Handle invalid `output_mode` values gracefully:
  - Return a descriptive error string listing the allowed modes instead of raising raw exceptions.
- Ensure all imports (`tempfile`, `pathlib`, `datetime`, `base64`, env handling) are placed at the **top of the module**, not inside the function body.

### 5. Tests
- Add or extend tests to cover:
  - `output_mode="BASE64"` – no filesystem writes, raw base64 returned.
  - `output_mode="FILE"` – file written, string contains the expected external path, no markdown.
  - `output_mode="MARKDOWN"` – file written, markdown and `data:` URL present, external path included.
  - Behavior when `BLENDER_AI_TMP_INTERNAL_DIR` / `BLENDER_AI_TMP_EXTERNAL_DIR` are set vs unset.
- Where possible, mock filesystem and environment access without touching actual `/tmp`.

### 6. Documentation Updates
- **`README.md`**
  - Add a subsection under Scene tools describing `scene_get_viewport` output modes and how LLMs should choose between them (Vision vs non-Vision clients).
  - Document the environment variables used for temp directory mapping and provide example Docker run / Compose snippets:
    - Example volume mapping: `-v /host/tmp/blender-ai-mcp:/tmp/blender-ai-mcp`.
    - Example env configuration: `BLENDER_AI_TMP_INTERNAL_DIR=/tmp/blender-ai-mcp`, `BLENDER_AI_TMP_EXTERNAL_DIR=/host/tmp/blender-ai-mcp`.
- Ensure the docs mention that imports and filesystem concerns live only in the outer layers (Adapters/Infrastructure), consistent with Clean Architecture.

---

## ✅ Checklist
- [x] Design and finalize `output_mode` API (name, allowed values, defaults) for `scene_get_viewport`.
- [x] Confirm/adjust domain and application interfaces so they remain format-agnostic and return base64 image data.
- [x] Implement temp directory helper in Infrastructure (internal/external path resolution with env vars).
- [x] Update MCP adapter implementation of `scene_get_viewport` to support all output modes and use the helper.
- [x] Add tests for all output modes and env-based temp-dir behavior.
- [x] Update `README.md` with output mode semantics and Docker tmp mapping configuration.
