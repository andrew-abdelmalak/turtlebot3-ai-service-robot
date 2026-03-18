#!/usr/bin/env python3
import rclpy
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from geometry_msgs.msg import PoseStamped
from tf_transformations import quaternion_from_euler

def main():
    rclpy.init()

    # --- STEP 1: Read Parameters from CLI ---
    param_node = rclpy.create_node('nav_param_reader')
    param_node.declare_parameter('x', 0.0)
    param_node.declare_parameter('y', 0.0)
    param_node.declare_parameter('yaw', 0.0)

    goal_x = param_node.get_parameter('x').value
    goal_y = param_node.get_parameter('y').value
    goal_yaw = param_node.get_parameter('yaw').value
    param_node.destroy_node()

    # --- STEP 2: Execute Navigation ---
    navigator = BasicNavigator()

    # Set the goal pose
    goal_pose = PoseStamped()
    goal_pose.header.frame_id = 'map'
    goal_pose.header.stamp = navigator.get_clock().now().to_msg()
    goal_pose.pose.position.x = float(goal_x)
    goal_pose.pose.position.y = float(goal_y)
    
    # We still need to send a valid orientation to Nav2, even if we don't check it
    q = quaternion_from_euler(0.0, 0.0, float(goal_yaw))
    goal_pose.pose.orientation.x = q[0]
    goal_pose.pose.orientation.y = q[1]
    goal_pose.pose.orientation.z = q[2]
    goal_pose.pose.orientation.w = q[3]

    print(f"Sending Goal: x={goal_x}, y={goal_y} (Orientation ignored for success)")
    navigator.goToPose(goal_pose)

    # --- STEP 3: Monitor Distance Only ---
    DIST_TOLERANCE = 0.30  # meters
    manual_success = False

    while not navigator.isTaskComplete():
        feedback = navigator.getFeedback()
        
        if feedback:
            current_dist = feedback.distance_remaining
            print(f"Distance Remaining: {current_dist:.2f}m", end='\r')

            # CHECK: Distance Only
            if current_dist < DIST_TOLERANCE:
                print("\nTarget reached! (Within distance tolerance).")
                print("Stopping robot...")
                navigator.cancelTask()
                manual_success = True
                break

    # --- STEP 4: Handle Result ---
    if manual_success:
        print("Goal Succeeded (Distance Check)!")
    else:
        result = navigator.getResult()
        if result == TaskResult.SUCCEEDED:
            print("Goal Succeeded (Standard)!")
        elif result == TaskResult.CANCELED:
            print("Goal Canceled!")
        elif result == TaskResult.FAILED:
            print("Goal Failed!")

    rclpy.shutdown()

if __name__ == '__main__':
    main()
