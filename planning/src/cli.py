"""Interactive and single-goal CLI for symbolic task planning and execution."""

from __future__ import annotations

import copy
from collections.abc import Iterable
from pathlib import Path

from planning.src.executor import execute_action
from planning.src.kb import KnowledgeBase
from planning.src.pddl_generator import (
    DEFAULT_DOMAIN_PATH,
    DEFAULT_PROBLEM_PATH,
    write_domain,
    write_problem,
)
from planning.src.planner import DEFAULT_OUTPUT_DIR, run_planner
from planning.src.utils import parse_plan
from planning.src.world_model import objects as default_objects
from planning.src.world_model import rooms as default_rooms


def parse_goal_input(
    goal: str,
    valid_rooms: Iterable[str] | None = None,
    valid_objects: Iterable[str] | None = None,
) -> str | None:
    """Parse and validate a user goal string into a PDDL goal clause."""
    text = goal.strip().lower()
    if not text:
        return None

    if text.startswith("(") and text.endswith(")"):
        text = text[1:-1].strip()

    parts = text.split()
    rooms_set = set(default_rooms if valid_rooms is None else valid_rooms)
    objects_set = set(default_objects.keys() if valid_objects is None else valid_objects)

    if len(parts) == 2 and parts[0] == "robot-at":
        room = parts[1]
        if room not in rooms_set:
            return None
        return f"(robot-at {room})"

    if len(parts) == 3 and parts[0] == "at":
        obj, room = parts[1], parts[2]
        if obj not in objects_set or room not in rooms_set:
            return None
        return f"(at {obj} {room})"

    if len(parts) == 2 and parts[0] == "holding":
        obj = parts[1]
        if obj not in objects_set:
            return None
        return f"(holding {obj})"

    return None


def _apply_step_to_kb(kb: KnowledgeBase, name: str, args: list[str]) -> None:
    """Apply a confirmed action to the Knowledge Base."""
    if name == "move":
        kb.apply_move(args[1])
    elif name == "pick":
        kb.apply_pick(args[0])
    elif name == "place":
        kb.apply_place(args[0])
    else:
        raise ValueError(f"Unsupported plan action '{name}'")


def _print_kb(kb: KnowledgeBase) -> None:
    print("\n--- Current KB ---")
    print("Robot at:", kb.robot_room)
    print("Objects:", kb.objects)
    print("Holding:", kb.holding)


def plan_and_execute_goal(
    kb: KnowledgeBase,
    goal: str,
    *,
    dry_run: bool = False,
    interactive: bool = True,
    domain_path: str | Path = DEFAULT_DOMAIN_PATH,
    problem_path: str | Path = DEFAULT_PROBLEM_PATH,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
) -> bool:
    """Plan and execute a single goal string, returning ``True`` on success."""
    parsed_goal = parse_goal_input(goal, valid_rooms=kb.rooms, valid_objects=kb.known_objects)
    if not parsed_goal:
        print(
            "Could not understand or validate goal. "
            f"Valid rooms: {', '.join(kb.rooms)}. "
            f"Valid objects: {', '.join(sorted(kb.known_objects))}. "
            "Examples: 'robot-at kitchen', 'at cup storage', '(holding phone)'."
        )
        return False

    goal_pddl = f"(and {parsed_goal})"
    write_domain(domain_path)
    write_problem(kb, goal_pddl, problem_path)

    status, plan_output = run_planner(
        domain_path=domain_path,
        problem_path=problem_path,
        output_dir=output_dir,
    )
    plan = parse_plan(plan_output)

    # Fallback: if the planner failed while holding an item, try dropping it first.
    if (status != 0 or not plan) and kb.holding is not None:
        drop_step = ["place", kb.holding, kb.robot_room]
        temp_kb = copy.deepcopy(kb)
        temp_kb.apply_place(temp_kb.holding)
        write_problem(temp_kb, goal_pddl, problem_path)
        status, plan_output = run_planner(
            domain_path=domain_path,
            problem_path=problem_path,
            output_dir=output_dir,
        )
        replanned = parse_plan(plan_output)
        if status == 0 and replanned:
            plan = [drop_step, *replanned]

    if status != 0:
        print(f"Planner did not return a plan. See {Path(output_dir) / 'plan.txt'} for details.")
        return False

    if len(plan) == 0:
        print("Goal already satisfied. No actions needed.")
        return True

    print("\nPlan found:")
    for step in plan:
        print(step)

    if interactive and not dry_run:
        input("\nPress Enter to start execution in Gazebo...")

    for step in plan:
        name = step[0]
        args = step[1:]
        if not execute_action(name, args, dry_run=dry_run):
            print("CRITICAL: Physical execution failed. Aborting plan.")
            return False
        _apply_step_to_kb(kb, name, args)

    return True


def run_cli(
    kb: KnowledgeBase,
    world: object | None = None,
    *,
    dry_run: bool = False,
    initial_goal: str | None = None,
    domain_path: str | Path = DEFAULT_DOMAIN_PATH,
    problem_path: str | Path = DEFAULT_PROBLEM_PATH,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
) -> int:
    """Run the planning CLI loop or execute a single ``initial_goal``."""
    del world  # World metadata is carried inside ``kb``.
    mode_label = " [DRY-RUN]" if dry_run else ""
    print(f"Welcome to the TurtleBot3 AI Service Robot: Task Planning CLI{mode_label}")

    if initial_goal is not None:
        _print_kb(kb)
        ok = plan_and_execute_goal(
            kb,
            initial_goal,
            dry_run=dry_run,
            interactive=False,
            domain_path=domain_path,
            problem_path=problem_path,
            output_dir=output_dir,
        )
        _print_kb(kb)
        return 0 if ok else 1

    while True:
        _print_kb(kb)
        try:
            goal = input("\nEnter goal (or 'quit'): ")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if goal.strip().lower() == "quit":
            break

        plan_and_execute_goal(
            kb,
            goal,
            dry_run=dry_run,
            interactive=True,
            domain_path=domain_path,
            problem_path=problem_path,
            output_dir=output_dir,
        )

    return 0
