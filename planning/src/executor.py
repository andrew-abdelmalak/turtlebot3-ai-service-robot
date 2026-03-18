import subprocess
from world_model import coordinates

def execute_action(action_name, args):
    """
    Translates PDDL actions into ROS 2 system calls.
    """
    print(f"\n[EXECUTOR] Processing Action: {action_name} {args}")

    cmd = []

    if action_name == "move":
        # PDDL: (move ?from ?to) -> args[0]=from, args[1]=to
        target_room = args[1]
        
        if target_room not in coordinates:
            print(f"[ERROR] Coordinates for room '{target_room}' not found in world_model.")
            return False

        # Get coordinates from world_model.py
        x, y = coordinates[target_room]
        yaw = 0.0  # Default orientation (you can add specific yaws to world_model later if needed)

        print(f" -> Navigating to {target_room} at (x={x}, y={y})...")
        
        # Call the Navigation Node
        cmd = [
            "ros2", "run", "tb3_service_robot", "navigation_node",
            "--ros-args", "-p", f"x:={x}", "-p", f"y:={y}", "-p", f"yaw:={yaw}"
        ]

    elif action_name == "pick":
        # PDDL: (pick ?obj ?room)
        print(" -> Closing gripper to pick object...")
        
        # Call the Gripper Node (Close)
        cmd = [
            "ros2", "run", "tb3_service_robot", "gripper_node",
            "--ros-args", "-p", 'state:="close"'
        ]

    elif action_name == "place":
        # PDDL: (place ?obj ?room)
        print(" -> Opening gripper to place object...")
        
        # Call the Gripper Node (Open)
        cmd = [
            "ros2", "run", "tb3_service_robot", "gripper_node",
            "--ros-args", "-p", 'state:="open"'
        ]

    else:
        print(f"[ERROR] Unknown action: {action_name}")
        return False

    # --- EXECUTE THE ROS COMMAND ---
    try:
        # check=True will raise an exception if the ROS node crashes or fails
        subprocess.run(cmd, check=True)
        print(" -> Action Complete.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] ROS Execution failed: {e}")
        return False
