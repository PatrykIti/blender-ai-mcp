"""
Unit tests for WorkflowLoader.

Tests for loading custom workflows from YAML/JSON files.
TASK-039-22
TASK-055: Added tests for parameters section parsing.
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
from server.router.domain.entities.parameter import ParameterSchema


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
        # Path: tests/unit/router/infrastructure/test_workflow_loader.py
        # Need 5 parents to reach project root
        custom_dir = (
            Path(__file__).parent.parent.parent.parent.parent
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
        # Path: tests/unit/router/infrastructure/test_workflow_loader.py
        # Need 5 parents to reach project root
        custom_dir = (
            Path(__file__).parent.parent.parent.parent.parent
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


class TestWorkflowLoaderParameters:
    """TASK-055: Tests for parameters section parsing."""

    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Create a temporary directory for workflow files."""
        return tmp_path

    @pytest.fixture
    def loader(self, temp_dir):
        """Create a loader with temporary directory."""
        return WorkflowLoader(workflows_dir=temp_dir)

    def test_load_workflow_with_parameters(self, loader, temp_dir):
        """Test loading workflow with parameters section."""
        workflow_data = {
            "name": "param_workflow",
            "description": "Workflow with parameters",
            "steps": [{"tool": "test_tool", "params": {"x": "$my_param"}}],
            "defaults": {"my_param": 1.0},
            "parameters": {
                "my_param": {
                    "type": "float",
                    "range": [0.0, 10.0],
                    "default": 1.0,
                    "description": "A test parameter",
                    "semantic_hints": ["size", "dimension"],
                }
            },
        }

        file_path = temp_dir / "param_workflow.json"
        file_path.write_text(json.dumps(workflow_data))

        workflow = loader.load_file(file_path)

        assert workflow.name == "param_workflow"
        assert "my_param" in workflow.parameters
        assert isinstance(workflow.parameters["my_param"], ParameterSchema)
        assert workflow.parameters["my_param"].type == "float"
        assert workflow.parameters["my_param"].range == (0.0, 10.0)
        assert workflow.parameters["my_param"].default == 1.0
        assert workflow.parameters["my_param"].semantic_hints == ["size", "dimension"]

    def test_load_workflow_multiple_parameters(self, loader, temp_dir):
        """Test loading workflow with multiple parameters."""
        workflow_data = {
            "name": "multi_param",
            "steps": [{"tool": "t", "params": {}}],
            "parameters": {
                "angle": {
                    "type": "float",
                    "range": [-3.14, 3.14],
                    "default": 0.0,
                    "description": "Rotation angle",
                    "semantic_hints": ["rotation", "angle", "tilt"],
                    "group": "angles",
                },
                "width": {
                    "type": "float",
                    "range": [0.1, 10.0],
                    "default": 1.0,
                    "description": "Object width",
                    "semantic_hints": ["wide", "narrow", "size"],
                },
                "enabled": {
                    "type": "bool",
                    "default": True,
                    "description": "Enable feature",
                },
            },
        }

        file_path = temp_dir / "multi.json"
        file_path.write_text(json.dumps(workflow_data))

        workflow = loader.load_file(file_path)

        assert len(workflow.parameters) == 3
        assert "angle" in workflow.parameters
        assert "width" in workflow.parameters
        assert "enabled" in workflow.parameters
        assert workflow.parameters["angle"].group == "angles"
        assert workflow.parameters["enabled"].type == "bool"

    def test_load_workflow_without_parameters(self, loader, temp_dir):
        """Test loading workflow without parameters section."""
        workflow_data = {
            "name": "no_params",
            "steps": [{"tool": "t", "params": {}}],
        }

        file_path = temp_dir / "no_params.json"
        file_path.write_text(json.dumps(workflow_data))

        workflow = loader.load_file(file_path)

        assert workflow.parameters == {}

    def test_parameter_invalid_type(self, loader, temp_dir):
        """Test that invalid parameter type raises error."""
        workflow_data = {
            "name": "invalid_type",
            "steps": [{"tool": "t", "params": {}}],
            "parameters": {
                "bad_param": {
                    "type": "invalid_type",
                    "default": 1,
                },
            },
        }

        file_path = temp_dir / "invalid.json"
        file_path.write_text(json.dumps(workflow_data))

        with pytest.raises(WorkflowValidationError, match="Invalid parameter"):
            loader.load_file(file_path)

    def test_parameter_not_dict(self, loader, temp_dir):
        """Test that non-dict parameter raises error."""
        workflow_data = {
            "name": "not_dict",
            "steps": [{"tool": "t", "params": {}}],
            "parameters": {
                "bad_param": "not a dictionary",
            },
        }

        file_path = temp_dir / "not_dict.json"
        file_path.write_text(json.dumps(workflow_data))

        with pytest.raises(WorkflowValidationError, match="must be a dictionary"):
            loader.load_file(file_path)

    def test_validate_parameters_valid(self, loader):
        """Test validation of valid parameters section."""
        data = {
            "name": "valid",
            "steps": [{"tool": "t", "params": {}}],
            "parameters": {
                "my_param": {
                    "type": "float",
                    "range": [0, 10],
                    "default": 5,
                    "semantic_hints": ["size"],
                },
            },
        }

        errors = loader.validate_workflow_data(data)
        assert errors == []

    def test_validate_parameters_invalid_type(self, loader):
        """Test validation catches invalid parameter type."""
        data = {
            "name": "invalid",
            "steps": [{"tool": "t", "params": {}}],
            "parameters": {
                "param": {"type": "invalid"},
            },
        }

        errors = loader.validate_workflow_data(data)
        assert any("invalid type" in e for e in errors)

    def test_validate_parameters_invalid_range(self, loader):
        """Test validation catches invalid range."""
        data = {
            "name": "invalid_range",
            "steps": [{"tool": "t", "params": {}}],
            "parameters": {
                "param": {
                    "type": "float",
                    "range": [10, 0],  # min > max
                },
            },
        }

        errors = loader.validate_workflow_data(data)
        assert any("min must be <= max" in e for e in errors)

    def test_validate_parameters_range_wrong_format(self, loader):
        """Test validation catches wrong range format."""
        data = {
            "name": "wrong_range",
            "steps": [{"tool": "t", "params": {}}],
            "parameters": {
                "param": {
                    "type": "float",
                    "range": [1, 2, 3],  # Should be [min, max]
                },
            },
        }

        errors = loader.validate_workflow_data(data)
        assert any("range must be [min, max]" in e for e in errors)

    def test_validate_parameters_hints_not_list(self, loader):
        """Test validation catches non-list semantic_hints."""
        data = {
            "name": "hints_string",
            "steps": [{"tool": "t", "params": {}}],
            "parameters": {
                "param": {
                    "type": "float",
                    "semantic_hints": "not a list",
                },
            },
        }

        errors = loader.validate_workflow_data(data)
        assert any("semantic_hints must be a list" in e for e in errors)

    def test_workflow_template_includes_parameters(self, loader):
        """Test that template includes parameters section."""
        template = loader.create_workflow_template()

        assert "parameters" in template
        assert isinstance(template["parameters"], dict)
        assert len(template["parameters"]) > 0

        # Check a sample parameter
        param = list(template["parameters"].values())[0]
        assert "type" in param
        assert "range" in param
        assert "default" in param
        assert "description" in param
        assert "semantic_hints" in param

    def test_workflow_to_dict_includes_parameters(self, loader, temp_dir):
        """Test that workflow to_dict includes parameters."""
        workflow_data = {
            "name": "to_dict_test",
            "steps": [{"tool": "t", "params": {}}],
            "parameters": {
                "test_param": {
                    "type": "float",
                    "range": [0, 1],
                    "default": 0.5,
                    "semantic_hints": ["test"],
                },
            },
        }

        file_path = temp_dir / "to_dict.json"
        file_path.write_text(json.dumps(workflow_data))

        workflow = loader.load_file(file_path)
        result = workflow.to_dict()

        assert "parameters" in result
        assert "test_param" in result["parameters"]
        assert result["parameters"]["test_param"]["type"] == "float"

    def test_yaml_with_parameters(self, loader, temp_dir):
        """Test loading YAML workflow with parameters."""
        pytest.importorskip("yaml")

        yaml_content = """
name: yaml_params
description: YAML with parameters
parameters:
  leg_angle:
    type: float
    range: [-1.57, 1.57]
    default: 0.32
    description: Angle of table legs
    semantic_hints:
      - angle
      - rotation
      - nogi
    group: angles
steps:
  - tool: test
    params:
      angle: "$leg_angle"
"""
        file_path = temp_dir / "params.yaml"
        file_path.write_text(yaml_content)

        workflow = loader.load_file(file_path)

        assert "leg_angle" in workflow.parameters
        assert workflow.parameters["leg_angle"].range == (-1.57, 1.57)
        assert workflow.parameters["leg_angle"].group == "angles"
        assert "nogi" in workflow.parameters["leg_angle"].semantic_hints


class TestWorkflowLoaderHintsModifiersValidation:
    """TASK-055: Tests for semantic hints vs modifiers validation."""

    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Create a temporary directory for workflow files."""
        return tmp_path

    @pytest.fixture
    def loader(self, temp_dir):
        """Create a loader with temporary directory."""
        return WorkflowLoader(workflows_dir=temp_dir)

    def test_no_warning_when_modifier_sets_param(self, loader, temp_dir, caplog):
        """Test no warning when modifier explicitly sets parameter."""
        import logging
        caplog.set_level(logging.DEBUG)

        workflow_data = {
            "name": "explicit_modifier",
            "steps": [{"tool": "t", "params": {}}],
            "modifiers": {
                "straight legs": {"leg_angle": 0},
            },
            "parameters": {
                "leg_angle": {
                    "type": "float",
                    "range": [-1.57, 1.57],
                    "default": 0.32,
                    "semantic_hints": ["straight legs", "angle"],
                },
            },
        }

        file_path = temp_dir / "explicit.json"
        file_path.write_text(json.dumps(workflow_data))

        workflow = loader.load_file(file_path)

        # Should succeed without warning
        assert workflow is not None
        # Debug message about modifier taking priority is expected
        assert "modifier will take priority" in caplog.text

    def test_warning_when_hint_matches_modifier_no_param(
        self, loader, temp_dir, caplog
    ):
        """Test warning when hint matches modifier but modifier doesn't set param."""
        import logging
        caplog.set_level(logging.WARNING)

        workflow_data = {
            "name": "missing_mapping",
            "steps": [{"tool": "t", "params": {}}],
            "modifiers": {
                "straight legs": {"other_param": 0},  # Doesn't set leg_angle
            },
            "parameters": {
                "leg_angle": {
                    "type": "float",
                    "semantic_hints": ["straight legs"],
                },
            },
        }

        file_path = temp_dir / "missing.json"
        file_path.write_text(json.dumps(workflow_data))

        workflow = loader.load_file(file_path)

        assert workflow is not None
        assert "Consider adding explicit mapping" in caplog.text

    def test_no_overlap_no_warning(self, loader, temp_dir, caplog):
        """Test no warning when no overlap between hints and modifiers."""
        import logging
        caplog.set_level(logging.DEBUG)

        workflow_data = {
            "name": "no_overlap",
            "steps": [{"tool": "t", "params": {}}],
            "modifiers": {
                "straight legs": {"leg_angle": 0},
            },
            "parameters": {
                "width": {
                    "type": "float",
                    "semantic_hints": ["wide", "narrow"],  # No overlap
                },
            },
        }

        file_path = temp_dir / "no_overlap.json"
        file_path.write_text(json.dumps(workflow_data))

        workflow = loader.load_file(file_path)

        assert workflow is not None
        # No warnings about overlap
        assert "Consider adding" not in caplog.text
        assert "modifier will take priority" not in caplog.text
