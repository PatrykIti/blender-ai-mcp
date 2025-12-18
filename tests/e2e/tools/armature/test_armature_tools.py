"""
E2E Tests for Armature & Rigging Tools (TASK-037)

Tests the complete workflow:
1. Create armature with initial bone
2. Add additional bones to armature
3. Bind mesh to armature
4. Pose bones for animation
5. Assign vertex weights manually
"""
import pytest
import time
from server.application.tool_handlers.armature_handler import ArmatureToolHandler
from server.application.tool_handlers.scene_handler import SceneToolHandler
from server.application.tool_handlers.modeling_handler import ModelingToolHandler
from server.application.tool_handlers.mesh_handler import MeshToolHandler
from server.application.tool_handlers.system_handler import SystemToolHandler


@pytest.fixture
def armature_handler(rpc_client):
    """Provides an armature handler instance using shared RPC client."""
    return ArmatureToolHandler(rpc_client)


@pytest.fixture
def scene_handler(rpc_client):
    """Provides a scene handler instance using shared RPC client."""
    return SceneToolHandler(rpc_client)


@pytest.fixture
def modeling_handler(rpc_client):
    """Provides a modeling handler instance using shared RPC client."""
    return ModelingToolHandler(rpc_client)


@pytest.fixture
def mesh_handler(rpc_client):
    """Provides a mesh handler instance using shared RPC client."""
    return MeshToolHandler(rpc_client)


@pytest.fixture
def system_handler(rpc_client):
    """Provides a system handler instance using shared RPC client."""
    return SystemToolHandler(rpc_client)


# ============================================================================
# TASK-037-1: armature_create Tests
# ============================================================================


