# Copyright 2026 Andrew Abdelmalak
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

"""ROS 2 manipulation client node executing OpenManipulator pick and place sequences."""

import sys
import time

from action_msgs.msg import GoalStatus
from control_msgs.action import FollowJointTrajectory, GripperCommand
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectoryPoint

# Preset poses in radians: [joint1, joint2, joint3, joint4].
ARM_DOWN = [0.0, 0.8, -0.2, 0.6]
ARM_HOME = [0.0, -1.0, 0.3, 0.7]
GRIPPER_CLOSE_POS = -0.01
GRIPPER_OPEN_POS = 0.019


class ManipulatorController(Node):
    """Action client node for arm trajectory and gripper commands."""

    def __init__(self) -> None:
        """Initialize arm and gripper action clients and wait for servers."""
        super().__init__("manipulator_controller")

        self.declare_parameter("state", "open")

        self._arm_client = ActionClient(
            self,
            FollowJointTrajectory,
            "/arm_controller/follow_joint_trajectory",
        )
        self._gripper_client = ActionClient(
            self,
            GripperCommand,
            "/gripper_controller/gripper_cmd",
        )

        print("Waiting for Arm and Gripper servers...")
        self._arm_client.wait_for_server()
        self._gripper_client.wait_for_server()
        print("Servers connected.")

    def send_arm_goal(self, positions: list[float]):
        """Send a joint trajectory goal to the arm controller."""
        goal_msg = FollowJointTrajectory.Goal()
        goal_msg.trajectory.joint_names = ["joint1", "joint2", "joint3", "joint4"]

        point = JointTrajectoryPoint()
        point.positions = positions
        point.time_from_start.sec = 2
        goal_msg.trajectory.points = [point]

        return self._arm_client.send_goal_async(goal_msg)

    def send_gripper_goal(self, position: float):
        """Send a target position command to the gripper controller."""
        goal_msg = GripperCommand.Goal()
        goal_msg.command.position = position
        goal_msg.command.max_effort = 1.0

        return self._gripper_client.send_goal_async(goal_msg)


def main(args=None) -> int:
    """Execute the three-phase arm and gripper sequence and return status code."""
    rclpy.init(args=args)
    node = ManipulatorController()

    try:
        state_param = str(node.get_parameter("state").value).lower()

        if state_param == "close":
            print("--- STARTING PICK SEQUENCE ---")
            steps = [
                ("Moving Arm DOWN", lambda: node.send_arm_goal(ARM_DOWN)),
                ("Closing Gripper", lambda: node.send_gripper_goal(GRIPPER_CLOSE_POS)),
                ("Moving Arm HOME", lambda: node.send_arm_goal(ARM_HOME)),
            ]
        elif state_param == "open":
            print("--- STARTING PLACE SEQUENCE ---")
            steps = [
                ("Moving Arm DOWN", lambda: node.send_arm_goal(ARM_DOWN)),
                ("Opening Gripper", lambda: node.send_gripper_goal(GRIPPER_OPEN_POS)),
                ("Moving Arm HOME", lambda: node.send_arm_goal(ARM_HOME)),
            ]
        else:
            print(f"Invalid state: {state_param}")
            return 1

        for description, action_func in steps:
            print(f" -> {description}...")
            future = action_func()
            rclpy.spin_until_future_complete(node, future)
            goal_handle = future.result()

            if goal_handle is None or not goal_handle.accepted:
                print("    Action rejected!")
                return 1

            result_future = goal_handle.get_result_async()
            rclpy.spin_until_future_complete(node, result_future)
            result_response = result_future.result()
            if result_response is None or result_response.status != GoalStatus.STATUS_SUCCEEDED:
                status = None if result_response is None else result_response.status
                print(f"    Action failed with status: {status}")
                return 1

            print("    Done.")
            time.sleep(0.5)

        print("--- SEQUENCE COMPLETE ---")
        return 0
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    sys.exit(main())
