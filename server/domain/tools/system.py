from abc import ABC, abstractmethod
from typing import Optional


class ISystemTool(ABC):
    """Abstract interface for system-level operations.

    System tools provide low-level control over Blender's state including
    mode switching, undo/redo, file operations, and checkpoint management.
    """

    @abstractmethod
    def set_mode(
        self,
        mode: str,
        object_name: Optional[str] = None,
    ) -> str:
        """Switches Blender mode for the active or specified object.

        Args:
            mode: Target mode (OBJECT, EDIT, SCULPT, VERTEX_PAINT, WEIGHT_PAINT, TEXTURE_PAINT, POSE)
            object_name: Object to set mode for (default: active object)

        Returns:
            Status message describing the result
        """
        pass

    @abstractmethod
    def undo(self, steps: int = 1) -> str:
        """Undoes the last operation(s).

        Args:
            steps: Number of steps to undo (default: 1, max: 10)

        Returns:
            Status message describing the result
        """
        pass

    @abstractmethod
    def redo(self, steps: int = 1) -> str:
        """Redoes previously undone operation(s).

        Args:
            steps: Number of steps to redo (default: 1, max: 10)

        Returns:
            Status message describing the result
        """
        pass

    @abstractmethod
    def save_file(
        self,
        filepath: Optional[str] = None,
        compress: bool = True,
    ) -> str:
        """Saves the current Blender file.

        Args:
            filepath: Path to save (default: current file path, or temp if unsaved)
            compress: Compress .blend file (default: True)

        Returns:
            Status message with saved file path
        """
        pass

    @abstractmethod
    def new_file(self, load_ui: bool = False) -> str:
        """Creates a new Blender file (clears current scene).

        WARNING: Unsaved changes will be lost!

        Args:
            load_ui: Load UI from startup file

        Returns:
            Status message describing the result
        """
        pass

    @abstractmethod
    def snapshot(
        self,
        action: str,
        name: Optional[str] = None,
    ) -> str:
        """Manages quick save/restore checkpoints.

        Snapshots are stored in temp directory and cleared on Blender restart.

        Args:
            action: Operation to perform (save, restore, list, delete)
            name: Snapshot name (required for restore/delete, auto-generated for save if not provided)

        Returns:
            Status message or list of snapshots
        """
        pass
