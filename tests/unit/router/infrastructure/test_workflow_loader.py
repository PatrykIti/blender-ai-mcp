"""
Unit tests for WorkflowLoader.

Tests for loading custom workflows from YAML/JSON files.
TASK-039-22
"""

import json
import tempfile
from pathlib import Path

import pytest

from server.router.infrastructure.workflow_loader import (
    WorkflowLoader,
    WorkflowValidationError,
    get_workflow_loader,
)
from server.router.application.workflows.base import WorkflowDefinition


class TestWorkflowLoader:
    """Tests for WorkflowLoader."""

    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Create a temporary directory for workflow files."""
        return tmp_path

    @pytest.fixture
    def loader(self, temp_dir):
        """Create a loader with temporary directory."""
        return WorkflowLoader(workflows_dir=temp_dir)

    def test_init_with_custom_dir(self, temp_dir):
        """Test initializing loader with custom directory."""
        loader = WorkflowLoader(workflows_dir=temp_dir)
        assert loader.workflows_dir == temp_dir

    def test_init_with_default_dir(self):
        """Test initializing loader with default directory."""
        loader = WorkflowLoader()
        assert "custom" in str(loader.workflows_dir)

    def test_load_all_empty_dir(self, loader, temp_dir):
        """Test loading from empty directory."""
        workflows = loader.load_all()
        assert workflows == {}

    def test_load_all_nonexistent_dir(self, tmp_path):
        """Test loading from non-existent directory."""
        loader = WorkflowLoader(workflows_dir=tmp_path / "nonexistent")
        workflows = loader.load_all()
        assert workflows == {}

    def test_load_json_file(self, loader, temp_dir):
        """Test loading a JSON workflow file."""
        workflow_data = {
            "name": "json_workflow",
            "description": "Test JSON workflow",
            "steps": [
                {"tool": "test_tool", "params": {"x": 1}},
            ],
        }

        file_path = temp_dir / "test_workflow.json"
        file_path.write_text(json.dumps(workflow_data))

        workflow = loader.load_file(file_path)

        assert workflow.name == "json_workflow"
        assert workflow.description == "Test JSON workflow"
        assert len(workflow.steps) == 1
        assert workflow.steps[0].tool == "test_tool"

    def test_load_json_with_all_fields(self, loader, temp_dir):
        """Test loading JSON with all optional fields."""
        workflow_data = {
            "name": "full_workflow",
            "description": "Full workflow",
            "category": "test",
            "author": "tester",
            "version": "2.0.0",
            "trigger_pattern": "test_pattern",
            "trigger_keywords": ["test", "example"],
            "steps": [
                {
                    "tool": "tool1",
                    "params": {"a": 1},
                    "description": "Step one",
                },
            ],
        }

        file_path = temp_dir / "full.json"
        file_path.write_text(json.dumps(workflow_data))

        workflow = loader.load_file(file_path)

        assert workflow.category == "test"
        assert workflow.author == "tester"
        assert workflow.version == "2.0.0"
        assert workflow.trigger_pattern == "test_pattern"
        assert workflow.trigger_keywords == ["test", "example"]
        assert workflow.steps[0].description == "Step one"

    def test_load_yaml_file(self, loader, temp_dir):
        """Test loading a YAML workflow file."""
        pytest.importorskip("yaml")

        yaml_content = """
name: yaml_workflow
description: Test YAML workflow
steps:
  - tool: yaml_tool
    params:
      value: 42
"""
        file_path = temp_dir / "test_workflow.yaml"
        file_path.write_text(yaml_content)

        workflow = loader.load_file(file_path)

        assert workflow.name == "yaml_workflow"
        assert len(workflow.steps) == 1
        assert workflow.steps[0].params["value"] == 42

    def test_load_yml_extension(self, loader, temp_dir):
        """Test loading file with .yml extension."""
        pytest.importorskip("yaml")

        yaml_content = """
name: yml_workflow
description: YML extension test
steps:
  - tool: test
    params: {}
