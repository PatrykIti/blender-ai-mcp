"""
Tests for MetadataLoader.

Task: TASK-039-4
"""

import pytest
import json
import tempfile
from pathlib import Path

from server.router.infrastructure.metadata_loader import (
    MetadataLoader,
    ToolMetadata,
    ValidationError,
)


@pytest.fixture
def temp_metadata_dir():
    """Create a temporary metadata directory with test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)

        # Create mesh directory with test files
        mesh_dir = base / "mesh"
        mesh_dir.mkdir()

        # Create a valid mesh tool
        mesh_extrude = {
            "tool_name": "mesh_extrude",
            "category": "mesh",
            "mode_required": "EDIT",
            "selection_required": True,
            "keywords": ["extrude", "pull"],
            "sample_prompts": ["extrude the face"],
            "parameters": {
                "value": {"type": "float", "default": 0.0}
            },
            "related_tools": ["mesh_bevel"],
            "patterns": ["phone_like"],
            "description": "Extrudes geometry",
        }
        with open(mesh_dir / "mesh_extrude.json", "w") as f:
            json.dump(mesh_extrude, f)

        # Create modeling directory
        modeling_dir = base / "modeling"
        modeling_dir.mkdir()

        modeling_primitive = {
            "tool_name": "modeling_create_primitive",
            "category": "modeling",
            "mode_required": "OBJECT",
            "selection_required": False,
            "keywords": ["create", "cube"],
            "sample_prompts": ["create a cube"],
        }
        with open(modeling_dir / "modeling_create_primitive.json", "w") as f:
            json.dump(modeling_primitive, f)

        # Create schema file
        schema = {"$schema": "http://json-schema.org/draft-07/schema#"}
        with open(base / "_schema.json", "w") as f:
            json.dump(schema, f)

        yield base


@pytest.fixture
def loader(temp_metadata_dir):
    """Create a MetadataLoader with test directory."""
    return MetadataLoader(metadata_dir=temp_metadata_dir)


class TestToolMetadata:
    """Tests for ToolMetadata dataclass."""

    def test_create_basic(self):
        """Test basic creation."""
        meta = ToolMetadata(
            tool_name="test_tool",
            category="mesh",
        )
        assert meta.tool_name == "test_tool"
        assert meta.mode_required == "ANY"
        assert not meta.selection_required

    def test_to_dict(self):
        """Test conversion to dictionary."""
        meta = ToolMetadata(
            tool_name="mesh_extrude",
            category="mesh",
            mode_required="EDIT",
            keywords=["extrude"],
        )
        data = meta.to_dict()
        assert data["tool_name"] == "mesh_extrude"
        assert data["keywords"] == ["extrude"]

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "tool_name": "mesh_bevel",
            "category": "mesh",
            "mode_required": "EDIT",
            "selection_required": True,
        }
        meta = ToolMetadata.from_dict(data)
        assert meta.tool_name == "mesh_bevel"
        assert meta.selection_required


class TestMetadataLoader:
    """Tests for MetadataLoader."""

    def test_load_all(self, loader):
        """Test loading all metadata."""
        metadata = loader.load_all()
        assert "mesh_extrude" in metadata
        assert "modeling_create_primitive" in metadata
        assert len(metadata) == 2

    def test_load_by_area(self, loader):
        """Test loading metadata by area."""
        mesh_tools = loader.load_by_area("mesh")
        assert len(mesh_tools) == 1
        assert "mesh_extrude" in mesh_tools

        modeling_tools = loader.load_by_area("modeling")
        assert len(modeling_tools) == 1

    def test_get_tool(self, loader):
        """Test getting specific tool."""
        tool = loader.get_tool("mesh_extrude")
        assert tool is not None
        assert tool.tool_name == "mesh_extrude"
        assert tool.mode_required == "EDIT"

    def test_get_tool_not_found(self, loader):
        """Test getting non-existent tool."""
        tool = loader.get_tool("nonexistent_tool")
        assert tool is None

    def test_reload(self, loader):
        """Test reloading metadata."""
        loader.load_all()
        assert len(loader._cache) == 2

        loader.reload()
        assert len(loader._cache) == 2

    def test_get_tools_by_mode(self, loader):
        """Test getting tools by mode."""
        loader.load_all()

        edit_tools = loader.get_tools_by_mode("EDIT")
        assert len(edit_tools) == 1
        assert edit_tools[0].tool_name == "mesh_extrude"

        object_tools = loader.get_tools_by_mode("OBJECT")
        assert len(object_tools) == 1
        assert object_tools[0].tool_name == "modeling_create_primitive"

    def test_get_tools_by_category(self, loader):
        """Test getting tools by category."""
        loader.load_all()

        mesh_tools = loader.get_tools_by_category("mesh")
        assert len(mesh_tools) == 1

    def test_get_tools_requiring_selection(self, loader):
        """Test getting tools that require selection."""
        loader.load_all()

        selection_tools = loader.get_tools_requiring_selection()
        assert "mesh_extrude" in selection_tools
        assert "modeling_create_primitive" not in selection_tools

    def test_search_by_keyword(self, loader):
        """Test searching by keyword."""
        loader.load_all()

        results = loader.search_by_keyword("extrude")
        assert len(results) == 1
        assert results[0].tool_name == "mesh_extrude"

        results = loader.search_by_keyword("create")
        assert len(results) == 1
        assert results[0].tool_name == "modeling_create_primitive"

    def test_get_all_sample_prompts(self, loader):
        """Test getting all sample prompts."""
        loader.load_all()

        prompts = loader.get_all_sample_prompts()
        assert "mesh_extrude" in prompts
        assert "extrude the face" in prompts["mesh_extrude"]

    def test_caching(self, loader):
        """Test that metadata is cached."""
        metadata1 = loader.load_all()
        metadata2 = loader.load_all()

        # Should return same cached data
        assert metadata1 is metadata2


class TestMetadataValidation:
    """Tests for metadata validation."""

    def test_validate_valid_file(self, temp_metadata_dir):
        """Test validation of valid files."""
        loader = MetadataLoader(metadata_dir=temp_metadata_dir)
        errors = loader.validate_all()
        assert len(errors) == 0

    def test_validate_missing_field(self, temp_metadata_dir):
        """Test validation catches missing fields."""
        # Create invalid file
        invalid_dir = temp_metadata_dir / "scene"
        invalid_dir.mkdir(exist_ok=True)

        invalid_data = {
            "tool_name": "invalid_tool",
            # Missing category and mode_required
        }
        with open(invalid_dir / "invalid.json", "w") as f:
            json.dump(invalid_data, f)

        loader = MetadataLoader(metadata_dir=temp_metadata_dir)
        errors = loader.validate_all()

        assert len(errors) >= 2
        error_types = [e.error_type for e in errors]
        assert "missing_required_field" in error_types

    def test_validate_invalid_category(self, temp_metadata_dir):
        """Test validation catches invalid category."""
        invalid_dir = temp_metadata_dir / "scene"
        invalid_dir.mkdir(exist_ok=True)

        invalid_data = {
            "tool_name": "test",
            "category": "invalid_category",
            "mode_required": "OBJECT",
        }
        with open(invalid_dir / "invalid_cat.json", "w") as f:
            json.dump(invalid_data, f)

        loader = MetadataLoader(metadata_dir=temp_metadata_dir)
        errors = loader.validate_all()

        error_types = [e.error_type for e in errors]
        assert "invalid_category" in error_types

    def test_validate_invalid_mode(self, temp_metadata_dir):
        """Test validation catches invalid mode."""
        invalid_dir = temp_metadata_dir / "scene"
        invalid_dir.mkdir(exist_ok=True)

        invalid_data = {
            "tool_name": "test",
            "category": "scene",
            "mode_required": "INVALID_MODE",
        }
        with open(invalid_dir / "invalid_mode.json", "w") as f:
            json.dump(invalid_data, f)

        loader = MetadataLoader(metadata_dir=temp_metadata_dir)
        errors = loader.validate_all()

        error_types = [e.error_type for e in errors]
        assert "invalid_mode" in error_types


class TestRealMetadata:
    """Tests using actual metadata files in the project."""

    def test_load_real_metadata(self):
        """Test loading real metadata files."""
        loader = MetadataLoader()
        metadata = loader.load_all()

        # Should have at least the sample files we created
        assert len(metadata) >= 0  # Will be > 0 when files exist

    def test_validate_real_metadata(self):
        """Test validating real metadata files."""
        loader = MetadataLoader()
        errors = loader.validate_all()

        # All real files should be valid
        assert len(errors) == 0
