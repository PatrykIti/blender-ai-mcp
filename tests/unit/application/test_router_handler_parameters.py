"""
Unit tests for RouterToolHandler parameter resolution methods.

TASK-055-5, TASK-055-6
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

    def list_mappings(
        self,
        workflow_name: Optional[str] = None,
        parameter_name: Optional[str] = None,
    ) -> List[StoredMapping]:
        """List mappings with optional filtering."""
        result = []
        for mapping in self._mappings.values():
            if workflow_name and mapping.workflow_name != workflow_name:
                continue
            if parameter_name and mapping.parameter_name != parameter_name:
                continue
            result.append(mapping)
        return result

    def delete_mapping(
        self,
        context: str,
        parameter_name: str,
        workflow_name: str,
    ) -> bool:
        """Delete mapping."""
        key = f"{workflow_name}:{parameter_name}:{context}"
        if key in self._mappings:
            del self._mappings[key]
            return True
        return False

    def add_test_mapping(
        self,
        context: str,
        parameter_name: str,
        value: Any,
        workflow_name: str,
    ):
        """Add test mapping."""
        key = f"{workflow_name}:{parameter_name}:{context}"
        self._mappings[key] = StoredMapping(
            context=context,
            value=value,
            similarity=1.0,
            workflow_name=workflow_name,
            parameter_name=parameter_name,
            usage_count=1,
        )


class MockParameterResolver:
    """Mock parameter resolver for testing."""

    def __init__(self):
        self.stored_values = []

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
def handler(mock_store, mock_resolver, mock_loader):
    """Create handler with mocks."""
    handler = RouterToolHandler(router=None, enabled=True)

    # Patch the getter methods
    handler._get_parameter_store = lambda: mock_store
    handler._get_parameter_resolver = lambda: mock_resolver
    handler._get_workflow_loader = lambda: mock_loader

    return handler


class TestStoreParameterValue:
    """Tests for store_parameter_value method."""

    def test_store_simple_value(self, handler, mock_resolver):
        """Test storing a simple parameter value."""
        result = handler.store_parameter_value(
            context="straight legs",
            parameter_name="leg_angle",
            value=0.0,
            workflow_name="table",
        )

        assert "Stored" in result
        assert "leg_angle=0.0" in result
        assert len(mock_resolver.stored_values) == 1
        assert mock_resolver.stored_values[0]["context"] == "straight legs"
        assert mock_resolver.stored_values[0]["value"] == 0.0

    def test_store_with_schema_validation(self, handler, mock_resolver, mock_loader):
        """Test storing value with schema validation."""
        # Add workflow with parameter schema
        mock_loader.add_test_workflow(
            "table",
            {
                "leg_angle": ParameterSchema(
                    name="leg_angle",
                    type="float",
                    range=(-1.57, 1.57),
                )
            }
        )

        result = handler.store_parameter_value(
            context="straight legs",
            parameter_name="leg_angle",
            value=0.5,  # Within range
            workflow_name="table",
        )

        assert "Stored" in result

    def test_store_returns_error_when_disabled(self, mock_resolver):
        """Test that disabled handler returns error."""
        handler = RouterToolHandler(router=None, enabled=False)

        result = handler.store_parameter_value(
            context="test",
            parameter_name="param",
            value=1.0,
            workflow_name="wf",
        )

        assert "disabled" in result.lower()


class TestListParameterMappings:
    """Tests for list_parameter_mappings method."""

    def test_list_empty(self, handler):
        """Test listing when no mappings exist."""
        result = handler.list_parameter_mappings()

        assert "No parameter mappings stored yet" in result

    def test_list_with_mappings(self, handler, mock_store):
        """Test listing existing mappings."""
        mock_store.add_test_mapping(
            context="straight legs",
            parameter_name="leg_angle",
            value=0.0,
            workflow_name="table",
        )
        mock_store.add_test_mapping(
            context="wide table",
            parameter_name="top_width",
            value=2.5,
            workflow_name="table",
        )

        result = handler.list_parameter_mappings()

        assert "Total mappings: 2" in result
        assert "table" in result
        assert "straight legs" in result
        assert "leg_angle=0.0" in result

    def test_list_filtered_by_workflow(self, handler, mock_store):
        """Test listing filtered by workflow."""
        mock_store.add_test_mapping(
            context="test",
            parameter_name="param",
            value=1.0,
            workflow_name="workflow_a",
        )
        mock_store.add_test_mapping(
            context="test2",
            parameter_name="param2",
            value=2.0,
            workflow_name="workflow_b",
        )

        result = handler.list_parameter_mappings(workflow_name="workflow_a")

        assert "workflow_a" in result
        # Should filter properly
        assert "Total mappings: 1" in result

    def test_list_returns_error_when_disabled(self):
        """Test that disabled handler returns error."""
        handler = RouterToolHandler(router=None, enabled=False)

        result = handler.list_parameter_mappings()

        assert "disabled" in result.lower()


class TestDeleteParameterMapping:
    """Tests for delete_parameter_mapping method."""

    def test_delete_existing_mapping(self, handler, mock_store):
        """Test deleting an existing mapping."""
        mock_store.add_test_mapping(
            context="straight legs",
            parameter_name="leg_angle",
            value=0.0,
            workflow_name="table",
        )

        result = handler.delete_parameter_mapping(
            context="straight legs",
            parameter_name="leg_angle",
            workflow_name="table",
        )

        assert "Deleted" in result

    def test_delete_nonexistent_mapping(self, handler, mock_store):
        """Test deleting a mapping that doesn't exist."""
        result = handler.delete_parameter_mapping(
            context="nonexistent",
            parameter_name="param",
            workflow_name="wf",
        )

        assert "not found" in result.lower()

    def test_delete_returns_error_when_disabled(self):
        """Test that disabled handler returns error."""
        handler = RouterToolHandler(router=None, enabled=False)

        result = handler.delete_parameter_mapping(
            context="test",
            parameter_name="param",
            workflow_name="wf",
        )

        assert "disabled" in result.lower()