def test_armature_create_default(armature_handler, scene_handler):
    """Test creating armature with default parameters."""
    try:
        armature_name = f"TestArmature_{int(time.time())}"

        result = armature_handler.create(name=armature_name)

        assert "Created armature" in result
        assert armature_name in result
        print(f"✓ armature_create default: {result}")

        # Cleanup
        scene_handler.delete_object(armature_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_armature_create_with_location(armature_handler, scene_handler):
    """Test creating armature at specific location."""
    try:
        armature_name = f"LocatedArmature_{int(time.time())}"

        result = armature_handler.create(
            name=armature_name,
            location=[1, 2, 3],
        )

        assert "Created armature" in result
        assert "(1, 2, 3)" in result
        print(f"✓ armature_create with location: {result}")

        # Cleanup
        scene_handler.delete_object(armature_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_armature_create_with_custom_bone(armature_handler, scene_handler):
    """Test creating armature with custom initial bone."""
    try:
        armature_name = f"CustomBoneArm_{int(time.time())}"

        result = armature_handler.create(
            name=armature_name,
            bone_name="Root",
            bone_length=0.5,
        )

        assert "Created armature" in result
        assert "Root" in result
        assert "length=0.5" in result
        print(f"✓ armature_create with custom bone: {result}")

        # Cleanup
        scene_handler.delete_object(armature_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


# ============================================================================
# TASK-037-2: armature_add_bone Tests
# ============================================================================


def test_armature_add_bone_basic(armature_handler, scene_handler):
    """Test adding bone to existing armature."""
    try:
        armature_name = f"BoneAddArm_{int(time.time())}"

        # Create armature
        armature_handler.create(name=armature_name)

        # Add bone
        result = armature_handler.add_bone(
            armature_name=armature_name,
            bone_name="Spine",
            head=[0, 0, 1],
            tail=[0, 0, 1.5],
        )

        assert "Added bone 'Spine'" in result
        print(f"✓ armature_add_bone basic: {result}")

        # Cleanup
        scene_handler.delete_object(armature_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_armature_add_bone_with_parent(armature_handler, scene_handler):
    """Test adding bone with parent relationship."""
    try:
        armature_name = f"ParentBoneArm_{int(time.time())}"

        # Create armature
        armature_handler.create(name=armature_name, bone_name="Root")

        # Add child bone
        result = armature_handler.add_bone(
            armature_name=armature_name,
            bone_name="Spine",
            head=[0, 0, 1],
            tail=[0, 0, 1.5],
            parent_bone="Root",
        )

        assert "Added bone 'Spine'" in result
        assert "parent='Root'" in result
        print(f"✓ armature_add_bone with parent: {result}")

        # Cleanup
        scene_handler.delete_object(armature_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_armature_add_bone_connected(armature_handler, scene_handler):
    """Test adding connected bone to parent."""
    try:
        armature_name = f"ConnectedArm_{int(time.time())}"

        # Create armature
        armature_handler.create(name=armature_name, bone_name="Spine")

        # Add connected child bone
        result = armature_handler.add_bone(
            armature_name=armature_name,
            bone_name="Chest",
            head=[0, 0, 1],
            tail=[0, 0, 1.5],
            parent_bone="Spine",
            use_connect=True,
        )

        assert "Added bone 'Chest'" in result
        assert "connected" in result
        print(f"✓ armature_add_bone connected: {result}")

        # Cleanup
        scene_handler.delete_object(armature_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_armature_add_bone_not_found(armature_handler):
    """Test error handling for non-existent armature."""
    try:
        armature_handler.add_bone(
            armature_name="NonExistentArm12345",
            bone_name="Bone",
            head=[0, 0, 0],
            tail=[0, 0, 1],
        )
        assert False, "Expected RuntimeError for non-existent armature"
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        elif "not found" in error_msg:
            print("✓ armature_add_bone properly handles non-existent armature")
        else:
            raise


# ============================================================================
# TASK-037-3: armature_bind Tests
# ============================================================================


def test_armature_bind_auto_weights(armature_handler, scene_handler, modeling_handler):
    """Test binding mesh to armature with automatic weights."""
    try:
        armature_name = f"BindArm_{int(time.time())}"
        mesh_name = f"BindMesh_{int(time.time())}"

        # Create armature
        armature_handler.create(name=armature_name, bone_length=2.0)

        # Create mesh
        modeling_handler.create_primitive(
            primitive_type="Cube",
            name=mesh_name,
            size=2.0,
        )

        # Bind mesh to armature
        result = armature_handler.bind(
            mesh_name=mesh_name,
            armature_name=armature_name,
        )

        assert "Bound mesh" in result
        assert "bind_type=AUTO" in result
        print(f"✓ armature_bind auto: {result}")

        # Cleanup
        scene_handler.delete_object(mesh_name)
        scene_handler.delete_object(armature_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_armature_bind_envelope(armature_handler, scene_handler, modeling_handler):
    """Test binding mesh with envelope weights."""
    try:
        armature_name = f"EnvArm_{int(time.time())}"
        mesh_name = f"EnvMesh_{int(time.time())}"

        # Create armature
        armature_handler.create(name=armature_name)

        # Create mesh
        modeling_handler.create_primitive(
            primitive_type="Sphere",
            name=mesh_name,
            radius=1.0,
        )

        # Bind mesh to armature
        result = armature_handler.bind(
            mesh_name=mesh_name,
            armature_name=armature_name,
            bind_type="ENVELOPE",
        )

        assert "Bound mesh" in result
        assert "bind_type=ENVELOPE" in result
        print(f"✓ armature_bind envelope: {result}")

        # Cleanup
        scene_handler.delete_object(mesh_name)
        scene_handler.delete_object(armature_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_armature_bind_empty(armature_handler, scene_handler, modeling_handler):
    """Test binding mesh without automatic weights."""
    try:
        armature_name = f"EmptyArm_{int(time.time())}"
        mesh_name = f"EmptyMesh_{int(time.time())}"

        # Create armature
        armature_handler.create(name=armature_name)

        # Create mesh
        modeling_handler.create_primitive(
            primitive_type="Cube",
            name=mesh_name,
        )

        # Bind mesh to armature without weights
        result = armature_handler.bind(
            mesh_name=mesh_name,
            armature_name=armature_name,
            bind_type="EMPTY",
        )

        assert "Bound mesh" in result
        assert "bind_type=EMPTY" in result
        print(f"✓ armature_bind empty: {result}")

        # Cleanup
        scene_handler.delete_object(mesh_name)
        scene_handler.delete_object(armature_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_armature_bind_invalid_type(armature_handler, scene_handler, modeling_handler):
    """Test error handling for invalid bind type."""
    try:
        armature_name = f"InvalidBindArm_{int(time.time())}"
        mesh_name = f"InvalidBindMesh_{int(time.time())}"

        # Create objects
        armature_handler.create(name=armature_name)
        modeling_handler.create_primitive(primitive_type="Cube", name=mesh_name)

        # Try invalid bind type
        try:
            armature_handler.bind(
                mesh_name=mesh_name,
                armature_name=armature_name,
                bind_type="INVALID",
            )
            assert False, "Expected RuntimeError for invalid bind_type"
        except RuntimeError as e:
            if "invalid bind_type" in str(e).lower():
                print("✓ armature_bind properly handles invalid bind_type")
            else:
                raise

        # Cleanup
        scene_handler.delete_object(mesh_name)
        scene_handler.delete_object(armature_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


# ============================================================================
# TASK-037-4: armature_pose_bone Tests
# ============================================================================


def test_armature_pose_bone_rotation(armature_handler, scene_handler):
    """Test posing bone with rotation."""
    try:
        armature_name = f"PoseRotArm_{int(time.time())}"

        # Create armature
        armature_handler.create(name=armature_name, bone_name="TestBone")

        # Pose bone
        result = armature_handler.pose_bone(
            armature_name=armature_name,
            bone_name="TestBone",
            rotation=[45, 0, 0],
        )

        assert "Posed bone 'TestBone'" in result
        assert "rotation=" in result
        print(f"✓ armature_pose_bone rotation: {result}")

        # Cleanup
        scene_handler.delete_object(armature_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_armature_pose_bone_location(armature_handler, scene_handler):
    """Test posing bone with location offset."""
    try:
        armature_name = f"PoseLocArm_{int(time.time())}"

        # Create armature
        armature_handler.create(name=armature_name, bone_name="MoveBone")

        # Pose bone
        result = armature_handler.pose_bone(
            armature_name=armature_name,
            bone_name="MoveBone",
            location=[0.1, 0, 0],
        )

        assert "Posed bone" in result
        assert "location=" in result
        print(f"✓ armature_pose_bone location: {result}")

        # Cleanup
        scene_handler.delete_object(armature_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_armature_pose_bone_scale(armature_handler, scene_handler):
    """Test posing bone with scale."""
    try:
        armature_name = f"PoseScaleArm_{int(time.time())}"

        # Create armature
        armature_handler.create(name=armature_name, bone_name="ScaleBone")

        # Pose bone
        result = armature_handler.pose_bone(
            armature_name=armature_name,
            bone_name="ScaleBone",
            scale=[1.5, 1.5, 1.5],
        )

        assert "Posed bone" in result
        assert "scale=" in result
        print(f"✓ armature_pose_bone scale: {result}")

        # Cleanup
        scene_handler.delete_object(armature_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_armature_pose_bone_not_found(armature_handler, scene_handler):
    """Test error handling for non-existent bone."""
    try:
        armature_name = f"PoseNotFoundArm_{int(time.time())}"

        # Create armature
        armature_handler.create(name=armature_name)

        # Try to pose non-existent bone
        try:
            armature_handler.pose_bone(
                armature_name=armature_name,
                bone_name="NonExistentBone",
                rotation=[45, 0, 0],
            )
            assert False, "Expected RuntimeError for non-existent bone"
        except RuntimeError as e:
            if "not found" in str(e).lower():
                print("✓ armature_pose_bone properly handles non-existent bone")
            else:
                raise

        # Cleanup
        scene_handler.delete_object(armature_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


# ============================================================================
# TASK-037-5: armature_weight_paint_assign Tests
# ============================================================================


def test_armature_weight_paint_assign(armature_handler, scene_handler, modeling_handler, mesh_handler, system_handler):
    """Test assigning weights to selected vertices."""
    try:
        armature_name = f"WeightArm_{int(time.time())}"
        mesh_name = f"WeightMesh_{int(time.time())}"

        # Create armature and mesh
        armature_handler.create(name=armature_name, bone_name="TestBone")
        modeling_handler.create_primitive(primitive_type="Cube", name=mesh_name)

        # Bind mesh to armature with empty weights
        armature_handler.bind(
            mesh_name=mesh_name,
            armature_name=armature_name,
            bind_type="EMPTY",
        )

        # Enter edit mode on mesh
        scene_handler.set_active_object(mesh_name)
        system_handler.set_mode(mode="EDIT")

        # Select all vertices
        mesh_handler.select_all(deselect=False)

        # Assign weight
        result = armature_handler.weight_paint_assign(
            object_name=mesh_name,
            vertex_group="TestBone",
            weight=1.0,
        )

        assert "Assigned weight" in result
        print(f"✓ armature_weight_paint_assign: {result}")

        # Cleanup
        system_handler.set_mode(mode="OBJECT")
        scene_handler.delete_object(mesh_name)
        scene_handler.delete_object(armature_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


# ============================================================================
# Complete Workflow Tests
# ============================================================================


def test_simple_rig_workflow(armature_handler, scene_handler, modeling_handler):
    """Test creating a simple rig: armature with multiple bones bound to mesh."""
    try:
        armature_name = f"SimpleRig_{int(time.time())}"
        mesh_name = f"SimpleMesh_{int(time.time())}"

        # 1. Create armature with root bone
        result1 = armature_handler.create(
            name=armature_name,
            bone_name="Root",
            bone_length=0.5,
        )
        assert "Created armature" in result1
        print(f"  Step 1: Created armature with Root bone")

        # 2. Add spine bone
        result2 = armature_handler.add_bone(
            armature_name=armature_name,
            bone_name="Spine",
            head=[0, 0, 0.5],
            tail=[0, 0, 1.0],
            parent_bone="Root",
            use_connect=True,
        )
        assert "Added bone 'Spine'" in result2
        print(f"  Step 2: Added Spine bone")

        # 3. Add chest bone
        result3 = armature_handler.add_bone(
            armature_name=armature_name,
            bone_name="Chest",
            head=[0, 0, 1.0],
            tail=[0, 0, 1.5],
            parent_bone="Spine",
            use_connect=True,
        )
        assert "Added bone 'Chest'" in result3
        print(f"  Step 3: Added Chest bone")

        # 4. Create mesh to rig
        modeling_handler.create_primitive(
            primitive_type="Cylinder",
            name=mesh_name,
            radius=0.3,
            location=[0, 0, 0.75],
        )
        print(f"  Step 4: Created mesh cylinder")

        # 5. Bind mesh to armature
        result5 = armature_handler.bind(
            mesh_name=mesh_name,
            armature_name=armature_name,
            bind_type="AUTO",
        )
        assert "Bound mesh" in result5
        print(f"  Step 5: Bound mesh to armature")

        # 6. Pose a bone
        result6 = armature_handler.pose_bone(
            armature_name=armature_name,
            bone_name="Spine",
            rotation=[15, 0, 0],
        )
        assert "Posed bone" in result6
        print(f"  Step 6: Posed Spine bone")

        print("✓ Simple rig workflow completed successfully")

        # Cleanup
        scene_handler.delete_object(mesh_name)
        scene_handler.delete_object(armature_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_arm_rig_workflow(armature_handler, scene_handler):
    """Test creating an arm rig with bone chain."""
    try:
        armature_name = f"ArmRig_{int(time.time())}"

        # 1. Create armature with shoulder
        armature_handler.create(
            name=armature_name,
            bone_name="Shoulder",
            bone_length=0.3,
            location=[0.5, 0, 0],
        )
        print(f"  Step 1: Created armature with Shoulder")

        # 2. Add upper arm
        armature_handler.add_bone(
            armature_name=armature_name,
            bone_name="UpperArm",
            head=[0.5, 0, 0],
            tail=[1.0, 0, 0],
            parent_bone="Shoulder",
            use_connect=True,
        )
        print(f"  Step 2: Added UpperArm")

        # 3. Add forearm
        armature_handler.add_bone(
            armature_name=armature_name,
            bone_name="Forearm",
            head=[1.0, 0, 0],
            tail=[1.5, 0, 0],
            parent_bone="UpperArm",
            use_connect=True,
        )
        print(f"  Step 3: Added Forearm")

        # 4. Add hand
        armature_handler.add_bone(
            armature_name=armature_name,
            bone_name="Hand",
            head=[1.5, 0, 0],
            tail=[1.7, 0, 0],
            parent_bone="Forearm",
            use_connect=True,
        )
        print(f"  Step 4: Added Hand")

        # 5. Pose arm (bend at elbow)
        result = armature_handler.pose_bone(
            armature_name=armature_name,
            bone_name="Forearm",
            rotation=[0, 0, -45],
        )
        assert "Posed bone" in result
        print(f"  Step 5: Posed arm at elbow")

        print("✓ Arm rig workflow completed successfully")

        # Cleanup
        scene_handler.delete_object(armature_name)
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "is blender running" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise
