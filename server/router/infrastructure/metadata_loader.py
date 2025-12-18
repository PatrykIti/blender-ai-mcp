"""
Tool Metadata Loader.

Loads tool metadata from per-tool JSON files for router decision making.
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, Optional, List, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ToolMetadata:
    """Metadata for a single tool.

    Attributes:
        tool_name: Unique tool identifier.
        category: Tool category (scene, mesh, modeling, etc.).
        mode_required: Required Blender mode (OBJECT, EDIT, ANY).
        selection_required: Whether tool requires geometry selection.
        keywords: Keywords for intent matching.
        sample_prompts: Example prompts for classifier training.
        parameters: Parameter definitions with types and ranges.
        related_tools: Tools often used together.
        patterns: Associated geometry patterns.
        description: Human-readable description.
    """

    tool_name: str
    category: str
    mode_required: str = "ANY"
    selection_required: bool = False
    keywords: List[str] = field(default_factory=list)
    sample_prompts: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    related_tools: List[str] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "tool_name": self.tool_name,
            "category": self.category,
            "mode_required": self.mode_required,
            "selection_required": self.selection_required,
            "keywords": self.keywords,
            "sample_prompts": self.sample_prompts,
            "parameters": self.parameters,
            "related_tools": self.related_tools,
            "patterns": self.patterns,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ToolMetadata":
        """Create from dictionary."""
        return cls(
            tool_name=data["tool_name"],
            category=data["category"],
            mode_required=data.get("mode_required", "ANY"),
            selection_required=data.get("selection_required", False),
            keywords=data.get("keywords", []),
            sample_prompts=data.get("sample_prompts", []),
            parameters=data.get("parameters", {}),
            related_tools=data.get("related_tools", []),
            patterns=data.get("patterns", []),
            description=data.get("description", ""),
        )


@dataclass
class ValidationError:
    """Metadata validation error.

    Attributes:
        file_path: Path to the file with error.
        error_type: Type of error.
        message: Error description.
    """

    file_path: str
    error_type: str
    message: str


class MetadataLoader:
    """Loads tool metadata from modular JSON files.

    Directory structure:
        tools_metadata/
        ├── _schema.json
        ├── scene/
        │   └── scene_*.json
        ├── mesh/
        │   └── mesh_*.json
        └── ...

    Usage:
        loader = MetadataLoader()
        metadata = loader.load_all()
        tool = loader.get_tool("mesh_extrude")
    """

    # Supported tool areas
    AREAS = [
        "scene",
        "system",
        "modeling",
        "mesh",
        "material",
        "uv",
        "curve",
        "collection",
        "lattice",
        "sculpt",
        "baking",
    ]

    def __init__(self, metadata_dir: Optional[Path] = None):
        """Initialize metadata loader.

        Args:
            metadata_dir: Path to tools_metadata directory.
                         Defaults to ./tools_metadata relative to this file.
        """
        if metadata_dir is None:
            metadata_dir = Path(__file__).parent / "tools_metadata"
        self.metadata_dir = metadata_dir
        self._cache: Dict[str, ToolMetadata] = {}
        self._cache_hash: Optional[str] = None
        self._last_load: Optional[datetime] = None
        self._schema: Optional[Dict[str, Any]] = None

    def load_all(self) -> Dict[str, ToolMetadata]:
        """Load all tool metadata from all areas.

        Returns:
            Dictionary mapping tool_name to ToolMetadata.
        """
        if self._cache and self._is_cache_valid():
            return self._cache

        self._cache.clear()
        self._load_schema()

        for area in self.AREAS:
            area_metadata = self.load_by_area(area)
            self._cache.update(area_metadata)

        self._cache_hash = self._compute_hash()
        self._last_load = datetime.now()
        return self._cache

    def load_by_area(self, area: str) -> Dict[str, ToolMetadata]:
        """Load tool metadata for a specific area.

        Args:
            area: Area name (scene, mesh, modeling, etc.).

        Returns:
            Dictionary mapping tool_name to ToolMetadata for that area.
        """
        area_dir = self.metadata_dir / area
        if not area_dir.exists():
            return {}

        metadata: Dict[str, ToolMetadata] = {}

        for json_file in area_dir.glob("*.json"):
            try:
                tool_metadata = self._load_file(json_file)
                if tool_metadata:
                    metadata[tool_metadata.tool_name] = tool_metadata
            except Exception as e:
                # Log error but continue loading other files
                print(f"Error loading {json_file}: {e}")

        return metadata

    def get_tool(self, tool_name: str) -> Optional[ToolMetadata]:
        """Get metadata for a specific tool.

        Args:
            tool_name: Tool name to look up.

        Returns:
            ToolMetadata or None if not found.
        """
        if not self._cache:
            self.load_all()
        return self._cache.get(tool_name)

    def reload(self) -> None:
        """Reload all metadata from disk."""
        self._cache.clear()
        self._cache_hash = None
        self._last_load = None
        self.load_all()

    def validate_all(self) -> List[ValidationError]:
        """Validate all metadata against schema.

        Returns:
            List of validation errors.
        """
        errors: List[ValidationError] = []
        self._load_schema()

        for area in self.AREAS:
            area_dir = self.metadata_dir / area
            if not area_dir.exists():
                continue

            for json_file in area_dir.glob("*.json"):
                file_errors = self._validate_file(json_file)
                errors.extend(file_errors)

        return errors

    def get_tools_by_mode(self, mode: str) -> List[ToolMetadata]:
        """Get all tools that require a specific mode.

        Args:
            mode: Blender mode (OBJECT, EDIT, SCULPT, etc.).

        Returns:
            List of ToolMetadata for tools requiring that mode.
        """
        if not self._cache:
            self.load_all()

        return [
            tool for tool in self._cache.values()
            if tool.mode_required == mode or tool.mode_required == "ANY"
        ]

    def get_tools_by_category(self, category: str) -> List[ToolMetadata]:
        """Get all tools in a specific category.

        Args:
            category: Category name.

        Returns:
            List of ToolMetadata for tools in that category.
        """
        if not self._cache:
            self.load_all()

        return [
            tool for tool in self._cache.values()
            if tool.category == category
        ]

    def get_tools_requiring_selection(self) -> List[str]:
        """Get names of all tools that require selection.

        Returns:
            List of tool names.
        """
        if not self._cache:
            self.load_all()

        return [
            tool.tool_name for tool in self._cache.values()
            if tool.selection_required
        ]

    def search_by_keyword(self, keyword: str) -> List[ToolMetadata]:
        """Search tools by keyword.

        Args:
            keyword: Keyword to search for.

        Returns:
            List of matching ToolMetadata.
        """
        if not self._cache:
            self.load_all()

        keyword_lower = keyword.lower()
        return [
            tool for tool in self._cache.values()
            if any(keyword_lower in kw.lower() for kw in tool.keywords)
        ]

    def get_all_sample_prompts(self) -> Dict[str, List[str]]:
        """Get all sample prompts mapped to tool names.

        Returns:
            Dictionary mapping tool_name to list of sample prompts.
        """
        if not self._cache:
            self.load_all()

        return {
            tool.tool_name: tool.sample_prompts
            for tool in self._cache.values()
            if tool.sample_prompts
        }

    def _load_file(self, file_path: Path) -> Optional[ToolMetadata]:
        """Load metadata from a single JSON file.

        Args:
            file_path: Path to JSON file.

        Returns:
            ToolMetadata or None if loading fails.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return ToolMetadata.from_dict(data)

    def _load_schema(self) -> None:
        """Load JSON schema for validation."""
        schema_path = self.metadata_dir / "_schema.json"
        if schema_path.exists() and self._schema is None:
            with open(schema_path, "r", encoding="utf-8") as f:
                self._schema = json.load(f)

    def _validate_file(self, file_path: Path) -> List[ValidationError]:
        """Validate a single metadata file.

        Args:
            file_path: Path to JSON file.

        Returns:
            List of validation errors for this file.
        """
        errors: List[ValidationError] = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            errors.append(ValidationError(
                file_path=str(file_path),
                error_type="json_parse_error",
                message=str(e),
            ))
            return errors

        # Required fields
        required = ["tool_name", "category", "mode_required"]
        for field in required:
            if field not in data:
                errors.append(ValidationError(
                    file_path=str(file_path),
                    error_type="missing_required_field",
                    message=f"Missing required field: {field}",
                ))

        # Valid category
        if "category" in data and data["category"] not in self.AREAS:
            errors.append(ValidationError(
                file_path=str(file_path),
                error_type="invalid_category",
                message=f"Invalid category: {data['category']}",
            ))

        # Valid mode
        valid_modes = ["OBJECT", "EDIT", "SCULPT", "VERTEX_PAINT", "WEIGHT_PAINT", "TEXTURE_PAINT", "ANY"]
        if "mode_required" in data and data["mode_required"] not in valid_modes:
            errors.append(ValidationError(
                file_path=str(file_path),
                error_type="invalid_mode",
                message=f"Invalid mode_required: {data['mode_required']}",
            ))

        return errors

    def _compute_hash(self) -> str:
        """Compute hash of all metadata for cache validation."""
        content = json.dumps(
            {k: v.to_dict() for k, v in sorted(self._cache.items())},
            sort_keys=True,
        )
        return hashlib.md5(content.encode()).hexdigest()

    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid."""
        if self._cache_hash is None:
            return False
        # For now, always consider cache valid during session
        # Could add file modification time checking here
        return True
