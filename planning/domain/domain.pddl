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
