"""
Unit tests for ParameterSchema enum validation.

Tests TASK-056-3: Enum constraints
"""

import pytest
from server.router.domain.entities.parameter import ParameterSchema


class TestEnumValidation:
    """Test TASK-056-3: Enum constraints."""

    def test_enum_field_exists(self):
        """Test that enum field can be set."""
        schema = ParameterSchema(
            name="color",
            type="string",
            enum=["red", "green", "blue"]
        )

        assert schema.enum == ["red", "green", "blue"]

    def test_enum_validation_success(self):
        """Test that valid enum values pass validation."""
        schema = ParameterSchema(
            name="color",
            type="string",
            enum=["red", "green", "blue"]
        )

        assert schema.validate_value("red") is True
        assert schema.validate_value("green") is True
        assert schema.validate_value("blue") is True

    def test_enum_validation_failure(self):
        """Test that invalid enum values fail validation."""
        schema = ParameterSchema(
            name="color",
            type="string",
            enum=["red", "green", "blue"]
        )

        assert schema.validate_value("yellow") is False
        assert schema.validate_value("purple") is False
        assert schema.validate_value("") is False

    def test_enum_with_numeric_values(self):
        """Test enum with numeric values."""
        schema = ParameterSchema(
            name="quality",
            type="int",
            enum=[1, 2, 3, 4, 5]
        )

        assert schema.validate_value(1) is True
        assert schema.validate_value(3) is True
        assert schema.validate_value(5) is True
        assert schema.validate_value(6) is False
        assert schema.validate_value(0) is False

    def test_enum_with_float_values(self):
        """Test enum with float values."""
        schema = ParameterSchema(
            name="angle",
            type="float",
            enum=[0.0, 0.25, 0.5, 0.75, 1.0]
        )

        assert schema.validate_value(0.0) is True
        assert schema.validate_value(0.5) is True
        assert schema.validate_value(1.0) is True
        assert schema.validate_value(0.3) is False

    def test_enum_empty_list_raises_error(self):
        """Test that empty enum list raises ValueError."""
        with pytest.raises(ValueError, match="Enum list cannot be empty"):
            ParameterSchema(
                name="empty",
                type="string",
                enum=[]
            )

    def test_enum_not_list_raises_error(self):
        """Test that non-list enum raises ValueError."""
        with pytest.raises(ValueError, match="Enum must be a list"):
            ParameterSchema(
                name="invalid",
                type="string",
                enum="not a list"
            )

    def test_enum_with_default_valid(self):
        """Test that default value must be in enum."""
        schema = ParameterSchema(
            name="size",
            type="string",
            enum=["small", "medium", "large"],
            default="medium"
        )

        assert schema.default == "medium"

    def test_enum_with_default_invalid_raises_error(self):
        """Test that invalid default raises ValueError."""
        with pytest.raises(ValueError, match="Default value .* must be in enum"):
            ParameterSchema(
                name="size",
                type="string",
                enum=["small", "medium", "large"],
                default="extra-large"
            )

    def test_enum_with_range(self):
        """Test that enum and range can coexist."""
        schema = ParameterSchema(
            name="quality",
            type="int",
            range=(1, 5),
            enum=[1, 2, 3, 4, 5]
        )

        # Must pass both range AND enum validation
        assert schema.validate_value(3) is True
        assert schema.validate_value(6) is False  # Outside range
        assert schema.validate_value(0) is False  # Outside enum

    def test_enum_none_means_no_restriction(self):
        """Test that enum=None means no enum restriction."""
        schema = ParameterSchema(
            name="text",
            type="string",
            enum=None
        )

        # Any string should be valid
        assert schema.validate_value("anything") is True
        assert schema.validate_value("goes") is True

    def test_enum_serialization(self):
        """Test that enum is included in to_dict."""
        schema = ParameterSchema(
            name="color",
            type="string",
            enum=["red", "green", "blue"]
        )

        data = schema.to_dict()

        assert "enum" in data
        assert data["enum"] == ["red", "green", "blue"]

    def test_enum_deserialization(self):
        """Test that enum is restored from from_dict."""
        data = {
            "name": "color",
            "type": "string",
            "enum": ["red", "green", "blue"]
        }

        schema = ParameterSchema.from_dict(data)

        assert schema.enum == ["red", "green", "blue"]
        assert schema.validate_value("red") is True
        assert schema.validate_value("yellow") is False

    def test_enum_in_question_dict(self):
        """Test that enum is included in question dictionary."""
        from server.router.domain.entities.parameter import UnresolvedParameter

        schema = ParameterSchema(
            name="mode",
            type="string",
            enum=["fast", "balanced", "quality"],
            description="Render mode"
        )

        unresolved = UnresolvedParameter(
            name="mode",
            schema=schema,
            context="render quality",
            relevance=0.8
        )

        question = unresolved.to_question_dict()

        assert "enum" in question
        assert question["enum"] == ["fast", "balanced", "quality"]


class TestEnumTypeCombinations:
    """Test enum with different parameter types."""

    def test_enum_with_bool_type(self):
        """Test enum with boolean type."""
        schema = ParameterSchema(
            name="flag",
            type="bool",
            enum=[True, False]
        )

        assert schema.validate_value(True) is True
        assert schema.validate_value(False) is True

    def test_enum_mixed_types_validation(self):
        """Test that enum validation respects type checking."""
        schema = ParameterSchema(
            name="value",
            type="int",
            enum=[1, 2, 3]
        )

        # Valid int in enum
        assert schema.validate_value(1) is True

        # String "1" should fail type validation even though 1 is in enum
        assert schema.validate_value("1") is False

    def test_enum_with_none_value(self):
        """Test enum containing None value."""
        schema = ParameterSchema(
            name="optional",
            type="string",
            enum=["a", "b", None]
        )

        # Note: This will fail because None isn't a string
        # Enum check happens first, but then type check fails
        # This documents current behavior
        assert schema.validate_value(None) is False
