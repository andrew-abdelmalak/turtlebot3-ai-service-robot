# Copyright 2026 Andrew Abdelmalak
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

"""ROS 2 navigation client node sending Nav2 pose goals with distance tolerance."""

import math
import sys

from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
import rclpy

DIST_TOLERANCE_M = 0.30


def yaw_to_quaternion(yaw: float) -> tuple[float, float, float, float]:
    """Convert planar yaw angle in radians to an (x, y, z, w) quaternion."""
    half_yaw = float(yaw) / 2.0
    return (0.0, 0.0, math.sin(half_yaw), math.cos(half_yaw))


def main() -> int:
    """Read target pose parameters, dispatch Nav2 goal, and return status code."""
    rclpy.init()
    exit_code = 1

    try:
        param_node = rclpy.create_node("nav_param_reader")
        param_node.declare_parameter("x", 0.0)
        param_node.declare_parameter("y", 0.0)
        param_node.declare_parameter("yaw", 0.0)

        goal_x = param_node.get_parameter("x").value
        goal_y = param_node.get_parameter("y").value
        goal_yaw = param_node.get_parameter("yaw").value
        param_node.destroy_node()

        navigator = BasicNavigator()

        goal_pose = PoseStamped()
        goal_pose.header.frame_id = "map"
        goal_pose.header.stamp = navigator.get_clock().now().to_msg()
        goal_pose.pose.position.x = float(goal_x)
        goal_pose.pose.position.y = float(goal_y)

        # Nav2 requires a valid orientation quaternion even when position-only is checked.
        qx, qy, qz, qw = yaw_to_quaternion(float(goal_yaw))
        goal_pose.pose.orientation.x = qx
        goal_pose.pose.orientation.y = qy
        goal_pose.pose.orientation.z = qz
        goal_pose.pose.orientation.w = qw

        print(f"Sending Goal: x={goal_x}, y={goal_y} (Orientation ignored for success)")
        navigator.goToPose(goal_pose)

        manual_success = False
        while not navigator.isTaskComplete():
            feedback = navigator.getFeedback()
            if feedback:
                current_dist = feedback.distance_remaining
                print(f"Distance Remaining: {current_dist:.2f}m", end="\r")

                if current_dist < DIST_TOLERANCE_M:
                    print("\nTarget reached! (Within distance tolerance).")
                    print("Stopping robot...")
                    navigator.cancelTask()
                    manual_success = True
                    break

        if manual_success:
            print("Goal Succeeded (Distance Check)!")
            exit_code = 0
        else:
            result = navigator.getResult()
            if result == TaskResult.SUCCEEDED:
                print("Goal Succeeded (Standard)!")
                exit_code = 0
            elif result == TaskResult.CANCELED:
                print("Goal Canceled!")
                exit_code = 1
            elif result == TaskResult.FAILED:
                print("Goal Failed!")
                exit_code = 1
            else:
                print(f"Unexpected navigation result: {result}")
                exit_code = 1
    finally:
        if rclpy.ok():
            rclpy.shutdown()

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
