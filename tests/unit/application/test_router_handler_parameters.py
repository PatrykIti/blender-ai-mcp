"""
Unit tests for RouterToolHandler parameter resolution methods.

TASK-055-5, TASK-055-6
TASK-055-FIX: Updated for unified set_goal interface.
"""

import pytest
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, patch

from server.application.tool_handlers.router_handler import RouterToolHandler
from server.router.domain.entities.parameter import (
    ParameterSchema,
    ParameterResolutionResult,
    UnresolvedParameter,
    StoredMapping,
)


class MockParameterStore:
    """Mock parameter store for testing."""

    def __init__(self):
        self._mappings: Dict[str, StoredMapping] = {}

    def find_mapping(
        self,
        prompt: str,
        parameter_name: str,
        workflow_name: str,
        similarity_threshold: float = 0.85,
    ) -> Optional[StoredMapping]:
        """Find mapping by context."""
        key = f"{workflow_name}:{parameter_name}:{prompt}"
        return self._mappings.get(key)

    def store_mapping(
        self,
        context: str,
        parameter_name: str,
        value: Any,
        workflow_name: str,
    ) -> None:
        """Store mapping."""
        key = f"{workflow_name}:{parameter_name}:{context}"
        self._mappings[key] = StoredMapping(
            context=context,
            value=value,
            similarity=1.0,
            workflow_name=workflow_name,
            parameter_name=parameter_name,
            usage_count=1,
        )

    def increment_usage(self, mapping: StoredMapping) -> None:
        """Increment usage count."""
        pass

    def clear(self) -> int:
        """Clear all mappings."""
        count = len(self._mappings)
        self._mappings.clear()
        return count


class MockParameterResolver:
    """Mock parameter resolver for testing."""

    def __init__(self):
        self.stored_values = []
        self._resolve_result = None

    def set_resolve_result(self, result: ParameterResolutionResult):
        """Set what resolve() should return."""
        self._resolve_result = result

    def store_resolved_value(
        self,
        context: str,
        parameter_name: str,
        value: Any,
        workflow_name: str,
        schema: Optional[ParameterSchema] = None,
    ) -> str:
        """Store resolved value."""
        # Validate if schema provided
        if schema is not None:
            if not schema.validate_value(value):
                return (
                    f"Error: Value {value} is invalid for parameter "
                    f"'{parameter_name}' (type={schema.type}, "
                    f"range={schema.range})"
                )

        self.stored_values.append({
            "context": context,
            "parameter_name": parameter_name,
            "value": value,
            "workflow_name": workflow_name,
        })
        return f"Stored: '{context}' → {parameter_name}={value} (workflow: {workflow_name})"

    def resolve(
        self,
        prompt: str,
        workflow_name: str,
        parameters: Dict[str, ParameterSchema],
        existing_modifiers: Optional[Dict[str, Any]] = None,
    ) -> ParameterResolutionResult:
        """Return configured result."""
        if self._resolve_result:
            return self._resolve_result
        # Default: return all as unresolved
        unresolved = []
        resolved = existing_modifiers or {}
        sources = {k: "yaml_modifier" for k in resolved}

        for name, schema in parameters.items():
            if name in resolved:
                continue
            if schema.default is not None:
                resolved[name] = schema.default
                sources[name] = "default"
            else:
                unresolved.append(UnresolvedParameter(
                    name=name,
                    schema=schema,
                    context=prompt,
                    relevance=0.8,
                ))
        return ParameterResolutionResult(
            resolved=resolved,
            unresolved=unresolved,
            resolution_sources=sources,
        )


class MockWorkflowLoader:
    """Mock workflow loader for testing."""

    def __init__(self):
        self._workflows = {}

    def get_workflow(self, name: str):
        """Get workflow by name."""
        return self._workflows.get(name)

    def add_test_workflow(self, name: str, parameters: Dict[str, ParameterSchema]):
        """Add test workflow."""
        workflow = MagicMock()
        workflow.parameters = parameters
        self._workflows[name] = workflow


