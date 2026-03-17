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
