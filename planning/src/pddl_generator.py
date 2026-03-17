from pathlib import Path
from textwrap import dedent


def write_domain(filename="domain/domain.pddl"):
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    domain_text = dedent(
        """
        (define (domain apartment)
          (:requirements :strips :typing)
          (:types room object)

          (:predicates
              (room ?r - room)
              (robot-at ?r - room)
              (object ?o - object)
              (at ?o - object ?r - room)
              (handempty)
              (holding ?o - object)
              (connected ?r1 - room ?r2 - room)
          )

          (:action move
              :parameters (?from - room ?to - room)
              :precondition (and (room ?from) (room ?to) (robot-at ?from) (connected ?from ?to))
              :effect (and (robot-at ?to) (not (robot-at ?from)))
          )

          (:action pick
              :parameters (?o - object ?r - room)
              :precondition (and (room ?r) (object ?o) (robot-at ?r) (at ?o ?r) (handempty))
              :effect (and (holding ?o) (not (at ?o ?r)) (not (handempty)))
          )

          (:action place
              :parameters (?o - object ?r - room)
              :precondition (and (room ?r) (object ?o) (robot-at ?r) (holding ?o))
              :effect (and (at ?o ?r) (not (holding ?o)) (handempty))
          )
        )
        """
    ).strip() + "\n"

    path.write_text(domain_text)


def write_problem(kb, goal, filename="problems/problem.pddl"):
    init_facts = kb.get_init_facts()

    rooms_str = " ".join(kb.rooms)
    objects_str = " ".join(list(kb.objects.keys()))
    if kb.holding:
        objects_str += f" {kb.holding}"

    with open(filename, "w") as f:
        f.write("(define (problem apartment-problem)\n")
        f.write("(:domain apartment)\n")

        f.write(f"(:objects {rooms_str} - room\n")
        f.write(f"          {objects_str} - object)\n")

        f.write("(:init\n")
        for fact in init_facts:
            f.write(f"  {fact}\n")
        f.write(")\n")

        f.write(f"(:goal {goal})\n")
        f.write(")")
