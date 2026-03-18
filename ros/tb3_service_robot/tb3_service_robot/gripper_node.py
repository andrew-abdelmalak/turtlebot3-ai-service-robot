#!/usr/bin/env python3
import rclpy
import time
from rclpy.node import Node
from rclpy.action import ActionClient
from control_msgs.action import GripperCommand, FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint

# --- PRESET POSES (Joint Angles in Radians) ---
# joint1, joint2, joint3, joint4
# Adjust these if the robot hits the floor or doesn't reach low enough
ARM_DOWN = [0.0, 0.8, -0.2, 0.6]  
ARM_HOME = [0.0, -1.0, 0.3, 0.7]   

class ManipulatorController(Node):
    def __init__(self):
        super().__init__('manipulator_controller')
        
        self.declare_parameter('state', 'open')

        # 1. Arm Action Client
        self._arm_client = ActionClient(
            self, 
            FollowJointTrajectory, 
            '/arm_controller/follow_joint_trajectory'
        )

        # 2. Gripper Action Client
        self._gripper_client = ActionClient(
            self, 
            GripperCommand, 
            '/gripper_controller/gripper_cmd'
        )

        # Wait for servers
        print("Waiting for Arm and Gripper servers...")
        self._arm_client.wait_for_server()
        self._gripper_client.wait_for_server()
        print("Servers connected.")

    def send_arm_goal(self, positions):
        """Send a trajectory to the arm joints"""
        goal_msg = FollowJointTrajectory.Goal()
        goal_msg.trajectory.joint_names = ['joint1', 'joint2', 'joint3', 'joint4']
        
        point = JointTrajectoryPoint()
        point.positions = positions
        point.time_from_start.sec = 2  # Time to move
        
        goal_msg.trajectory.points = [point]
        
        return self._arm_client.send_goal_async(goal_msg)

    def send_gripper_goal(self, position):
        """Send a command to the gripper"""
        goal_msg = GripperCommand.Goal()
        goal_msg.command.position = position
        goal_msg.command.max_effort = 1.0
        
        return self._gripper_client.send_goal_async(goal_msg)

def main(args=None):
    rclpy.init(args=args)
    node = ManipulatorController()

    # Get the desired action (open/place or close/pick)
    state_param = node.get_parameter('state').value.lower()

    # Define the sequence based on the state
    if state_param == 'close':  # PICK SEQUENCE
        print("--- STARTING PICK SEQUENCE ---")
        steps = [
            ("Moving Arm DOWN", lambda: node.send_arm_goal(ARM_DOWN)),
            ("Closing Gripper", lambda: node.send_gripper_goal(-0.01)),
            ("Moving Arm HOME", lambda: node.send_arm_goal(ARM_HOME))
        ]

    elif state_param == 'open': # PLACE SEQUENCE
        print("--- STARTING PLACE SEQUENCE ---")
        steps = [
            ("Moving Arm DOWN", lambda: node.send_arm_goal(ARM_DOWN)),
            ("Opening Gripper", lambda: node.send_gripper_goal(0.019)),
            ("Moving Arm HOME", lambda: node.send_arm_goal(ARM_HOME))
        ]
    
    else:
        print(f"Invalid state: {state_param}")
        return

    # --- EXECUTE STEPS SEQUENTIALLY ---
    for description, action_func in steps:
        print(f" -> {description}...")
        
        # 1. Send the goal
        future = action_func()
        rclpy.spin_until_future_complete(node, future)
        goal_handle = future.result()

        if not goal_handle.accepted:
            print("    Action rejected!")
            break
        
        # 2. Wait for the result (motion to finish)
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(node, result_future)
        print("    Done.")
        
        # Optional: Short pause between moves for stability
        time.sleep(0.5)

    print("--- SEQUENCE COMPLETE ---")
    rclpy.shutdown()

if __name__ == '__main__':
    main()
