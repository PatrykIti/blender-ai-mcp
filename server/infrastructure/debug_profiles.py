"""Central debug-profile parsing and bounded runtime logging helpers."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any, Final, Mapping

_ROUTER_SCOPE = "router"
_REGISTERED_SCOPE_NAMES: Final[tuple[str, ...]] = (
    "vision",
    "reference",
    "tools",
    "transport",
    "visibility",
    "guided_flow",
    _ROUTER_SCOPE,
)
_ACCEPTED_SELECTOR_NAMES: Final[tuple[str, ...]] = ("off", "all", *_REGISTERED_SCOPE_NAMES)
_ENV_TRUTHY_VALUES: Final[frozenset[str]] = frozenset({"1", "true", "yes"})


@dataclass(frozen=True)
class DebugProfileDefinition:
    """One named repo-owned debug scope."""

    name: str
    logger_names: tuple[str, ...]
    description: str


@dataclass(frozen=True)
class DebugProfileRegistry:
    """Stable registry for repo-owned debug scopes and onboarding."""

    profiles: Mapping[str, DebugProfileDefinition]

    def __post_init__(self) -> None:
        expected_names = set(self.profiles)
        for name, definition in self.profiles.items():
            if definition.name != name:
                raise ValueError(f"Debug profile registry entry '{name}' must use the same canonical definition name.")
        if expected_names != set(_REGISTERED_SCOPE_NAMES):
            missing = sorted(set(_REGISTERED_SCOPE_NAMES).difference(expected_names))
            extra = sorted(expected_names.difference(_REGISTERED_SCOPE_NAMES))
            details: list[str] = []
            if missing:
                details.append(f"missing={missing}")
            if extra:
                details.append(f"extra={extra}")
            joined = ", ".join(details) if details else "unknown registry mismatch"
            raise ValueError(f"Debug profile registry must cover the canonical scope set ({joined}).")

    @property
    def scope_names(self) -> tuple[str, ...]:
        return tuple(self.profiles)

    def require_scope(self, scope_name: str) -> str:
        normalized = str(scope_name).strip().lower()
        if normalized not in self.profiles:
            supported = ", ".join(self.scope_names)
            raise ValueError(f"Unknown debug scope '{scope_name}'. Supported scopes: {supported}.")
        return normalized


@dataclass(frozen=True)
class DebugProfileState:
    """Resolved repo-owned debug state for the current runtime."""

    selector: frozenset[str] | None
    enabled_scopes: frozenset[str]
    authoritative_selector: bool
    router_legacy_compatibility: bool

    def scope_enabled(self, scope_name: str, *, registry: DebugProfileRegistry) -> bool:
        return registry.require_scope(scope_name) in self.enabled_scopes


DEFAULT_DEBUG_PROFILE_REGISTRY = DebugProfileRegistry(
    profiles={
        "vision": DebugProfileDefinition(
            name="vision",
            logger_names=(
                "server.adapters.mcp.areas.reference_understanding",
                "server.adapters.mcp.vision.reference_support",
            ),
            description="Reference understanding backend and optional support timing/failure summaries.",
        ),
        "reference": DebugProfileDefinition(
            name="reference",
            logger_names=(
                "server.adapters.mcp.areas.reference",
                "server.adapters.mcp.areas.reference_images_runtime",
            ),
            description="Reference attach/list/remove/clear plus staged compare/iterate lifecycle summaries.",
        ),
        "tools": DebugProfileDefinition(
            name="tools",
            logger_names=("server.adapters.mcp.discovery.search_surface",),
            description="call_tool(...) proxy resolution, canonicalization, and hidden-tool recovery diagnostics.",
        ),
        "transport": DebugProfileDefinition(
            name="transport",
            logger_names=(
                "server.adapters.mcp.server",
                "server.adapters.mcp.context_utils",
            ),
            description="Transport bootstrap plus surfaced session/transport identity diagnostics.",
        ),
        "visibility": DebugProfileDefinition(
            name="visibility",
            logger_names=("server.adapters.mcp.visibility_runtime",),
            description="Guided visibility transaction and audit diagnostics.",
        ),
        "guided_flow": DebugProfileDefinition(
            name="guided_flow",
            logger_names=(
                "server.adapters.mcp.session_capabilities_flow",
                "server.adapters.mcp.session_capabilities_registry",
                "server.adapters.mcp.session_capabilities_bootstrap",
                "server.adapters.mcp.session_capabilities_runtime_glue",
            ),
            description="Guided-flow step transitions, spatial refresh barriers, and bootstrap/runtime state shaping.",
        ),
        "router": DebugProfileDefinition(
            name="router",
            logger_names=(
                "router",
                "server.router.application.router",
                "server.router.application.matcher.ensemble_matcher",
                "server.adapters.mcp.areas.router",
                "server.adapters.mcp.router_helper",
                "server.application.tool_handlers.router_handler",
            ),
            description="Router goal/status, correction, ensemble, and execution-audit diagnostics.",
        ),
    }
)


def supported_debug_selector_values() -> tuple[str, ...]:
    """Return the accepted operator-facing selector vocabulary."""

    return _ACCEPTED_SELECTOR_NAMES


def _accepted_selector_text() -> str:
    values = ", ".join(supported_debug_selector_values())
    return f"BLENDER_AI_DEBUG must be one of: {values} or a comma-separated combination of named scopes."


def _coerce_tokens(value: str | frozenset[str] | tuple[str, ...] | list[str] | set[str] | None) -> list[str] | None:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        return stripped.split(",")
    if isinstance(value, (frozenset, set, tuple, list)):
        return [str(item) for item in value]
    raise ValueError(_accepted_selector_text())


def parse_debug_selector(
    value: str | frozenset[str] | tuple[str, ...] | list[str] | set[str] | None,
    *,
    registry: DebugProfileRegistry = DEFAULT_DEBUG_PROFILE_REGISTRY,
) -> frozenset[str] | None:
    """Parse and validate the operator-facing BLENDER_AI_DEBUG selector."""

    raw_tokens = _coerce_tokens(value)
    if raw_tokens is None:
        return None

    normalized_tokens: list[str] = []
    seen: set[str] = set()
    duplicates: set[str] = set()
    for raw_token in raw_tokens:
        token = str(raw_token).strip().lower()
        if not token:
            raise ValueError(
                "BLENDER_AI_DEBUG contains an empty item. Use a comma-separated list without blank entries."
            )
        if token in seen:
            duplicates.add(token)
        seen.add(token)
        normalized_tokens.append(token)

    if duplicates:
        repeated = ", ".join(sorted(duplicates))
        raise ValueError(f"BLENDER_AI_DEBUG contains duplicate scope names: {repeated}.")

    unknown = sorted(set(normalized_tokens).difference({"off", "all", *registry.scope_names}))
    if unknown:
        joined = ", ".join(unknown)
        raise ValueError(f"Unknown BLENDER_AI_DEBUG scope(s): {joined}. {_accepted_selector_text()}")

    if "off" in normalized_tokens:
        if len(normalized_tokens) != 1:
            raise ValueError("BLENDER_AI_DEBUG=off cannot be combined with other debug scopes.")
        return frozenset()

    if "all" in normalized_tokens:
        return frozenset({"all"})

    return frozenset(normalized_tokens)


def resolve_debug_profile_state(
    *,
    debug_selector: str | frozenset[str] | tuple[str, ...] | list[str] | set[str] | None,
    router_log_decisions: bool,
    registry: DebugProfileRegistry = DEFAULT_DEBUG_PROFILE_REGISTRY,
) -> DebugProfileState:
    """Resolve effective repo-owned debug scopes from config or env input."""

    selector = parse_debug_selector(debug_selector, registry=registry)
    if selector is None:
        enabled_scopes = frozenset({_ROUTER_SCOPE}) if router_log_decisions else frozenset()
        return DebugProfileState(
            selector=None,
            enabled_scopes=enabled_scopes,
            authoritative_selector=False,
            router_legacy_compatibility=bool(router_log_decisions),
        )

    if not selector:
        return DebugProfileState(
            selector=selector,
            enabled_scopes=frozenset(),
            authoritative_selector=True,
            router_legacy_compatibility=False,
        )

    if "all" in selector:
        enabled_scopes = frozenset(registry.scope_names)
    else:
        enabled_scopes = frozenset(registry.require_scope(scope_name) for scope_name in selector)

    return DebugProfileState(
        selector=selector,
        enabled_scopes=enabled_scopes,
        authoritative_selector=True,
        router_legacy_compatibility=False,
    )


def resolve_debug_profile_state_from_config(
    config: Any,
    *,
    registry: DebugProfileRegistry = DEFAULT_DEBUG_PROFILE_REGISTRY,
) -> DebugProfileState:
    """Resolve repo-owned debug state from a config-like object."""

    return resolve_debug_profile_state(
        debug_selector=getattr(config, "BLENDER_AI_DEBUG", None),
        router_log_decisions=bool(getattr(config, "ROUTER_LOG_DECISIONS", True)),
        registry=registry,
    )


def resolve_debug_profile_state_from_env(
    *,
    registry: DebugProfileRegistry = DEFAULT_DEBUG_PROFILE_REGISTRY,
) -> DebugProfileState:
    """Resolve repo-owned debug state directly from the process environment."""

    router_log_decisions = os.getenv("ROUTER_LOG_DECISIONS", "true").strip().lower() in _ENV_TRUTHY_VALUES
    return resolve_debug_profile_state(
        debug_selector=os.getenv("BLENDER_AI_DEBUG"),
        router_log_decisions=router_log_decisions,
        registry=registry,
    )


def debug_scope_enabled(
    scope_name: str,
    *,
    config: Any | None = None,
    registry: DebugProfileRegistry = DEFAULT_DEBUG_PROFILE_REGISTRY,
) -> bool:
    """Return whether one repo-owned debug scope should emit runtime logs."""

    normalized_scope = registry.require_scope(scope_name)
    state = (
        resolve_debug_profile_state_from_config(config, registry=registry)
        if config is not None
        else resolve_debug_profile_state_from_env(registry=registry)
    )
    return state.scope_enabled(normalized_scope, registry=registry)


def emit_debug_log(
    scope_name: str,
    logger: logging.Logger,
    message: str,
    *args: Any,
    level: int = logging.INFO,
    config: Any | None = None,
    registry: DebugProfileRegistry = DEFAULT_DEBUG_PROFILE_REGISTRY,
) -> None:
    """Emit one bounded repo-owned debug log only when the scope is enabled."""

    normalized_scope = registry.require_scope(scope_name)
    if not debug_scope_enabled(normalized_scope, config=config, registry=registry):
        return
    logger.log(level, f"[{normalized_scope.upper()}_DEBUG] {message}", *args)


def describe_debug_profile_state(config: Any | None = None) -> str:
    """Return one human-readable summary of the effective selector state."""

    state = (
        resolve_debug_profile_state_from_config(config)
        if config is not None
        else resolve_debug_profile_state_from_env()
    )
    if state.selector is None:
        requested = "unset"
    elif not state.selector:
        requested = "off"
    else:
        requested = ",".join(sorted(state.selector))
    enabled = ",".join(sorted(state.enabled_scopes)) or "none"
    return f"requested={requested} enabled={enabled}"


__all__ = [
    "DEFAULT_DEBUG_PROFILE_REGISTRY",
    "DebugProfileDefinition",
    "DebugProfileRegistry",
    "DebugProfileState",
    "debug_scope_enabled",
    "describe_debug_profile_state",
    "emit_debug_log",
    "parse_debug_selector",
    "resolve_debug_profile_state",
    "resolve_debug_profile_state_from_config",
    "resolve_debug_profile_state_from_env",
    "supported_debug_selector_values",
]
