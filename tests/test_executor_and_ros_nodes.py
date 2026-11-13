"""Unit tests for executor command translation and ROS 2 node exit codes."""

from __future__ import annotations

import importlib
import math
import subprocess
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from planning.src.executor import build_ros_command, execute_action

ROS_PKG_ROOT = Path(__file__).resolve().parents[1] / "ros" / "tb3_service_robot"


def _load_ros_module(module_name: str, fake_modules: dict[str, types.ModuleType]):
    """Import a ROS 2 node module under stubbed ROS dependencies."""
    if str(ROS_PKG_ROOT) not in sys.path:
        sys.path.insert(0, str(ROS_PKG_ROOT))
    with patch.dict(sys.modules, fake_modules):
        sys.modules.pop(module_name, None)
        return importlib.import_module(module_name)


def _make_nav_stubs(
    *,
    distances: list[float] | None = None,
    result_value: str = "SUCCEEDED",
):
    """Create stub rclpy, geometry_msgs, and nav2_simple_commander modules."""
    rclpy_mod = types.ModuleType("rclpy")
    rclpy_mod.init = MagicMock()
    rclpy_mod.ok = MagicMock(return_value=True)
    rclpy_mod.shutdown = MagicMock()

    param_node = MagicMock()
    param_node.get_parameter.side_effect = lambda name: types.SimpleNamespace(
        value={"x": 8.5, "y": -1.5, "yaw": 0.0}[name]
    )
    rclpy_mod.create_node = MagicMock(return_value=param_node)

    geometry_mod = types.ModuleType("geometry_msgs")
    geometry_msgs_mod = types.ModuleType("geometry_msgs.msg")

    class PoseStamped:
        def __init__(self) -> None:
            self.header = types.SimpleNamespace(frame_id="", stamp=None)
            self.pose = types.SimpleNamespace(
                position=types.SimpleNamespace(x=0.0, y=0.0),
                orientation=types.SimpleNamespace(x=0.0, y=0.0, z=0.0, w=0.0),
            )

    geometry_msgs_mod.PoseStamped = PoseStamped

    nav2_root = types.ModuleType("nav2_simple_commander")
    nav2_mod = types.ModuleType("nav2_simple_commander.robot_navigator")

    class TaskResult:
        SUCCEEDED = "SUCCEEDED"
        CANCELED = "CANCELED"
        FAILED = "FAILED"

    dist_iter = iter(distances or [])

    class BasicNavigator:
        def get_clock(self):
            return types.SimpleNamespace(now=lambda: types.SimpleNamespace(to_msg=lambda: 0))

        def goToPose(self, pose) -> None:
            self.last_pose = pose

        def isTaskComplete(self) -> bool:
            return not bool(distances)

        def getFeedback(self):
            try:
                return types.SimpleNamespace(distance_remaining=next(dist_iter))
            except StopIteration:
                return None

        def cancelTask(self) -> None:
            self.canceled = True

        def getResult(self):
            return result_value

    nav2_mod.BasicNavigator = BasicNavigator
    nav2_mod.TaskResult = TaskResult

    stubs = {
        "rclpy": rclpy_mod,
        "geometry_msgs": geometry_mod,
        "geometry_msgs.msg": geometry_msgs_mod,
        "nav2_simple_commander": nav2_root,
        "nav2_simple_commander.robot_navigator": nav2_mod,
    }
    return stubs, rclpy_mod, TaskResult


def _make_gripper_stubs(
    *,
    state: str = "open",
    accepted: bool = True,
    result_status: int = 4,
):
    """Create stub rclpy and action message modules for gripper_node."""
    rclpy_mod = types.ModuleType("rclpy")
    rclpy_mod.init = MagicMock()
    rclpy_mod.ok = MagicMock(return_value=True)
    rclpy_mod.shutdown = MagicMock()
    rclpy_mod.spin_until_future_complete = MagicMock()

    rclpy_node_mod = types.ModuleType("rclpy.node")

    class Node:
        def __init__(self, name: str) -> None:
            self.name = name
            self._params: dict[str, object] = {}

        def declare_parameter(self, key: str, default: object) -> None:
            self._params[key] = state if key == "state" else default

        def get_parameter(self, key: str):
            return types.SimpleNamespace(value=self._params[key])

        def destroy_node(self) -> None:
            pass

    rclpy_node_mod.Node = Node

    rclpy_action_mod = types.ModuleType("rclpy.action")

    class ActionClient:
        def __init__(self, node, action_type, topic: str) -> None:
            self.topic = topic

        def wait_for_server(self) -> bool:
            return True

        def send_goal_async(self, goal_msg):
            del goal_msg
            goal_handle = MagicMock()
            goal_handle.accepted = accepted
            result_future = MagicMock()
            result_future.result.return_value = types.SimpleNamespace(status=result_status)
            goal_handle.get_result_async.return_value = result_future
            future = MagicMock()
            future.result.return_value = goal_handle
            return future

    rclpy_action_mod.ActionClient = ActionClient

    action_msgs_root = types.ModuleType("action_msgs")
    action_msgs_mod = types.ModuleType("action_msgs.msg")

    class GoalStatus:
        STATUS_SUCCEEDED = 4
        STATUS_ABORTED = 6

    action_msgs_mod.GoalStatus = GoalStatus

    control_msgs_root = types.ModuleType("control_msgs")
    control_msgs_action = types.ModuleType("control_msgs.action")

    class FollowJointTrajectory:
        class Goal:
            def __init__(self) -> None:
                self.trajectory = types.SimpleNamespace(joint_names=[], points=[])

    class GripperCommand:
        class Goal:
            def __init__(self) -> None:
                self.command = types.SimpleNamespace(position=0.0, max_effort=0.0)

    control_msgs_action.FollowJointTrajectory = FollowJointTrajectory
    control_msgs_action.GripperCommand = GripperCommand

    traj_root = types.ModuleType("trajectory_msgs")
    traj_msgs = types.ModuleType("trajectory_msgs.msg")

    class JointTrajectoryPoint:
        def __init__(self) -> None:
            self.positions = []
            self.time_from_start = types.SimpleNamespace(sec=0)

    traj_msgs.JointTrajectoryPoint = JointTrajectoryPoint

    stubs = {
        "rclpy": rclpy_mod,
        "rclpy.node": rclpy_node_mod,
        "rclpy.action": rclpy_action_mod,
        "action_msgs": action_msgs_root,
        "action_msgs.msg": action_msgs_mod,
        "control_msgs": control_msgs_root,
        "control_msgs.action": control_msgs_action,
        "trajectory_msgs": traj_root,
        "trajectory_msgs.msg": traj_msgs,
    }
    return stubs, rclpy_mod


