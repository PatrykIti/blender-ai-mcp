"""
Custom Workflow Loader.

Loads workflow definitions from YAML/JSON files.
TASK-039-22
TASK-055: Added parameters section parsing and validation.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Union

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


from server.router.application.workflows.base import WorkflowDefinition, WorkflowStep
from server.router.domain.entities.parameter import ParameterSchema

logger = logging.getLogger(__name__)


class WorkflowValidationError(Exception):
    """Raised when workflow validation fails."""

    pass


class WorkflowLoader:
    """Loads custom workflow definitions from files.

    Supports both YAML and JSON formats. Workflows are loaded from
    a configured directory and validated against the expected schema.

    Usage:
        loader = WorkflowLoader(Path("./workflows"))
        workflows = loader.load_all()
    """

    REQUIRED_FIELDS = ["name", "steps"]
    STEP_REQUIRED_FIELDS = ["tool", "params"]

    def __init__(self, workflows_dir: Optional[Path] = None):
        """Initialize the workflow loader.

        Args:
            workflows_dir: Directory containing workflow files.
                          Defaults to server/router/workflows/custom/
        """
        if workflows_dir is None:
            self._workflows_dir = (
                Path(__file__).parent.parent / "application" / "workflows" / "custom"
            )
        else:
            self._workflows_dir = workflows_dir

        self._cache: Dict[str, WorkflowDefinition] = {}
        self._loaded = False

    @property
    def workflows_dir(self) -> Path:
        """Get the workflows directory path."""
        return self._workflows_dir

    def load_all(self) -> Dict[str, WorkflowDefinition]:
        """Load all workflows from the directory.

        Returns:
            Dictionary mapping workflow names to definitions.

        Raises:
            WorkflowValidationError: If any workflow fails validation.
        """
        if not self._workflows_dir.exists():
            logger.warning(f"Workflows directory not found: {self._workflows_dir}")
            return {}

        workflows = {}

        # Load YAML files
        for yaml_file in self._workflows_dir.glob("*.yaml"):
            try:
                workflow = self.load_file(yaml_file)
                workflows[workflow.name] = workflow
                logger.debug(f"Loaded workflow: {workflow.name} from {yaml_file.name}")
            except Exception as e:
                logger.error(f"Failed to load workflow from {yaml_file}: {e}")

        # Load YML files
        for yml_file in self._workflows_dir.glob("*.yml"):
            try:
                workflow = self.load_file(yml_file)
                workflows[workflow.name] = workflow
                logger.debug(f"Loaded workflow: {workflow.name} from {yml_file.name}")
            except Exception as e:
                logger.error(f"Failed to load workflow from {yml_file}: {e}")

        # Load JSON files
        for json_file in self._workflows_dir.glob("*.json"):
            try:
                workflow = self.load_file(json_file)
                workflows[workflow.name] = workflow
                logger.debug(f"Loaded workflow: {workflow.name} from {json_file.name}")
            except Exception as e:
                logger.error(f"Failed to load workflow from {json_file}: {e}")

        self._cache = workflows
        self._loaded = True

        logger.info(f"Loaded {len(workflows)} custom workflows")
        return workflows

    def load_file(self, file_path: Path) -> WorkflowDefinition:
        """Load a single workflow file.

        Args:
            file_path: Path to the workflow file.

        Returns:
            Parsed workflow definition.

        Raises:
            WorkflowValidationError: If validation fails.
            FileNotFoundError: If file doesn't exist.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Workflow file not found: {file_path}")

        # Read and parse file
        content = file_path.read_text(encoding="utf-8")

        if file_path.suffix in [".yaml", ".yml"]:
            if not YAML_AVAILABLE:
                raise ImportError(
                    "PyYAML is required to load YAML workflows. "
                    "Install with: poetry add pyyaml"
                )
            data = yaml.safe_load(content)
        elif file_path.suffix == ".json":
            data = json.loads(content)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

        # Validate and convert
        return self._parse_workflow(data, file_path)

    def _parse_workflow(
        self, data: Dict[str, Any], source: Optional[Path] = None
    ) -> WorkflowDefinition:
        """Parse workflow data into WorkflowDefinition.

        Args:
            data: Raw workflow data.
            source: Source file path for error messages.

        Returns:
            Parsed workflow definition.

        Raises:
            WorkflowValidationError: If validation fails.
        """
        # Validate required fields
        for field in self.REQUIRED_FIELDS:
            if field not in data:
                raise WorkflowValidationError(
                    f"Missing required field '{field}' in workflow"
                    + (f" from {source}" if source else "")
                )

        # Parse steps
        steps = []
        for i, step_data in enumerate(data.get("steps", [])):
            step = self._parse_step(step_data, i, source)
            steps.append(step)

        if not steps:
            raise WorkflowValidationError(
                f"Workflow must have at least one step"
                + (f" in {source}" if source else "")
            )

        # TASK-055: Parse parameters section
        parameters = self._parse_parameters(data.get("parameters", {}), source)

        # TASK-055: Validate semantic hints vs modifiers overlap
        modifiers = data.get("modifiers", {})
        self._validate_hints_modifiers_overlap(parameters, modifiers, source)

        return WorkflowDefinition(
            name=data["name"],
            description=data.get("description", ""),
            steps=steps,
            trigger_pattern=data.get("trigger_pattern"),
            trigger_keywords=data.get("trigger_keywords", []),
            sample_prompts=data.get("sample_prompts", []),
            category=data.get("category", "custom"),
            author=data.get("author", "user"),
            version=data.get("version", "1.0.0"),
            defaults=data.get("defaults", {}),
            modifiers=modifiers,
            parameters=parameters,
        )

    def _parse_parameters(
        self,
        data: Dict[str, Any],
        source: Optional[Path] = None,
    ) -> Dict[str, ParameterSchema]:
        """Parse parameters section into ParameterSchema objects.

        TASK-055: Parses the parameters section of a workflow YAML.

        Args:
            data: Raw parameters data from YAML.
            source: Source file path for error messages.

        Returns:
            Dictionary mapping parameter names to ParameterSchema objects.

        Raises:
            WorkflowValidationError: If parameter validation fails.
        """
        parameters: Dict[str, ParameterSchema] = {}

        for param_name, param_data in data.items():
            if not isinstance(param_data, dict):
                raise WorkflowValidationError(
                    f"Parameter '{param_name}' must be a dictionary"
                    + (f" in {source}" if source else "")
                )

            try:
                # Add name to data for ParameterSchema.from_dict
                param_data_with_name = {"name": param_name, **param_data}
                schema = ParameterSchema.from_dict(param_data_with_name)
                parameters[param_name] = schema
            except (ValueError, KeyError) as e:
                raise WorkflowValidationError(
                    f"Invalid parameter '{param_name}': {e}"
                    + (f" in {source}" if source else "")
                )

        return parameters

    def _validate_hints_modifiers_overlap(
        self,
        parameters: Dict[str, ParameterSchema],
        modifiers: Dict[str, Dict[str, Any]],
        source: Optional[Path] = None,
    ) -> None:
        """Validate that semantic hints don't conflict with modifiers.

        TASK-055: Implementation note - semantic_hints should NOT overlap with
        modifier keys if they produce different values. This validation warns
        about potential conflicts but doesn't fail (modifiers take priority).

        Args:
            parameters: Parsed parameter schemas.
            modifiers: Modifier keyword mappings.
            source: Source file path for log messages.
        """
        modifier_keys_lower = {k.lower() for k in modifiers.keys()}

        for param_name, schema in parameters.items():
            for hint in schema.semantic_hints:
                hint_lower = hint.lower()
                if hint_lower in modifier_keys_lower:
                    # Find the matching modifier
                    matching_modifier = None
                    for mod_key in modifiers:
                        if mod_key.lower() == hint_lower:
                            matching_modifier = mod_key
                            break

                    if matching_modifier:
                        mod_value = modifiers[matching_modifier].get(param_name)
                        if mod_value is not None:
                            # Modifier explicitly sets this parameter - this is intentional
                            logger.debug(
                                f"Parameter '{param_name}' has semantic_hint '{hint}' "
                                f"matching modifier '{matching_modifier}' "
                                f"(value={mod_value}) - modifier will take priority"
                                + (f" in {source}" if source else "")
                            )
                        else:
                            # Hint matches modifier key but modifier doesn't set this param
                            logger.warning(
                                f"Parameter '{param_name}' has semantic_hint '{hint}' "
                                f"matching modifier '{matching_modifier}', but modifier "
                                f"doesn't set '{param_name}'. Consider adding explicit mapping."
                                + (f" in {source}" if source else "")
                            )

    def _parse_step(
        self, data: Dict[str, Any], index: int, source: Optional[Path] = None
    ) -> WorkflowStep:
        """Parse a single workflow step.

        Args:
            data: Raw step data.
            index: Step index for error messages.
            source: Source file path for error messages.

        Returns:
            Parsed workflow step.

        Raises:
            WorkflowValidationError: If validation fails.
        """
        for field in self.STEP_REQUIRED_FIELDS:
            if field not in data:
                raise WorkflowValidationError(
                    f"Missing required field '{field}' in step {index + 1}"
                    + (f" from {source}" if source else "")
                )

        return WorkflowStep(
            tool=data["tool"],
            params=data.get("params", {}),
            description=data.get("description"),
            condition=data.get("condition"),
            optional=data.get("optional", False),
            tags=data.get("tags", []),
        )

    def get_workflow(self, name: str) -> Optional[WorkflowDefinition]:
        """Get a loaded workflow by name.

        Args:
            name: Workflow name.

        Returns:
            Workflow definition or None if not found.
        """
        if not self._loaded:
            self.load_all()
        return self._cache.get(name)

    def reload(self) -> Dict[str, WorkflowDefinition]:
        """Reload all workflows from disk.

        Returns:
            Updated workflow dictionary.
        """
        self._cache.clear()
        self._loaded = False
        return self.load_all()

    def validate_workflow_data(self, data: Dict[str, Any]) -> List[str]:
        """Validate workflow data without parsing.

        Args:
            data: Workflow data to validate.

        Returns:
            List of validation error messages (empty if valid).
        """
        errors = []

        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in data:
                errors.append(f"Missing required field: {field}")

        # Check steps
        steps = data.get("steps", [])
        if not steps:
            errors.append("Workflow must have at least one step")

        for i, step in enumerate(steps):
            for field in self.STEP_REQUIRED_FIELDS:
                if field not in step:
                    errors.append(f"Step {i + 1}: Missing required field '{field}'")

            # Validate params is a dict
            if "params" in step and not isinstance(step["params"], dict):
                errors.append(f"Step {i + 1}: 'params' must be a dictionary")

        # Check name format
        if "name" in data:
            name = data["name"]
            if not isinstance(name, str) or not name.strip():
                errors.append("Workflow name must be a non-empty string")
            elif " " in name:
                errors.append("Workflow name should not contain spaces (use underscores)")

        # TASK-055: Validate parameters section
        parameters = data.get("parameters", {})
        if parameters:
            if not isinstance(parameters, dict):
                errors.append("'parameters' must be a dictionary")
            else:
                valid_types = {"float", "int", "bool", "string"}
                for param_name, param_data in parameters.items():
                    if not isinstance(param_data, dict):
                        errors.append(
                            f"Parameter '{param_name}': must be a dictionary"
                        )
                        continue

                    # Validate type if specified
                    param_type = param_data.get("type")
                    if param_type and param_type not in valid_types:
                        errors.append(
                            f"Parameter '{param_name}': invalid type '{param_type}'. "
                            f"Must be one of: {valid_types}"
                        )

                    # Validate range if specified
                    param_range = param_data.get("range")
                    if param_range:
                        if not isinstance(param_range, (list, tuple)) or len(param_range) != 2:
                            errors.append(
                                f"Parameter '{param_name}': range must be [min, max]"
                            )
                        elif param_range[0] > param_range[1]:
                            errors.append(
                                f"Parameter '{param_name}': range min must be <= max"
                            )

                    # Validate semantic_hints if specified
                    hints = param_data.get("semantic_hints")
                    if hints and not isinstance(hints, list):
                        errors.append(
                            f"Parameter '{param_name}': semantic_hints must be a list"
                        )

        return errors

    def create_workflow_template(self) -> Dict[str, Any]:
        """Create a template for a new workflow file.

        Returns:
            Template dictionary that can be saved as YAML/JSON.
        """
        return {
            "name": "my_workflow",
            "description": "Description of what this workflow does",
            "category": "custom",
            "author": "your_name",
            "version": "1.0.0",
            "trigger_pattern": None,  # Optional: pattern name to trigger
            "trigger_keywords": ["keyword1", "keyword2"],
            "sample_prompts": [
                # English prompts for LaBSE semantic matching
                "create my object",
                "build my thing",
                # Multilingual prompts (LaBSE supports 109 languages)
                "stwórz mój obiekt",  # Polish
                "erstelle mein Objekt",  # German
            ],
            # Parametric variables (TASK-052)
            "defaults": {
                "my_variable": 1.0,
                "another_var": 0.5,
            },
            "modifiers": {
                "keyword phrase": {
                    "my_variable": 2.0,
                },
                "inna fraza": {  # Polish
                    "my_variable": 2.0,
                },
            },
            # TASK-055: Interactive parameter resolution
            # Parameters that can be interactively resolved via LLM
            "parameters": {
                "my_variable": {
                    "type": "float",
                    "range": [0.5, 3.0],
                    "default": 1.0,
                    "description": "Controls the Y-scale of the object",
                    "semantic_hints": ["height", "tall", "short", "scale"],
                    "group": "dimensions",
                },
                "another_var": {
                    "type": "float",
                    "range": [0.0, 1.0],
                    "default": 0.5,
                    "description": "Secondary adjustment factor",
                    "semantic_hints": ["factor", "amount", "level"],
                },
            },
            "steps": [
                {
                    "tool": "modeling_create_primitive",
                    "params": {"type": "CUBE"},
                    "description": "Create a cube",
                    "optional": False,  # Core step - always executed
                    "tags": [],
                },
                {
                    "tool": "modeling_transform_object",
                    "params": {
                        "scale": [1.0, "$my_variable", 1.0],  # $variable substitution
                    },
                    "description": "Transform with variable",
                    "optional": False,
                    "tags": [],
                },
            ],
        }

    def save_workflow(
        self,
        workflow: Union[WorkflowDefinition, Dict[str, Any]],
        filename: str,
        format: str = "yaml",
    ) -> Path:
        """Save a workflow to file.

        Args:
            workflow: Workflow definition or dict to save.
            filename: Filename (without extension).
            format: Output format ('yaml' or 'json').

        Returns:
            Path to the saved file.
        """
        # Ensure directory exists
        self._workflows_dir.mkdir(parents=True, exist_ok=True)

        # Convert to dict if needed
        if isinstance(workflow, WorkflowDefinition):
            data = workflow.to_dict()
        else:
            data = workflow

        # Determine extension and save
        if format == "yaml":
            if not YAML_AVAILABLE:
                raise ImportError("PyYAML is required to save YAML workflows")
            file_path = self._workflows_dir / f"{filename}.yaml"
            content = yaml.dump(data, default_flow_style=False, allow_unicode=True)
        else:
            file_path = self._workflows_dir / f"{filename}.json"
            content = json.dumps(data, indent=2)

        file_path.write_text(content, encoding="utf-8")
        logger.info(f"Saved workflow to {file_path}")

        return file_path


# Singleton instance
_workflow_loader: Optional[WorkflowLoader] = None


def get_workflow_loader() -> WorkflowLoader:
    """Get the global workflow loader instance.

    Returns:
        WorkflowLoader singleton.
    """
    global _workflow_loader
    if _workflow_loader is None:
        _workflow_loader = WorkflowLoader()
    return _workflow_loader
