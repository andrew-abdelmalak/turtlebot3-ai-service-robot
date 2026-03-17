# TurtleBot3 AI Service Robot

An AI-powered service robot that combines **ROS 2 navigation and manipulation** with **PDDL-based task planning**. A TurtleBot3 with an OpenManipulator gripper navigates a simulated apartment in Gazebo, autonomously picking and placing objects across six rooms based on natural-language goals.

## Architecture

The system has three layers:

1. **PDDL Planning** — A CLI accepts high-level goals (e.g. *"move cup to kitchen"*), generates PDDL, and invokes [Fast Downward](https://www.fast-downward.org/) to produce an action plan.
2. **Executor** — Translates each planned action (`move`, `pick`, `place`) into ROS 2 commands by launching the appropriate node with the correct parameters.
3. **ROS 2 Nodes** — `navigation_node` sends goal poses via Nav2, and `gripper_node` controls the OpenManipulator arm and gripper through MoveIt action clients.

## Repository Layout

```
├── planning/
│   ├── src/               # Planning CLI and PDDL pipeline
│   │   ├── main.py        # Entry point — boots world, KB, CLI
│   │   ├── world_model.py # 6-room apartment model with object placement
│   │   ├── kb.py          # In-memory knowledge base (robot/object state)
│   │   ├── pddl_generator.py  # Emits domain + problem PDDL from KB
│   │   ├── planner.py     # Calls Fast Downward solver
│   │   ├── executor.py    # Bridges PDDL actions → ROS 2 commands
│   │   ├── cli.py         # Interactive text UI for goals
│   │   └── utils.py       # Plan parsing helpers
│   ├── domain/            # PDDL domain (move / pick / place actions)
│   ├── problems/          # Generated PDDL problem files
│   ├── output/            # Planner output artifacts
│   └── README.md
├── ros/
│   ├── milestone1_code/   # ROS 2 Python package
│   │   └── milestone1_code/
│   │       ├── navigation_node.py  # Nav2 goal sender
│   │       └── gripper_node.py     # OpenManipulator arm + gripper control
│   └── tb3_course_assets/ # Custom Gazebo world, map, and models
│       ├── maps/          # SLAM-generated occupancy grid
│       ├── models/        # Custom house model for Gazebo
│       └── worlds/        # Gazebo world file
└── docs/
    └── Milestone3_Report.pdf
```

## Prerequisites

| Dependency | Notes |
|---|---|
| **ROS 2 Humble** | With `nav2_simple_commander`, `control_msgs`, `geometry_msgs` |
| **TurtleBot3 packages** | [`turtlebot3_simulations`](https://github.com/ROBOTIS-GIT/turtlebot3_simulations), `turtlebot3_manipulation_*` |
| **Gazebo** | Classic (ROS 2 Humble default) |
| **Fast Downward** | [github.com/aibasel/downward](https://github.com/aibasel/downward) — build and add to `PATH` |
| **Python 3.8+** | For the planning CLI |

## Usage

**1. Launch the simulation environment**

```bash
# Terminal 1 — Gazebo with TurtleBot3 + OpenManipulator
ros2 launch turtlebot3_manipulation_gazebo gazebo.launch.py

# Terminal 2 — MoveIt servo for arm control
ros2 launch turtlebot3_manipulation_moveit_config servo.launch.py

# Terminal 3 — Nav2 with the custom map
ros2 launch turtlebot3_manipulation_navigation2 navigation2.launch.py \
  map_yaml_file:=$HOME/<path-to-repo>/ros/tb3_course_assets/maps/map.yaml
```

**2. Run the planning CLI**

```bash
# Terminal 4
cd planning
python3 src/main.py
```

**3. Enter goals at the prompt**

```
> robot-at kitchen
> at cup bedroom
> holding phone
```

The planner generates a sequence of `move` / `pick` / `place` actions, the executor dispatches each as a ROS 2 node call, and the robot carries out the task in Gazebo.

## World Model

The apartment has **6 rooms** connected by doorways:

| Room | Connected To |
|---|---|
| Kitchen | Dining Room, Living Room |
| Dining Room | Kitchen, Bedroom |
| Living Room | Kitchen, Storage, Bathroom |
| Bedroom | Dining Room, Storage |
| Storage | Living Room, Bedroom, Bathroom |
| Bathroom | Living Room, Storage |

**10 objects** (cup, plate, fork, knife, book, phone, remote, pillow, towel, soap) are distributed across the rooms at startup.

## License

MIT