class TestRouterHandlerIntegration:
    """Integration tests for handler methods."""

    def test_store_and_list_flow(self, handler, mock_store, mock_resolver):
        """Test storing and then listing mappings."""
        # Store a value
        store_result = handler.store_parameter_value(
            context="prostymi nogami",  # Polish
            parameter_name="leg_angle_left",
            value=0.0,
            workflow_name="picnic_table",
        )

        assert "Stored" in store_result

        # Add to mock store for listing (since resolver doesn't add to store)
        mock_store.add_test_mapping(
            context="prostymi nogami",
            parameter_name="leg_angle_left",
            value=0.0,
            workflow_name="picnic_table",
        )

        # List mappings
        list_result = handler.list_parameter_mappings()

        assert "picnic_table" in list_result
        assert "prostymi nogami" in list_result


class MockRouter:
    """Mock router for set_goal_interactive tests."""

    def __init__(self):
        self._current_goal = None
        self._pending_workflow = None
        self._pending_modifiers = {}

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

    def clear_goal(self):
        self._current_goal = None
        self._pending_workflow = None
        self._pending_modifiers = {}


class MockParameterResolverWithResolve(MockParameterResolver):
    """Extended mock resolver with resolve method for set_goal_interactive."""

    def __init__(self):
        super().__init__()
        self._resolve_result = None

    def set_resolve_result(self, result: ParameterResolutionResult):
        """Set what resolve() should return."""
        self._resolve_result = result

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
        for name, schema in parameters.items():
            if existing_modifiers and name in existing_modifiers:
                continue
            unresolved.append(UnresolvedParameter(
                name=name,
                schema=schema,
                context=prompt,
                relevance=0.8,
            ))
        return ParameterResolutionResult(
            resolved=existing_modifiers or {},
            unresolved=unresolved,
            resolution_sources={k: "yaml_modifier" for k in (existing_modifiers or {})},
        )


