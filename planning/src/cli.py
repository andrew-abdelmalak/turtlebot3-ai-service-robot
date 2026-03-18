import copy

# --- IMPORT THE NEW EXECUTOR ---
from executor import execute_action 
# -------------------------------

from pddl_generator import write_domain, write_problem
from planner import run_planner
from utils import parse_plan


def parse_goal_input(goal):
    text = goal.strip().lower()
    if not text:
        return None

    if text.startswith("(") and text.endswith(")"):
        return text

    parts = text.split()
    if len(parts) == 2 and parts[0] == "robot-at":
        return f"(robot-at {parts[1]})"
    if len(parts) == 3 and parts[0] == "at":
        return f"(at {parts[1]} {parts[2]})"
    if len(parts) == 2 and parts[0] == "holding":
        return f"(holding {parts[1]})"

    return None


def run_cli(kb, world):
    print("Welcome to the TurtleBot3 AI Service Robot — Task Planning CLI")
    
    while True:
        print("\n--- Current KB ---")
        print("Robot at:", kb.robot_room)
        print("Objects:", kb.objects)
        print("Holding:", kb.holding)

        goal = input("\nEnter goal (or 'quit'): ")

        if goal == "quit":
            break

        parsed_goal = parse_goal_input(goal)
        if not parsed_goal:
            print("Could not understand goal. Examples: 'robot-at kitchen', 'at cup bedroom', '(holding phone)'.")
            continue

        goal_pddl = f"(and {parsed_goal})"

        write_domain()
        write_problem(kb, goal_pddl)

        status, plan_output = run_planner()
        plan = parse_plan(plan_output)

        # Enforce: if a pick is needed while something is held, drop it here before moving.
        if kb.holding and any(step and step[0] == "pick" for step in plan):
            drop_step = ["place", kb.holding, kb.robot_room]

            # Re-plan from the state after the drop so the plan stays consistent.
            temp_kb = copy.deepcopy(kb)
            temp_kb.apply_place(temp_kb.holding)
            write_problem(temp_kb, goal_pddl)
            status, plan_output = run_planner()
            replanned = parse_plan(plan_output)

            if status != 0 or not replanned:
                print("Planner did not return a plan after forcing a drop. See output/plan.txt for details.")
                continue

            plan = [drop_step] + replanned

        if status != 0 or plan is None:
            print("Planner did not return a plan. See output/plan.txt for details.")
            continue

        if len(plan) == 0:
            print("Goal already satisfied. No actions needed.")
            continue

        print("\nPlan found:")
        for step in plan:
            print(step)

        input("\nPress Enter to start execution in Gazebo...")

        # --- EXECUTION LOOP ---
        for step in plan:
            name = step[0]
            args = step[1:]
            
            # 1. Execute Physical Action
            success = execute_action(name, args)
            
            if not success:
                print("CRITICAL: Physical execution failed. Aborting plan.")
                break

            # 2. Update Knowledge Base (Only if physical action succeeded)
            if name == "move":
                kb.apply_move(args[1])
            elif name == "pick":
                kb.apply_pick(args[0])
            elif name == "place":
                kb.apply_place(args[0])
        # ----------------------