"""
        file_path = temp_dir / "test.yml"
        file_path.write_text(yaml_content)

        workflow = loader.load_file(file_path)
        assert workflow.name == "yml_workflow"

    def test_load_file_not_found(self, loader, temp_dir):
        """Test loading non-existent file raises error."""
        with pytest.raises(FileNotFoundError):
            loader.load_file(temp_dir / "nonexistent.json")

    def test_load_unsupported_format(self, loader, temp_dir):
        """Test loading unsupported file format."""
        file_path = temp_dir / "test.txt"
        file_path.write_text("not a workflow")

        with pytest.raises(ValueError, match="Unsupported file format"):
            loader.load_file(file_path)

    def test_validation_missing_name(self, loader, temp_dir):
        """Test validation fails without name."""
        workflow_data = {
            "steps": [{"tool": "t", "params": {}}],
        }

        file_path = temp_dir / "invalid.json"
        file_path.write_text(json.dumps(workflow_data))

        with pytest.raises(WorkflowValidationError, match="name"):
            loader.load_file(file_path)

    def test_validation_missing_steps(self, loader, temp_dir):
        """Test validation fails without steps."""
        workflow_data = {
            "name": "no_steps",
        }

        file_path = temp_dir / "invalid.json"
        file_path.write_text(json.dumps(workflow_data))

        with pytest.raises(WorkflowValidationError, match="steps"):
            loader.load_file(file_path)

    def test_validation_empty_steps(self, loader, temp_dir):
        """Test validation fails with empty steps."""
        workflow_data = {
            "name": "empty_steps",
            "steps": [],
        }

        file_path = temp_dir / "invalid.json"
        file_path.write_text(json.dumps(workflow_data))

        with pytest.raises(WorkflowValidationError, match="at least one step"):
            loader.load_file(file_path)

    def test_validation_step_missing_tool(self, loader, temp_dir):
        """Test validation fails when step missing tool."""
        workflow_data = {
            "name": "bad_step",
            "steps": [{"params": {}}],
        }

        file_path = temp_dir / "invalid.json"
        file_path.write_text(json.dumps(workflow_data))

        with pytest.raises(WorkflowValidationError, match="tool"):
            loader.load_file(file_path)

    def test_load_all_multiple_files(self, loader, temp_dir):
        """Test loading multiple workflow files."""
        # Create JSON file
        json_data = {
            "name": "workflow_1",
            "steps": [{"tool": "t1", "params": {}}],
        }
        (temp_dir / "w1.json").write_text(json.dumps(json_data))

        # Create another JSON file
        json_data2 = {
            "name": "workflow_2",
            "steps": [{"tool": "t2", "params": {}}],
        }
        (temp_dir / "w2.json").write_text(json.dumps(json_data2))

        workflows = loader.load_all()

        assert len(workflows) == 2
        assert "workflow_1" in workflows
        assert "workflow_2" in workflows

    def test_reload(self, loader, temp_dir):
        """Test reloading workflows."""
        # Initial load
        json_data = {
            "name": "initial",
            "steps": [{"tool": "t", "params": {}}],
        }
        (temp_dir / "w.json").write_text(json.dumps(json_data))

        workflows = loader.load_all()
        assert "initial" in workflows

        # Modify file
        json_data["name"] = "updated"
        (temp_dir / "w.json").write_text(json.dumps(json_data))

        # Reload
        workflows = loader.reload()
        assert "updated" in workflows
        assert "initial" not in workflows

    def test_get_workflow(self, loader, temp_dir):
        """Test getting workflow by name."""
        json_data = {
            "name": "get_test",
            "steps": [{"tool": "t", "params": {}}],
        }
        (temp_dir / "w.json").write_text(json.dumps(json_data))

        # First call triggers load
        workflow = loader.get_workflow("get_test")

        assert workflow is not None
        assert workflow.name == "get_test"

    def test_get_workflow_not_found(self, loader, temp_dir):
        """Test getting non-existent workflow."""
        workflow = loader.get_workflow("nonexistent")
        assert workflow is None

    def test_validate_workflow_data_valid(self, loader):
        """Test validating valid workflow data."""
        data = {
            "name": "valid",
            "steps": [{"tool": "t", "params": {}}],
        }

        errors = loader.validate_workflow_data(data)
        assert errors == []

    def test_validate_workflow_data_missing_name(self, loader):
        """Test validation catches missing name."""
        data = {
            "steps": [{"tool": "t", "params": {}}],
        }

        errors = loader.validate_workflow_data(data)
        assert any("name" in e for e in errors)

    def test_validate_workflow_data_empty_name(self, loader):
        """Test validation catches empty name."""
        data = {
            "name": "   ",
            "steps": [{"tool": "t", "params": {}}],
        }

        errors = loader.validate_workflow_data(data)
        assert any("non-empty" in e for e in errors)

    def test_validate_workflow_data_name_with_spaces(self, loader):
        """Test validation warns about spaces in name."""
        data = {
            "name": "my workflow",
            "steps": [{"tool": "t", "params": {}}],
        }

        errors = loader.validate_workflow_data(data)
        assert any("spaces" in e for e in errors)

    def test_validate_workflow_data_invalid_params(self, loader):
        """Test validation catches invalid params."""
        data = {
            "name": "test",
            "steps": [{"tool": "t", "params": "not a dict"}],
        }

        errors = loader.validate_workflow_data(data)
        assert any("dictionary" in e for e in errors)

    def test_create_workflow_template(self, loader):
        """Test creating a workflow template."""
        template = loader.create_workflow_template()

        assert "name" in template
        assert "description" in template
        assert "steps" in template
        assert len(template["steps"]) > 0

    def test_save_workflow_json(self, loader, temp_dir):
        """Test saving workflow as JSON."""
        workflow_data = {
            "name": "save_test",
            "steps": [{"tool": "t", "params": {}}],
        }

        path = loader.save_workflow(workflow_data, "saved", format="json")

        assert path.exists()
        assert path.suffix == ".json"

        # Verify content
        loaded = json.loads(path.read_text())
        assert loaded["name"] == "save_test"

    def test_save_workflow_yaml(self, loader, temp_dir):
        """Test saving workflow as YAML."""
        pytest.importorskip("yaml")

        workflow_data = {
            "name": "yaml_save",
            "steps": [{"tool": "t", "params": {}}],
        }

        path = loader.save_workflow(workflow_data, "saved_yaml", format="yaml")

        assert path.exists()
        assert path.suffix == ".yaml"

    def test_save_workflow_creates_dir(self, tmp_path):
        """Test save creates directory if needed."""
        new_dir = tmp_path / "new" / "subdir"
        loader = WorkflowLoader(workflows_dir=new_dir)

        workflow_data = {
            "name": "test",
            "steps": [{"tool": "t", "params": {}}],
        }

        path = loader.save_workflow(workflow_data, "test", format="json")

        assert path.exists()
        assert new_dir.exists()


class TestGetWorkflowLoader:
    """Tests for get_workflow_loader singleton."""

    def test_returns_loader(self):
        """Test that function returns a loader."""
        loader = get_workflow_loader()
        assert isinstance(loader, WorkflowLoader)

    def test_returns_same_instance(self):
        """Test singleton behavior."""
        loader1 = get_workflow_loader()
        loader2 = get_workflow_loader()
        assert loader1 is loader2


class TestRealCustomWorkflows:
    """Tests for loading real example workflows."""

    def test_load_example_table_yaml(self):
        """Test loading the example table workflow."""
        pytest.importorskip("yaml")

        # Get the actual custom workflows directory
        custom_dir = (
            Path(__file__).parent.parent.parent.parent.parent.parent
            / "server" / "router" / "application" / "workflows" / "custom"
        )

        if not custom_dir.exists():
            pytest.skip("Custom workflows directory not found")

        loader = WorkflowLoader(workflows_dir=custom_dir)
        workflows = loader.load_all()

        # Should have at least the example workflows
        assert len(workflows) >= 1

    def test_load_example_chair_json(self):
        """Test loading the example chair workflow."""
        custom_dir = (
            Path(__file__).parent.parent.parent.parent.parent.parent
            / "server" / "router" / "application" / "workflows" / "custom"
        )

        if not custom_dir.exists():
            pytest.skip("Custom workflows directory not found")

        chair_file = custom_dir / "example_chair.json"
        if not chair_file.exists():
            pytest.skip("Example chair workflow not found")

        loader = WorkflowLoader(workflows_dir=custom_dir)
        workflow = loader.load_file(chair_file)

        assert workflow.name == "chair_workflow"
        assert len(workflow.steps) > 5  # Chair has many steps
