"""Unit tests for KnowledgeBase state transitions and PDDL generation."""

from __future__ import annotations

from pathlib import Path

import pytest

from planning.src.kb import KnowledgeBase
from planning.src.main import World
from planning.src.pddl_generator import (
    DEFAULT_DOMAIN_PATH,
    DEFAULT_PROBLEM_PATH,
    write_domain,
    write_problem,
)


def test_kb_initial_state_and_facts() -> None:
    """Verify initial KnowledgeBase state and generated PDDL :init facts."""
    kb = KnowledgeBase(World())
    assert kb.robot_room == "livingroom"
    assert kb.holding is None
    assert len(kb.known_objects) == 10

    facts = kb.get_init_facts()
    assert "(robot-at livingroom)" in facts
    assert "(at cup kitchen)" in facts
    assert "(connected livingroom diningroom)" in facts
    assert "(handempty)" in facts
    assert not any(f.startswith("(holding ") for f in facts)


def test_kb_invalid_initial_room_raises() -> None:
    """Reject unknown initial rooms immediately."""
    with pytest.raises(ValueError, match="Unknown initial room"):
        KnowledgeBase(World(), initial_room="garage")


def test_kb_move_pick_place_transitions_and_guards() -> None:
    """Verify valid transitions and precondition error checks in KnowledgeBase."""
    kb = KnowledgeBase(World())

    with pytest.raises(ValueError, match="not connected"):
        kb.apply_move("kitchen")
    with pytest.raises(ValueError, match="unknown room"):
        kb.apply_move("garage")
    with pytest.raises(ValueError, match="not 'livingroom'"):
        kb.apply_pick("cup")

    kb.apply_move("diningroom")
    kb.apply_move("kitchen")
    kb.apply_pick("cup")
    assert kb.holding == "cup"
    assert "cup" not in kb.objects
    assert "cup" in kb.known_objects

    facts = kb.get_init_facts()
    assert "(holding cup)" in facts
    assert "(handempty)" not in facts

    with pytest.raises(ValueError, match="already holding"):
        kb.apply_pick("pan")
    with pytest.raises(ValueError, match="when holding 'cup'"):
        kb.apply_place("pan")

    kb.apply_move("diningroom")
    kb.apply_place("cup")
    assert kb.holding is None
    assert kb.objects["cup"] == "diningroom"


def test_pddl_generator_writes_valid_files_and_matches_tracked_canonical(tmp_path: Path) -> None:
    """Verify write_domain and write_problem output and sync with canonical PDDL files."""
    kb = KnowledgeBase(World())
    domain_out = write_domain(tmp_path / "domain.pddl")
    problem_out = write_problem(kb, "(and (at cup storage))", tmp_path / "problem.pddl")

    domain_text = domain_out.read_text(encoding="utf-8")
    problem_text = problem_out.read_text(encoding="utf-8")

    assert "(:types room item)" in domain_text
    assert "(:action move" in domain_text
    assert "(:action pick" in domain_text
    assert "(:action place" in domain_text
    assert "(:goal (and (at cup storage)))" in problem_text

    assert DEFAULT_DOMAIN_PATH.read_text(encoding="utf-8") == domain_text
    assert DEFAULT_PROBLEM_PATH.read_text(encoding="utf-8") == problem_text


def test_write_problem_includes_held_object_in_objects_list(tmp_path: Path) -> None:
    """Ensure a held object remains declared in :objects so place remains grounded."""
    kb = KnowledgeBase(World())
    kb.apply_pick("bottle")
    problem_out = write_problem(kb, "(and (at bottle kitchen))", tmp_path / "held.pddl")
    content = problem_out.read_text(encoding="utf-8")
    assert "bottle" in content.split("(:init", 1)[0]
    assert "(holding bottle)" in content
