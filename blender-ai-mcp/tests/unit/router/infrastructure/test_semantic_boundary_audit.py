"""Tests for TASK-095-01 semantic boundary policy and code audit."""

from __future__ import annotations

import ast
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
AUDIT_DOC = REPO_ROOT / "_docs" / "_ROUTER" / "semantic-boundary-audit.md"

EXPECTED_AUDITED_CALL_SITES = {
    "server/router/application/classifier/intent_classifier.py",
    "server/router/application/classifier/workflow_intent_classifier.py",
    "server/router/application/matcher/semantic_matcher.py",
    "server/router/application/matcher/semantic_workflow_matcher.py",
    "server/router/application/matcher/modifier_extractor.py",
    "server/router/application/matcher/ensemble_aggregator.py",
    "server/router/application/resolver/parameter_resolver.py",
    "server/router/application/resolver/parameter_store.py",
    "server/router/application/engines/workflow_adapter.py",
    "server/router/application/router.py",
}

PLATFORM_BOUNDARY_PATHS = (
    REPO_ROOT / "server" / "adapters" / "mcp" / "platform",
    REPO_ROOT / "server" / "adapters" / "mcp" / "discovery",
    REPO_ROOT / "server" / "adapters" / "mcp" / "transforms",
    REPO_ROOT / "server" / "adapters" / "mcp" / "visibility",
)

TRUTH_BOUNDARY_PATHS = (
    REPO_ROOT / "server" / "adapters" / "mcp" / "router_helper.py",
    REPO_ROOT / "server" / "router" / "application" / "engines" / "tool_correction_engine.py",
    REPO_ROOT / "server" / "adapters" / "mcp" / "areas" / "scene.py",
    REPO_ROOT / "server" / "adapters" / "mcp" / "areas" / "mesh.py",
)

FORBIDDEN_SEMANTIC_IMPORT_PREFIXES = (
    "sentence_transformers",
    "server.router.application.classifier",
    "server.router.application.matcher",
    "server.router.application.resolver",
)


def _extract_documented_file_paths(doc_path: Path) -> set[str]:
    text = doc_path.read_text(encoding="utf-8")
    return set(re.findall(r"server/[A-Za-z0-9_./-]+\.py", text))


def _iter_python_files(paths: tuple[Path, ...]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            files.extend(sorted(p for p in path.rglob("*.py") if p.name != "__init__.py"))
        else:
            files.append(path)
    return files


def _extract_imported_modules(py_file: Path) -> set[str]:
    tree = ast.parse(py_file.read_text(encoding="utf-8"))
    modules: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)

    return modules


def test_semantic_boundary_audit_covers_current_labse_call_sites():
    """The audit doc should enumerate the repo's current semantic call sites."""

    documented = _extract_documented_file_paths(AUDIT_DOC)

    assert EXPECTED_AUDITED_CALL_SITES <= documented


def test_semantic_boundary_audit_declares_allowed_and_disallowed_roles():
    """The audit doc should explicitly separate allowed and disallowed LaBSE roles."""

    text = AUDIT_DOC.read_text(encoding="utf-8")

    for expected in (
        "Allowed LaBSE roles in this repo:",
        "Disallowed LaBSE roles in this repo:",
        "final public tool exposure",
        "public search/discovery ownership",
        "scene-state truth",
        "post-execution verification",
        "`TASK-095-02`",
        "`TASK-095-03`",
    ):
        assert expected in text


def test_platform_boundary_files_do_not_import_semantic_router_components():
    """FastMCP platform/exposure files should not depend on LaBSE matching components."""

    for py_file in _iter_python_files(PLATFORM_BOUNDARY_PATHS):
        modules = _extract_imported_modules(py_file)
        forbidden = sorted(module for module in modules if module.startswith(FORBIDDEN_SEMANTIC_IMPORT_PREFIXES))
        assert forbidden == [], f"{py_file.relative_to(REPO_ROOT)} imports semantic modules: {forbidden}"


def test_truth_and_verification_files_do_not_import_semantic_router_components():
    """Inspection/truth-side MCP files should not depend on semantic matching modules."""

    for py_file in _iter_python_files(TRUTH_BOUNDARY_PATHS):
        modules = _extract_imported_modules(py_file)
        forbidden = sorted(module for module in modules if module.startswith(FORBIDDEN_SEMANTIC_IMPORT_PREFIXES))
        assert forbidden == [], f"{py_file.relative_to(REPO_ROOT)} imports semantic modules: {forbidden}"
