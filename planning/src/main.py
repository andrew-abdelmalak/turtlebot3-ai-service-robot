"""Entry point for the TurtleBot3 AI service robot task planning CLI."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from planning.src.cli import run_cli
from planning.src.kb import KnowledgeBase
from planning.src.planner import DEFAULT_OUTPUT_DIR
from planning.src.world_model import connected, objects, rooms


class World:
    """Container pairing static apartment rooms, connectivity, and initial objects."""

    def __init__(self) -> None:
        self.rooms = rooms
        self.objects = objects
        self.connected = connected


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser for the task planning CLI."""
    parser = argparse.ArgumentParser(
        description="TurtleBot3 AI Service Robot PDDL task planning CLI.",
    )
    parser.add_argument(
        "--goal",
        type=str,
        default=None,
        help="Run a single goal non-interactively (e.g. 'at cup storage') and exit.",
    )
    parser.add_argument(
        "--dry-run",
        "--no-ros",
        action="store_true",
        dest="dry_run",
        help="Simulate action execution without invoking ROS 2 or Gazebo.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for planner logs and solution files.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the planning CLI with optional command-line arguments."""
    args = build_parser().parse_args(argv)
    world = World()
    kb = KnowledgeBase(world)
    output_dir = Path(args.output_dir)
    return run_cli(
        kb,
        world,
        dry_run=args.dry_run,
        initial_goal=args.goal,
        domain_path=output_dir / "domain.pddl",
        problem_path=output_dir / "problem.pddl",
        output_dir=output_dir,
    )


if __name__ == "__main__":
    raise SystemExit(main())