def test_build_ros_command_and_executor_failure_handling() -> None:
    """Verify ROS 2 command translation and error propagation."""
    move_cmd = build_ros_command("move", ["livingroom", "kitchen"])
    assert move_cmd[:4] == ["ros2", "run", "tb3_service_robot", "navigation_node"]
    assert "x:=8.5" in move_cmd and "y:=-1.5" in move_cmd

    pick_cmd = build_ros_command("pick", ["cup", "kitchen"])
    assert pick_cmd[:4] == ["ros2", "run", "tb3_service_robot", "gripper_node"]
    assert 'state:="close"' in pick_cmd

    place_cmd = build_ros_command("place", ["cup", "storage"])
    assert 'state:="open"' in place_cmd

    with pytest.raises(ValueError, match="not found"):
        build_ros_command("move", ["livingroom", "dining"])
    with pytest.raises(ValueError, match="Unknown action"):
        build_ros_command("spin", [])

    assert execute_action("move", ["livingroom", "kitchen"], dry_run=True) is True
    assert execute_action("move", ["livingroom", "dining"], dry_run=True) is False

    with patch("planning.src.executor.subprocess.run", side_effect=subprocess.CalledProcessError(1, "ros2")):
        assert execute_action("pick", ["cup", "kitchen"], dry_run=False) is False

    with patch("planning.src.executor.subprocess.run", side_effect=FileNotFoundError("ros2")):
        assert execute_action("place", ["cup", "storage"], dry_run=False) is False


def test_navigation_node_quaternion_and_exit_codes() -> None:
    """Verify yaw_to_quaternion and non-zero exit codes on Nav2 cancel/failure."""
    stubs, rclpy_mod, TaskResult = _make_nav_stubs(distances=[0.15])
    nav_mod = _load_ros_module("tb3_service_robot.navigation_node", stubs)

    assert nav_mod.yaw_to_quaternion(0.0) == (0.0, 0.0, 0.0, 1.0)
    qx, qy, qz, qw = nav_mod.yaw_to_quaternion(math.pi / 2.0)
    assert (qx, qy) == (0.0, 0.0)
    assert math.isclose(qz, math.sin(math.pi / 4.0))
    assert math.isclose(qw, math.cos(math.pi / 4.0))

    assert nav_mod.main() == 0
    rclpy_mod.shutdown.assert_called_once()

    for result, expected_code in [
        (TaskResult.SUCCEEDED, 0),
        (TaskResult.CANCELED, 1),
        (TaskResult.FAILED, 1),
        ("UNKNOWN", 1),
    ]:
        stubs, rclpy_mod, _ = _make_nav_stubs(distances=[], result_value=result)
        nav_mod = _load_ros_module("tb3_service_robot.navigation_node", stubs)
        assert nav_mod.main() == expected_code
        rclpy_mod.shutdown.assert_called_once()


def test_gripper_node_exit_codes_on_success_reject_and_failure() -> None:
    """Verify gripper_node returns 0 on success and 1 on invalid state, reject, or failure."""
    with patch("time.sleep"):
        for state, accepted, status, expected in [
            ("open", True, 4, 0),
            ("close", True, 4, 0),
            ("invalid", True, 4, 1),
            ("open", False, 4, 1),
            ("close", True, 6, 1),
        ]:
            stubs, rclpy_mod = _make_gripper_stubs(state=state, accepted=accepted, result_status=status)
            grip_mod = _load_ros_module("tb3_service_robot.gripper_node", stubs)
            assert grip_mod.main() == expected
            rclpy_mod.shutdown.assert_called_once()
