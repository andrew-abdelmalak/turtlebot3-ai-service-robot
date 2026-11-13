"""Integration tests running the real Fast Downward planner."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from planning.src.cli import plan_and_execute_goal
from planning.src.kb import KnowledgeBase
from planning.src.main import World
from planning.src.pddl_generator import (
    DEFAULT_DOMAIN_PATH,
    DEFAULT_PROBLEM_PATH,
    write_domain,
    write_problem,
)
from planning.src.planner import run_planner
from planning.src.utils import parse_plan

FAST_DOWNWARD_AVAILABLE = shutil.which("fast-downward") is not None

pytestmark = pytest.mark.skipif(
    not FAST_DOWNWARD_AVAILABLE,
    reason="fast-downward executable not found on PATH",
)


def test_canonical_domain_and_problem_solve_with_zero_warnings(tmp_path: Path) -> None:
    """Solve the tracked canonical PDDL files and confirm the optimal 8-step plan."""
    status, plan_text = run_planner(
        domain_path=DEFAULT_DOMAIN_PATH,
        problem_path=DEFAULT_PROBLEM_PATH,
        output_dir=tmp_path / "output",
    )
    assert status == 0
    log_text = (tmp_path / "output" / "plan.txt").read_text(encoding="utf-8")
    assert "Warning:" not in log_text

    steps = parse_plan(plan_text)
    assert steps == [
        ["move", "livingroom", "diningroom"],
        ["move", "diningroom", "kitchen"],
        ["pick", "cup", "kitchen"],
        ["move", "kitchen", "diningroom"],
        ["move", "diningroom", "livingroom"],
        ["move", "livingroom", "bedroom"],
        ["move", "bedroom", "storage"],
        ["place", "cup", "storage"],
    ]


def test_fast_downward_solves_all_goal_types_and_holding_replan(tmp_path: Path) -> None:
    """Verify robot-at, holding, and picking while already holding another object."""
    domain_path = tmp_path / "domain.pddl"
    problem_path = tmp_path / "problem.pddl"
    output_dir = tmp_path / "output"
    write_domain(domain_path)

    kb = KnowledgeBase(World())
    write_problem(kb, "(and (robot-at kitchen))", problem_path)
    status, plan_text = run_planner(domain_path, problem_path, output_dir)
    assert status == 0
    assert parse_plan(plan_text) == [
        ["move", "livingroom", "diningroom"],
        ["move", "diningroom", "kitchen"],
    ]

    write_problem(kb, "(and (holding phone))", problem_path)
    status, plan_text = run_planner(domain_path, problem_path, output_dir)
    assert status == 0
    assert parse_plan(plan_text) == [
        ["move", "livingroom", "bedroom"],
        ["pick", "phone", "bedroom"],
    ]

    # Holding bottle in livingroom while transferring cup from kitchen to storage.
    kb.apply_pick("bottle")
    ok = plan_and_execute_goal(
        kb,
        "at cup storage",
        dry_run=True,
        interactive=False,
        domain_path=domain_path,
        problem_path=problem_path,
        output_dir=output_dir,
    )
    assert ok is True
    assert kb.holding is None
    assert kb.robot_room == "storage"
    assert kb.objects["bottle"] == "livingroom"
    assert kb.objects["cup"] == "storage"
