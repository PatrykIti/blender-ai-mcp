"""
Guards against API drift between MCP tool definitions and router tool metadata.

Task: TASK-061
"""

import ast
import json
from pathlib import Path


def _find_repo_root(start: Path) -> Path:
    for candidate in [start] + list(start.parents):
        if (candidate / "pyproject.toml").exists():
            return candidate
    raise RuntimeError(f"Could not find repo root from: {start}")


def _is_mcp_tool_decorator(decorator: ast.expr) -> bool:
    if isinstance(decorator, ast.Call):
        decorator = decorator.func

    return (
        isinstance(decorator, ast.Attribute)
        and isinstance(decorator.value, ast.Name)
        and decorator.value.id == "mcp"
        and decorator.attr == "tool"
    )


def _extract_mcp_tool_signatures(areas_dir: Path) -> dict[str, set[str] | None]:
    """
    Returns:
        Dict of tool_name -> set(parameter_names), excluding ctx
        If a tool accepts **kwargs, returns None for that tool (skip strict param checks).
    """
    signatures: dict[str, set[str] | None] = {}

    for py_file in sorted(areas_dir.glob("*.py")):
        if py_file.name == "__init__.py":
            continue

        tree = ast.parse(py_file.read_text(encoding="utf-8"))

        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue

            if not any(_is_mcp_tool_decorator(d) for d in node.decorator_list):
                continue

            tool_name = node.name

            if node.args.kwarg is not None:
                signatures[tool_name] = None
                continue

            param_names = []
            param_names.extend(arg.arg for arg in node.args.posonlyargs)
            param_names.extend(arg.arg for arg in node.args.args)
            param_names.extend(arg.arg for arg in node.args.kwonlyargs)

            signatures[tool_name] = {p for p in param_names if p != "ctx"}

    return signatures


def _iter_tools_metadata(metadata_dir: Path) -> list[tuple[str, Path, set[str]]]:
    out: list[tuple[str, Path, set[str]]] = []

    for json_file in sorted(metadata_dir.rglob("*.json")):
        if json_file.name == "_schema.json":
            continue

        data = json.loads(json_file.read_text(encoding="utf-8"))
        tool_name = data.get("tool_name")
        if not tool_name:
            continue

        params = data.get("parameters") or {}
        param_names = set(params.keys()) if isinstance(params, dict) else set()
        out.append((tool_name, json_file, param_names))

    return out


def _extract_router_emitted_tool_names(router_dir: Path) -> set[str]:
    """
    Finds string literals passed via keyword argument `tool_name=...` in router code.
    """
    tool_names: set[str] = set()

    for py_file in sorted(router_dir.rglob("*.py")):
        if py_file.name == "__init__.py":
            continue

        tree = ast.parse(py_file.read_text(encoding="utf-8"))

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue

            for kw in node.keywords:
                if kw.arg != "tool_name":
                    continue
                if not isinstance(kw.value, ast.Constant):
                    continue
                if not isinstance(kw.value.value, str):
                    continue

                tool_names.add(kw.value.value)

    return tool_names


def test_tools_metadata_tool_names_exist_in_mcp():
    repo_root = _find_repo_root(Path(__file__).resolve().parent)
    mcp_signatures = _extract_mcp_tool_signatures(
        repo_root / "server" / "adapters" / "mcp" / "areas"
    )
    tools_metadata = _iter_tools_metadata(
        repo_root / "server" / "router" / "infrastructure" / "tools_metadata"
    )

    unknown = []
    for tool_name, json_file, _param_names in tools_metadata:
        if tool_name not in mcp_signatures:
            unknown.append(f"- {tool_name} ({json_file.relative_to(repo_root)})")

    assert not unknown, (
        "Tools metadata references non-existent MCP tools:\n" + "\n".join(unknown)
    )


def test_tools_metadata_parameters_match_mcp_signatures():
    repo_root = _find_repo_root(Path(__file__).resolve().parent)
    mcp_signatures = _extract_mcp_tool_signatures(
        repo_root / "server" / "adapters" / "mcp" / "areas"
    )
    tools_metadata = _iter_tools_metadata(
        repo_root / "server" / "router" / "infrastructure" / "tools_metadata"
    )

    missing = []
    mismatches = []
    for tool_name, json_file, meta_params in tools_metadata:
        if tool_name not in mcp_signatures:
            missing.append(f"- {tool_name} ({json_file.relative_to(repo_root)})")
            continue

        sig_params = mcp_signatures[tool_name]
        if sig_params is None:
            continue

        extra_params = sorted(meta_params - sig_params)
        if extra_params:
            mismatches.append(
                f"- {tool_name} ({json_file.relative_to(repo_root)}): "
                f"unknown params: {extra_params}"
            )

    assert not (missing or mismatches), (
        "Tools metadata is out of sync with MCP tool signatures:\n"
        + ("\nMissing tools:\n" + "\n".join(missing) if missing else "")
        + ("\nInvalid params:\n" + "\n".join(mismatches) if mismatches else "")
    )


def test_router_emitted_tool_names_exist_in_mcp():
    repo_root = _find_repo_root(Path(__file__).resolve().parent)
    mcp_signatures = _extract_mcp_tool_signatures(
        repo_root / "server" / "adapters" / "mcp" / "areas"
    )
    emitted = _extract_router_emitted_tool_names(repo_root / "server" / "router")

    unknown = sorted(tool for tool in emitted if tool not in mcp_signatures)

    assert not unknown, (
        "Router code emits tool_name values not present in MCP tools:\n"
        + "\n".join(f"- {tool}" for tool in unknown)
    )