class TestSetGoalInteractive:
    """Tests for set_goal_interactive method (TASK-055-6)."""

    @pytest.fixture
    def mock_router(self):
        """Create mock router."""
        return MockRouter()

    @pytest.fixture
    def mock_resolver_ext(self):
        """Create extended mock resolver."""
        return MockParameterResolverWithResolve()

    @pytest.fixture
    def handler_with_router(self, mock_router, mock_resolver_ext, mock_loader):
        """Create handler with mock router."""
        handler = RouterToolHandler(router=mock_router, enabled=True)
        handler._get_parameter_resolver = lambda: mock_resolver_ext
        handler._get_workflow_loader = lambda: mock_loader
        return handler

    def test_set_goal_interactive_no_workflow_match(self, handler_with_router):
        """Test when no workflow matches the goal."""
        result = handler_with_router.set_goal_interactive("random unmatched goal")

        assert result["workflow_name"] is None
        assert result["resolved_parameters"] == {}
        assert result["unresolved_parameters"] == []
        assert "No workflow matched" in result.get("message", "")

    def test_set_goal_interactive_with_workflow_no_params(
        self, handler_with_router, mock_loader
    ):
        """Test when workflow matches but has no parameters."""
        # Add workflow without parameters
        mock_loader.add_test_workflow("picnic_table", {})

        result = handler_with_router.set_goal_interactive("picnic table")

        assert result["workflow_name"] == "picnic_table"
        assert result["resolved_parameters"] == {}
        assert "no interactive parameters" in result.get("message", "").lower()

    def test_set_goal_interactive_with_modifiers_from_goal(
        self, handler_with_router, mock_loader, mock_resolver_ext
    ):
        """Test when modifiers are extracted from goal text."""
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
        mock_resolver_ext.set_resolve_result(ParameterResolutionResult(
            resolved={"leg_angle_left": 0.0, "leg_angle_right": 0.0},
            unresolved=[],
            resolution_sources={
                "leg_angle_left": "yaml_modifier",
                "leg_angle_right": "yaml_modifier",
            },
        ))

        result = handler_with_router.set_goal_interactive(
            "picnic table with straight legs"
        )

        assert result["workflow_name"] == "picnic_table"
        assert result["is_complete"] is True
        assert result["needs_llm_input"] is False
        assert "leg_angle_left" in result["resolved_parameters"]

    def test_set_goal_interactive_with_unresolved_params(
        self, handler_with_router, mock_loader, mock_resolver_ext
    ):
        """Test when some parameters remain unresolved."""
        # Add workflow with parameters
        leg_schema = ParameterSchema(
            name="leg_angle_left",
            type="float",
            range=(-1.57, 1.57),
            default=0.3,
            description="Left leg angle",
            semantic_hints=["angle", "tilt", "slant"],
        )
        mock_loader.add_test_workflow(
            "picnic_table",
            {"leg_angle_left": leg_schema}
        )

        # Configure resolver to return unresolved parameter
        mock_resolver_ext.set_resolve_result(ParameterResolutionResult(
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

        result = handler_with_router.set_goal_interactive("table")

        assert result["workflow_name"] == "picnic_table"
        assert result["needs_llm_input"] is True
        assert result["is_complete"] is False
        assert len(result["unresolved_parameters"]) == 1

        unresolved = result["unresolved_parameters"][0]
        assert unresolved["name"] == "leg_angle_left"
        assert unresolved["type"] == "float"
        assert unresolved["description"] == "Left leg angle"
        assert unresolved["default"] == 0.3

    def test_set_goal_interactive_formatted_output(
        self, handler_with_router, mock_loader, mock_resolver_ext
    ):
        """Test formatted output for set_goal_interactive."""
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
            }
        )

        # Configure resolver
        mock_resolver_ext.set_resolve_result(ParameterResolutionResult(
            resolved={"leg_angle_left": 0.0},
            unresolved=[],
            resolution_sources={"leg_angle_left": "yaml_modifier"},
        ))

        result = handler_with_router.set_goal_interactive_formatted(
            "picnic table with straight legs"
        )

        assert "Matched workflow: picnic_table" in result
        assert "Resolved parameters:" in result
        assert "leg_angle_left = 0.0" in result
        assert "yaml_modifier" in result
        assert "All parameters resolved!" in result

    def test_set_goal_interactive_disabled(self):
        """Test that disabled handler returns error."""
        handler = RouterToolHandler(router=None, enabled=False)

        result = handler.set_goal_interactive("table")

        assert "error" in result
        assert "disabled" in result["error"].lower()

    def test_set_goal_interactive_no_router(self):
        """Test when router returns None from DI."""
        handler = RouterToolHandler(router=None, enabled=True)
        # Mock _get_router to return None (simulating disabled router in config)
        handler._get_router = lambda: None

        result = handler.set_goal_interactive("table")

        assert "error" in result
        assert "not initialized" in result["error"].lower()
