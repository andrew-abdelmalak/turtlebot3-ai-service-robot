"""Unit tests for CLI goal parsing, plan parsing, and closed-loop execution."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from planning.src.cli import parse_goal_input, plan_and_execute_goal, run_cli
from planning.src.kb import KnowledgeBase
from planning.src.main import World, main
from planning.src.utils import parse_plan


def test_parse_goal_input_accepts_valid_and_rejects_invalid() -> None:
    """Verify goal validation against world rooms and objects."""
    assert parse_goal_input("robot-at kitchen") == "(robot-at kitchen)"
    assert parse_goal_input("  AT  Cup  Storage ") == "(at cup storage)"
    assert parse_goal_input("(holding phone)") == "(holding phone)"
    assert parse_goal_input("(at cup bedroom)") == "(at cup bedroom)"

    # Previously caused Fast Downward translator exit code 31.
    assert parse_goal_input("robot-at dining") is None
    assert parse_goal_input("at fork kitchen") is None
    assert parse_goal_input("holding pillow") is None
    assert parse_goal_input("(foo bar)") is None
    assert parse_goal_input("") is None
    assert parse_goal_input("move kitchen") is None


def test_parse_plan_handles_various_fast_downward_formats() -> None:
    """Parse standard, numbered, and comment-annotated Fast Downward plan lines."""
    raw = """
    ; comment line
    0: (move livingroom diningroom) (1)
    (move diningroom kitchen)
    (pick cup kitchen) (1)
    ; cost = 3 (unit cost)
    """
    assert parse_plan(raw) == [
        ["move", "livingroom", "diningroom"],
        ["move", "diningroom", "kitchen"],
        ["pick", "cup", "kitchen"],
    ]
    assert parse_plan("") == []


def test_closed_loop_aborts_without_mutating_kb_after_failed_step(tmp_path: Path) -> None:
    """Confirm KB updates stop immediately when a physical action fails."""
    kb = KnowledgeBase(World())
    fake_plan = "(move livingroom diningroom)\n(move diningroom kitchen)\n(pick cup kitchen)\n"

    with (
        patch("planning.src.cli.run_planner", return_value=(0, fake_plan)),
        patch("planning.src.cli.execute_action", side_effect=[True, False]),
    ):
        ok = plan_and_execute_goal(
            kb,
            "at cup storage",
            dry_run=False,
            interactive=False,
            domain_path=tmp_path / "domain.pddl",
            problem_path=tmp_path / "problem.pddl",
            output_dir=tmp_path / "output",
        )

    assert ok is False
    # Step 1 succeeded so robot moved to diningroom; step 2 failed so robot stays there.
    assert kb.robot_room == "diningroom"
    assert kb.holding is None
    assert kb.objects["cup"] == "kitchen"


def test_already_satisfied_goal_skips_execution(tmp_path: Path) -> None:
    """Return True immediately when Fast Downward returns an empty plan."""
    kb = KnowledgeBase(World())
    with (
        patch("planning.src.cli.run_planner", return_value=(0, "; cost = 0\n")),
        patch("planning.src.cli.execute_action") as mock_exec,
    ):
        ok = plan_and_execute_goal(
            kb,
            "robot-at livingroom",
            dry_run=True,
            interactive=False,
            domain_path=tmp_path / "domain.pddl",
            problem_path=tmp_path / "problem.pddl",
            output_dir=tmp_path / "output",
        )

    assert ok is True
    mock_exec.assert_not_called()


def test_holding_object_does_not_replan_when_first_plan_succeeds(tmp_path: Path) -> None:
    """Ensure Fast Downward's single optimal plan is used without redundant re-planning."""
    kb = KnowledgeBase(World())
    kb.apply_pick("bottle")
    plan_text = "(place bottle livingroom)\n(move livingroom bedroom)\n(pick phone bedroom)\n"

    with patch("planning.src.cli.run_planner", return_value=(0, plan_text)) as mock_planner:
        ok = plan_and_execute_goal(
            kb,
            "holding phone",
            dry_run=True,
            interactive=False,
            domain_path=tmp_path / "domain.pddl",
            problem_path=tmp_path / "problem.pddl",
            output_dir=tmp_path / "output",
        )

    assert ok is True
    assert mock_planner.call_count == 1
    assert kb.holding == "phone"
    assert kb.objects["bottle"] == "livingroom"


def test_cli_non_interactive_dry_run_and_eof_exit(tmp_path: Path) -> None:
    """Verify run_cli single-goal return codes and EOFError graceful exit."""
    kb = KnowledgeBase(World())
    with patch("planning.src.cli.run_planner", return_value=(0, "(move livingroom diningroom)\n")):
        code = run_cli(
            kb,
            dry_run=True,
            initial_goal="robot-at diningroom",
            domain_path=tmp_path / "domain.pddl",
            problem_path=tmp_path / "problem.pddl",
            output_dir=tmp_path / "output",
        )
    assert code == 0
    assert kb.robot_room == "diningroom"

    bad_code = main(["--dry-run", "--goal", "robot-at dining", "--output-dir", str(tmp_path / "out")])
    assert bad_code == 1

    with patch("builtins.input", side_effect=EOFError):
        assert run_cli(KnowledgeBase(World()), dry_run=True) == 0
