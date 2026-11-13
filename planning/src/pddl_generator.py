"""PDDL domain and problem file generator."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

from planning.src.kb import KnowledgeBase

PLANNING_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DOMAIN_PATH = PLANNING_DIR / "domain" / "domain.pddl"
DEFAULT_PROBLEM_PATH = PLANNING_DIR / "problems" / "problem.pddl"


def write_domain(filename: str | Path = DEFAULT_DOMAIN_PATH) -> Path:
    """Write the apartment PDDL domain definition to ``filename``."""
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    domain_text = (
        dedent(
            """
            (define (domain apartment)
              (:requirements :strips :typing)
              (:types room item)

              (:predicates
                  (robot-at ?r - room)
                  (at ?o - item ?r - room)
                  (handempty)
                  (holding ?o - item)
                  (connected ?r1 - room ?r2 - room)
              )

              (:action move
                  :parameters (?from - room ?to - room)
                  :precondition (and (robot-at ?from) (connected ?from ?to))
                  :effect (and (robot-at ?to) (not (robot-at ?from)))
              )

              (:action pick
                  :parameters (?o - item ?r - room)
                  :precondition (and (robot-at ?r) (at ?o ?r) (handempty))
                  :effect (and (holding ?o) (not (at ?o ?r)) (not (handempty)))
              )

              (:action place
                  :parameters (?o - item ?r - room)
                  :precondition (and (robot-at ?r) (holding ?o))
                  :effect (and (at ?o ?r) (not (holding ?o)) (handempty))
              )
            )
            """
        ).strip()
        + "\n"
    )

    path.write_text(domain_text, encoding="utf-8")
    return path


def write_problem(
    kb: KnowledgeBase,
    goal: str,
    filename: str | Path = DEFAULT_PROBLEM_PATH,
) -> Path:
    """Write a PDDL problem file from ``kb`` and a PDDL ``goal`` expression."""
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)

    init_facts = kb.get_init_facts()
    rooms_str = " ".join(kb.rooms)
    objects_list = list(kb.objects.keys())
    if kb.holding is not None and kb.holding not in objects_list:
        objects_list.append(kb.holding)
    objects_str = " ".join(objects_list)

    lines = [
        "(define (problem apartment-problem)",
        "(:domain apartment)",
        f"(:objects {rooms_str} - room",
        f"          {objects_str} - item)",
        "(:init",
        *[f"  {fact}" for fact in init_facts],
        ")",
        f"(:goal {goal})",
        ")",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