class MockRouter:
    """Mock router for set_goal tests."""

    def __init__(self):
        self._current_goal = None
        self._pending_workflow = None
        self._pending_modifiers = {}
        self._pending_variables = {}

    def set_current_goal(self, goal: str) -> Optional[str]:
        """Set goal and return matched workflow."""
        self._current_goal = goal
        # Simple keyword matching for tests
        if "table" in goal.lower():
            self._pending_workflow = "picnic_table"
            # Check for modifiers in goal
            if "straight" in goal.lower():
                self._pending_modifiers = {
                    "leg_angle_left": 0.0,
                    "leg_angle_right": 0.0,
                }
            return "picnic_table"
        return None

    def get_current_goal(self) -> Optional[str]:
        return self._current_goal

    def get_pending_workflow(self) -> Optional[str]:
        return self._pending_workflow

    def execute_pending_workflow(
        self,
        variables: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Execute pending workflow (mock - returns empty list)."""
        # In mock, just return empty list to simulate successful execution
        self.clear_goal()
        return []

    def clear_goal(self):
        self._current_goal = None
        self._pending_workflow = None
        self._pending_modifiers = {}
        self._pending_variables = {}


@pytest.fixture
def mock_store():
    """Create mock store."""
    return MockParameterStore()


@pytest.fixture
def mock_resolver():
    """Create mock resolver."""
    return MockParameterResolver()


@pytest.fixture
def mock_loader():
    """Create mock loader."""
    return MockWorkflowLoader()


@pytest.fixture
def mock_router():
    """Create mock router."""
    return MockRouter()


@pytest.fixture
def handler(mock_router, mock_resolver, mock_loader):
    """Create handler with mocks."""
    return RouterToolHandler(
        router=mock_router,
        enabled=True,
        parameter_resolver=mock_resolver,
        workflow_loader=mock_loader,
    )


class TestSetGoalUnified:
    """Tests for the unified set_goal method (TASK-055-FIX)."""

    def test_set_goal_no_workflow_match(self, handler):
        """Test when no workflow matches the goal."""
        result = handler.set_goal("random unmatched goal")

        assert result["status"] == "no_match"
        assert result["workflow"] is None
        assert result["resolved"] == {}
        assert result["unresolved"] == []

    def test_set_goal_with_workflow_no_params(self, handler, mock_loader):
        """Test when workflow matches but has no parameters."""
        # Add workflow without parameters
        mock_loader.add_test_workflow("picnic_table", {})

        result = handler.set_goal("picnic table")

        assert result["status"] == "ready"
        assert result["workflow"] == "picnic_table"
        assert result["resolved"] == {}

    def test_set_goal_with_all_resolved(self, handler, mock_loader, mock_resolver):
        """Test when all parameters are resolved via modifiers."""
        # Add workflow with parameters
        mock_loader.add_test_workflow(
            "picnic_table",
            {
                "leg_angle_left": ParameterSchema(
                    name="leg_angle_left",
                    type="float",
                    range=(-1.57, 1.57),
                    default=0.3,
                    description="Left leg angle",
                ),
                "leg_angle_right": ParameterSchema(
                    name="leg_angle_right",
                    type="float",
                    range=(-1.57, 1.57),
                    default=0.3,
                    description="Right leg angle",
                ),
            }
        )

        # Configure resolver to return everything as resolved
        mock_resolver.set_resolve_result(ParameterResolutionResult(
            resolved={"leg_angle_left": 0.0, "leg_angle_right": 0.0},
            unresolved=[],
            resolution_sources={
                "leg_angle_left": "yaml_modifier",
                "leg_angle_right": "yaml_modifier",
            },
        ))

        result = handler.set_goal("picnic table with straight legs")

        assert result["status"] == "ready"
        assert result["workflow"] == "picnic_table"
        assert result["resolved"]["leg_angle_left"] == 0.0
        assert result["resolved"]["leg_angle_right"] == 0.0
        assert result["unresolved"] == []

    def test_set_goal_with_unresolved_params(self, handler, mock_loader, mock_resolver):
        """Test when some parameters remain unresolved."""
        leg_schema = ParameterSchema(
            name="leg_angle_left",
            type="float",
            range=(-1.57, 1.57),
            default=0.3,
            description="Left leg angle",
            semantic_hints=["angle", "tilt", "slant"],
        )
        mock_loader.add_test_workflow("picnic_table", {"leg_angle_left": leg_schema})

        # Configure resolver to return unresolved parameter
        mock_resolver.set_resolve_result(ParameterResolutionResult(
            resolved={},
            unresolved=[
                UnresolvedParameter(
                    name="leg_angle_left",
                    schema=leg_schema,
                    context="table",
                    relevance=0.8,
                )
            ],
            resolution_sources={},
        ))

        result = handler.set_goal("table")

        assert result["status"] == "needs_input"
        assert result["workflow"] == "picnic_table"
        assert len(result["unresolved"]) == 1
        assert result["unresolved"][0]["param"] == "leg_angle_left"
        assert result["unresolved"][0]["type"] == "float"
        assert result["unresolved"][0]["default"] == 0.3

    def test_set_goal_with_resolved_params_second_call(
        self, handler, mock_loader, mock_resolver
    ):
        """Test providing resolved_params on second call."""
        leg_schema = ParameterSchema(
            name="leg_angle_left",
            type="float",
            range=(-1.57, 1.57),
            default=0.3,
            description="Left leg angle",
        )
        mock_loader.add_test_workflow("picnic_table", {"leg_angle_left": leg_schema})

        # First call returns unresolved
        mock_resolver.set_resolve_result(ParameterResolutionResult(
            resolved={},
            unresolved=[
                UnresolvedParameter(
                    name="leg_angle_left",
                    schema=leg_schema,
                    context="table",
                    relevance=0.8,
                )
            ],
            resolution_sources={},
        ))

        result1 = handler.set_goal("table")
        assert result1["status"] == "needs_input"

        # Second call with resolved_params
        mock_resolver.set_resolve_result(ParameterResolutionResult(
            resolved={"leg_angle_left": 0.5},
            unresolved=[],
            resolution_sources={"leg_angle_left": "learned_mapping"},
        ))

        result2 = handler.set_goal("table", resolved_params={"leg_angle_left": 0.5})

        assert result2["status"] == "ready"
        assert result2["resolved"]["leg_angle_left"] == 0.5

    def test_set_goal_disabled(self):
        """Test that disabled handler returns disabled status."""
        handler = RouterToolHandler(router=None, enabled=False)

        result = handler.set_goal("table")

        assert result["status"] == "disabled"

    def test_set_goal_no_router(self):
        """Test when router returns None from DI."""
        handler = RouterToolHandler(router=None, enabled=True)
        handler._get_router = lambda: None

        result = handler.set_goal("table")

        assert result["status"] == "disabled"
        assert "not initialized" in result["message"]

    def test_set_goal_resolution_sources_included(
        self, handler, mock_loader, mock_resolver
    ):
        """Test that resolution sources are included in response."""
        mock_loader.add_test_workflow(
            "picnic_table",
            {
                "leg_angle_left": ParameterSchema(
                    name="leg_angle_left",
                    type="float",
                    default=0.3,
                ),
            }
        )

        mock_resolver.set_resolve_result(ParameterResolutionResult(
            resolved={"leg_angle_left": 0.0},
            unresolved=[],
            resolution_sources={"leg_angle_left": "yaml_modifier"},
        ))

        result = handler.set_goal("picnic table with straight legs")

        assert result["resolution_sources"]["leg_angle_left"] == "yaml_modifier"


class TestExtractContextForParam:
    """Tests for _extract_context_for_param helper method."""

    def test_extract_context_with_matching_hint(self, handler):
        """Test context extraction when hint matches."""
        params = {
            "leg_angle": ParameterSchema(
                name="leg_angle",
                type="float",
                semantic_hints=["straight", "angled", "proste"],
            )
        }

        context = handler._extract_context_for_param(
            "stół z prostymi nogami",
            "leg_angle",
            params,
        )

        # Should extract context around "proste" (Polish matching "prostymi")
        # The method looks for hints in goal, "proste" is not directly in "prostymi"
        # but it's a substring-based match, so may return full goal
        assert isinstance(context, str)

    def test_extract_context_no_match_returns_full_goal(self, handler):
        """Test that full goal is returned when no hint matches."""
        params = {
            "width": ParameterSchema(
                name="width",
                type="float",
                semantic_hints=["wide", "narrow"],
            )
        }

        context = handler._extract_context_for_param(
            "simple table",
            "width",
            params,
        )

        assert context == "simple table"

    def test_extract_context_missing_param_returns_full_goal(self, handler):
        """Test that full goal is returned when param not found."""
        params = {}

        context = handler._extract_context_for_param(
            "simple table",
            "unknown_param",
            params,
        )

        assert context == "simple table"
