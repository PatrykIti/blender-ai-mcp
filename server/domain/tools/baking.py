from abc import ABC, abstractmethod
from typing import Optional


class IBakingTool(ABC):
    """Interface for texture baking operations."""

    @abstractmethod
    def bake_normal_map(
        self,
        object_name: str,
        output_path: str,
        resolution: int = 1024,
        high_poly_source: Optional[str] = None,
        cage_extrusion: float = 0.1,
        margin: int = 16,
        normal_space: str = "TANGENT"
    ) -> str:
        """
        Bakes normal map from high-poly to low-poly or from geometry.

        Args:
            object_name: Target object to bake onto
            output_path: File path to save the baked image
            resolution: Image resolution (default 1024x1024)
            high_poly_source: Source object for high-to-low baking (None = self-bake)
            cage_extrusion: Ray distance for high-to-low baking
            margin: Pixel margin for UV island bleeding
            normal_space: TANGENT or OBJECT space normals
        """
        pass

    @abstractmethod
    def bake_ao(
        self,
        object_name: str,
        output_path: str,
        resolution: int = 1024,
        samples: int = 128,
        distance: float = 1.0,
        margin: int = 16
    ) -> str:
        """
        Bakes ambient occlusion map.

        Args:
            object_name: Target object to bake
            output_path: File path to save the baked image
            resolution: Image resolution (default 1024x1024)
            samples: Number of samples for quality
            distance: AO ray distance
            margin: Pixel margin for UV island bleeding
        """
        pass

    @abstractmethod
    def bake_combined(
        self,
        object_name: str,
        output_path: str,
        resolution: int = 1024,
        samples: int = 128,
        margin: int = 16,
        use_pass_direct: bool = True,
        use_pass_indirect: bool = True,
        use_pass_color: bool = True
    ) -> str:
        """
        Bakes combined render (full material + lighting) to texture.

        Args:
            object_name: Target object to bake
            output_path: File path to save the baked image
            resolution: Image resolution (default 1024x1024)
            samples: Number of render samples
            margin: Pixel margin for UV island bleeding
            use_pass_direct: Include direct lighting
            use_pass_indirect: Include indirect lighting
            use_pass_color: Include diffuse color
        """
        pass

    @abstractmethod
    def bake_diffuse(
        self,
        object_name: str,
        output_path: str,
        resolution: int = 1024,
        margin: int = 16
    ) -> str:
        """
        Bakes diffuse/albedo color only.

        Args:
            object_name: Target object to bake
            output_path: File path to save the baked image
            resolution: Image resolution (default 1024x1024)
            margin: Pixel margin for UV island bleeding
        """
        pass
