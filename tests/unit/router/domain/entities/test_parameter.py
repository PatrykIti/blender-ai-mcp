"""
Unit tests for Parameter Resolution Domain Entities.

TASK-055-1
"""

import pytest
from datetime import datetime

from server.router.domain.entities.parameter import (
    ParameterSchema,
    StoredMapping,
    UnresolvedParameter,
    ParameterResolutionResult,
)


class TestParameterSchema:
    """Tests for ParameterSchema dataclass."""

    def test_create_basic_schema(self):
        """Test creating a basic parameter schema."""
        schema = ParameterSchema(
            name="leg_angle",
            type="float",
            default=0.32,
            description="Rotation angle for table legs",
        )

        assert schema.name == "leg_angle"
        assert schema.type == "float"
        assert schema.default == 0.32
        assert schema.range is None
        assert schema.semantic_hints == []
        assert schema.group is None

    def test_create_schema_with_all_fields(self):
        """Test creating schema with all optional fields."""
        schema = ParameterSchema(
            name="leg_angle_left",
            type="float",
            range=(-1.57, 1.57),
            default=0.32,
            description="Left leg rotation",
            semantic_hints=["angle", "rotation", "nogi"],
            group="leg_angles",
        )

        assert schema.name == "leg_angle_left"
        assert schema.range == (-1.57, 1.57)
        assert schema.semantic_hints == ["angle", "rotation", "nogi"]
        assert schema.group == "leg_angles"

    def test_invalid_type_raises_error(self):
        """Test that invalid type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid parameter type"):
            ParameterSchema(name="test", type="invalid")

    def test_valid_types(self):
        """Test all valid parameter types."""
        for valid_type in ["float", "int", "bool", "string"]:
            schema = ParameterSchema(name="test", type=valid_type)
            assert schema.type == valid_type

    def test_invalid_range_length_raises_error(self):
        """Test that range with wrong length raises ValueError."""
        with pytest.raises(ValueError, match="must be a tuple of"):
            ParameterSchema(name="test", type="float", range=(0, 1, 2))

    def test_invalid_range_order_raises_error(self):
        """Test that range with min > max raises ValueError."""
        with pytest.raises(ValueError, match="min .* must be <= max"):
            ParameterSchema(name="test", type="float", range=(10, 5))

    def test_validate_value_float_in_range(self):
        """Test value validation for floats within range."""
        schema = ParameterSchema(
            name="angle",
            type="float",
            range=(-1.57, 1.57),
        )

        assert schema.validate_value(0.5) is True
        assert schema.validate_value(-1.57) is True
        assert schema.validate_value(1.57) is True
        assert schema.validate_value(0) is True  # int coerced to float

    def test_validate_value_float_out_of_range(self):
        """Test value validation for floats outside range."""
        schema = ParameterSchema(
            name="angle",
            type="float",
            range=(-1.57, 1.57),
        )

        assert schema.validate_value(5.0) is False
        assert schema.validate_value(-5.0) is False

    def test_validate_value_float_no_range(self):
        """Test value validation for floats without range."""
        schema = ParameterSchema(name="scale", type="float")

        assert schema.validate_value(100.0) is True
        assert schema.validate_value(-100.0) is True
        assert schema.validate_value("string") is False

    def test_validate_value_int(self):
        """Test value validation for integers."""
        schema = ParameterSchema(
            name="count",
            type="int",
            range=(0, 10),
        )

        assert schema.validate_value(5) is True
        assert schema.validate_value(0) is True
        assert schema.validate_value(10) is True
        assert schema.validate_value(15) is False
        assert schema.validate_value(5.5) is False
        assert schema.validate_value(True) is False  # bool is not int

    def test_validate_value_bool(self):
        """Test value validation for booleans."""
        schema = ParameterSchema(name="enabled", type="bool")

        assert schema.validate_value(True) is True
        assert schema.validate_value(False) is True
        assert schema.validate_value(1) is False
        assert schema.validate_value("true") is False

    def test_validate_value_string(self):
        """Test value validation for strings."""
        schema = ParameterSchema(name="name", type="string")

        assert schema.validate_value("hello") is True
        assert schema.validate_value("") is True
        assert schema.validate_value(123) is False

    def test_to_dict(self):
        """Test conversion to dictionary."""
        schema = ParameterSchema(
            name="angle",
            type="float",
            range=(-1.57, 1.57),
            default=0.0,
            description="Angle in radians",
            semantic_hints=["angle"],
            group="angles",
        )

        result = schema.to_dict()

        assert result["name"] == "angle"
        assert result["type"] == "float"
        assert result["range"] == [-1.57, 1.57]
        assert result["default"] == 0.0
        assert result["description"] == "Angle in radians"
        assert result["semantic_hints"] == ["angle"]
        assert result["group"] == "angles"

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "name": "scale",
            "type": "float",
            "range": [0.1, 10.0],
            "default": 1.0,
            "description": "Scale factor",
            "semantic_hints": ["size", "scale"],
            "group": "transform",
        }

        schema = ParameterSchema.from_dict(data)

        assert schema.name == "scale"
        assert schema.type == "float"
        assert schema.range == (0.1, 10.0)
        assert schema.default == 1.0
        assert schema.semantic_hints == ["size", "scale"]

    def test_from_dict_minimal(self):
        """Test creation from minimal dictionary."""
        data = {"name": "flag"}

        schema = ParameterSchema.from_dict(data)

        assert schema.name == "flag"
        assert schema.type == "float"  # default
        assert schema.range is None
        assert schema.default is None


class TestStoredMapping:
    """Tests for StoredMapping dataclass."""

    def test_create_basic_mapping(self):
        """Test creating a basic stored mapping."""
        mapping = StoredMapping(
            context="prostymi nogami",
            value=0,
            similarity=0.92,
            workflow_name="picnic_table",
            parameter_name="leg_angle_left",
        )

        assert mapping.context == "prostymi nogami"
        assert mapping.value == 0
        assert mapping.similarity == 0.92
        assert mapping.usage_count == 1
        assert mapping.created_at is None

    def test_create_mapping_with_all_fields(self):
        """Test creating mapping with all fields."""
        now = datetime.now()
        mapping = StoredMapping(
            context="straight legs",
            value=0.0,
            similarity=0.95,
            workflow_name="table",
            parameter_name="angle",
            usage_count=5,
            created_at=now,
        )

        assert mapping.usage_count == 5
        assert mapping.created_at == now

    def test_empty_context_raises_error(self):
        """Test that empty context raises ValueError."""
        with pytest.raises(ValueError, match="Context cannot be empty"):
            StoredMapping(
                context="",
                value=0,
                similarity=0.9,
                workflow_name="test",
                parameter_name="param",
            )

    def test_invalid_similarity_raises_error(self):
        """Test that invalid similarity raises ValueError."""
        with pytest.raises(ValueError, match="Similarity must be between"):
            StoredMapping(
                context="test",
                value=0,
                similarity=1.5,
                workflow_name="test",
                parameter_name="param",
            )

        with pytest.raises(ValueError, match="Similarity must be between"):
            StoredMapping(
                context="test",
                value=0,
                similarity=-0.1,
                workflow_name="test",
                parameter_name="param",
            )

    def test_empty_workflow_name_raises_error(self):
        """Test that empty workflow name raises ValueError."""
        with pytest.raises(ValueError, match="Workflow name cannot be empty"):
            StoredMapping(
                context="test",
                value=0,
                similarity=0.9,
                workflow_name="",
                parameter_name="param",
            )

    def test_empty_parameter_name_raises_error(self):
        """Test that empty parameter name raises ValueError."""
        with pytest.raises(ValueError, match="Parameter name cannot be empty"):
            StoredMapping(
                context="test",
                value=0,
                similarity=0.9,
                workflow_name="test",
                parameter_name="",
            )

    def test_to_dict(self):
        """Test conversion to dictionary."""
        now = datetime.now()
        mapping = StoredMapping(
            context="test context",
            value=0.5,
            similarity=0.88,
            workflow_name="workflow",
            parameter_name="param",
            usage_count=3,
            created_at=now,
        )

        result = mapping.to_dict()

        assert result["context"] == "test context"
        assert result["value"] == 0.5
        assert result["similarity"] == 0.88
        assert result["usage_count"] == 3
        assert result["created_at"] == now.isoformat()

    def test_to_dict_without_created_at(self):
        """Test to_dict when created_at is None."""
        mapping = StoredMapping(
            context="test",
            value=1,
            similarity=0.9,
            workflow_name="wf",
            parameter_name="p",
        )

        result = mapping.to_dict()
        assert result["created_at"] is None


class TestUnresolvedParameter:
    """Tests for UnresolvedParameter dataclass."""

    def test_create_unresolved_parameter(self):
        """Test creating an unresolved parameter."""
        schema = ParameterSchema(
            name="angle",
            type="float",
            range=(-1.57, 1.57),
            default=0,
            description="Rotation angle",
        )

        unresolved = UnresolvedParameter(
            name="angle",
            schema=schema,
            context="z pochylonymi nogami",
            relevance=0.72,
        )

        assert unresolved.name == "angle"
        assert unresolved.schema == schema
        assert unresolved.context == "z pochylonymi nogami"
        assert unresolved.relevance == 0.72

    def test_invalid_relevance_raises_error(self):
        """Test that invalid relevance raises ValueError."""
        schema = ParameterSchema(name="test", type="float")

        with pytest.raises(ValueError, match="Relevance must be between"):
            UnresolvedParameter(
                name="test",
                schema=schema,
                context="test",
                relevance=1.5,
            )

    def test_to_question_dict(self):
        """Test conversion to question format."""
        schema = ParameterSchema(
            name="leg_angle",
            type="float",
            range=(-1.57, 1.57),
            default=0.32,
            description="Table leg rotation angle",
            group="leg_angles",
        )

        unresolved = UnresolvedParameter(
            name="leg_angle",
            schema=schema,
            context="straight legs",
            relevance=0.8,
        )

        question = unresolved.to_question_dict()

        assert question["parameter"] == "leg_angle"
        assert question["context"] == "straight legs"
        assert question["description"] == "Table leg rotation angle"
        assert question["range"] == [-1.57, 1.57]
        assert question["default"] == 0.32
        assert question["type"] == "float"
        assert question["group"] == "leg_angles"


class TestParameterResolutionResult:
    """Tests for ParameterResolutionResult dataclass."""

    def test_create_empty_result(self):
        """Test creating an empty resolution result."""
        result = ParameterResolutionResult()

        assert result.resolved == {}
        assert result.unresolved == []
        assert result.resolution_sources == {}
        assert result.is_complete is True
        assert result.needs_llm_input is False

    def test_create_fully_resolved_result(self):
        """Test creating a fully resolved result."""
        result = ParameterResolutionResult(
            resolved={
                "leg_angle_left": 0,
                "leg_angle_right": 0,
            },
            unresolved=[],
            resolution_sources={
                "leg_angle_left": "yaml_modifier",
                "leg_angle_right": "yaml_modifier",
            },
        )

        assert result.is_complete is True
        assert result.needs_llm_input is False
        assert len(result.resolved) == 2

    def test_create_partially_resolved_result(self):
        """Test creating result with unresolved parameters."""
        schema = ParameterSchema(
            name="angle",
            type="float",
            default=0,
        )

        unresolved = UnresolvedParameter(
            name="angle",
            schema=schema,
            context="test",
            relevance=0.7,
        )

        result = ParameterResolutionResult(
            resolved={"width": 1.0},
            unresolved=[unresolved],
            resolution_sources={"width": "default"},
        )

        assert result.is_complete is False
        assert result.needs_llm_input is True
        assert len(result.unresolved) == 1

    def test_get_questions(self):
        """Test getting questions for LLM interaction."""
        schema1 = ParameterSchema(
            name="angle",
            type="float",
            range=(0, 1),
            description="First param",
        )
        schema2 = ParameterSchema(
            name="scale",
            type="float",
            description="Second param",
        )

        result = ParameterResolutionResult(
            unresolved=[
                UnresolvedParameter(
                    name="angle",
                    schema=schema1,
                    context="ctx1",
                    relevance=0.8,
                ),
                UnresolvedParameter(
                    name="scale",
                    schema=schema2,
                    context="ctx2",
                    relevance=0.6,
                ),
            ],
        )

        questions = result.get_questions()

        assert len(questions) == 2
        assert questions[0]["parameter"] == "angle"
        assert questions[1]["parameter"] == "scale"

    def test_to_dict(self):
        """Test conversion to dictionary."""
        schema = ParameterSchema(
            name="test",
            type="float",
            default=0,
        )

        result = ParameterResolutionResult(
            resolved={"width": 1.0},
            unresolved=[
                UnresolvedParameter(
                    name="test",
                    schema=schema,
                    context="ctx",
                    relevance=0.7,
                ),
            ],
            resolution_sources={"width": "default"},
        )

        data = result.to_dict()

        assert data["resolved"] == {"width": 1.0}
        assert data["resolution_sources"] == {"width": "default"}
        assert data["needs_llm_input"] is True
        assert data["is_complete"] is False
        assert len(data["unresolved"]) == 1
        assert data["unresolved"][0]["name"] == "test"
