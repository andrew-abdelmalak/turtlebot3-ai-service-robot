"""Executor translating symbolic PDDL actions into ROS 2 node invocations."""

from __future__ import annotations

import subprocess
from collections.abc import Sequence

from planning.src.world_model import coordinates

DEFAULT_YAW_RAD = 0.0


def build_ros_command(action_name: str, args: Sequence[str]) -> list[str]:
    """Build the ``ros2 run`` command for a symbolic action, or raise ``ValueError``."""
    if action_name == "move":
        if len(args) != 2:
            raise ValueError(f"'move' expects 2 arguments (from, to), got {list(args)}")
        target_room = args[1]
        if target_room not in coordinates:
            raise ValueError(f"Coordinates for room '{target_room}' not found in world_model.")
        x, y = coordinates[target_room]
        return [
            "ros2",
            "run",
            "tb3_service_robot",
            "navigation_node",
            "--ros-args",
            "-p",
            f"x:={x}",
            "-p",
            f"y:={y}",
            "-p",
            f"yaw:={DEFAULT_YAW_RAD}",
        ]

    if action_name == "pick":
        if len(args) != 2:
            raise ValueError(f"'pick' expects 2 arguments (object, room), got {list(args)}")
        return [
            "ros2",
            "run",
            "tb3_service_robot",
            "gripper_node",
            "--ros-args",
            "-p",
            'state:="close"',
        ]

    if action_name == "place":
        if len(args) != 2:
            raise ValueError(f"'place' expects 2 arguments (object, room), got {list(args)}")
        return [
            "ros2",
            "run",
            "tb3_service_robot",
            "gripper_node",
            "--ros-args",
            "-p",
            'state:="open"',
        ]

    raise ValueError(f"Unknown action: {action_name}")


def execute_action(action_name: str, args: Sequence[str], *, dry_run: bool = False) -> bool:
    """Execute a symbolic PDDL action via ROS 2 (or simulate it in ``dry_run`` mode)."""
    print(f"\n[EXECUTOR] Processing Action: {action_name} {list(args)}")

    try:
        cmd = build_ros_command(action_name, args)
    except ValueError as exc:
        print(f"[ERROR] {exc}")
        return False

    if action_name == "move":
        target_room = args[1]
        x, y = coordinates[target_room]
        print(f" -> Navigating to {target_room} at (x={x}, y={y})...")
    elif action_name == "pick":
        print(" -> Closing gripper to pick object...")
    elif action_name == "place":
        print(" -> Opening gripper to place object...")

    if dry_run:
        print(f" -> [DRY-RUN] Would run: {' '.join(cmd)}")
        print(" -> Action Complete (simulated).")
        return True

    try:
        subprocess.run(cmd, check=True)
        print(" -> Action Complete.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        print(f"[ERROR] ROS Execution failed: {exc}")
        return False
