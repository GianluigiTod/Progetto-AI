(define (domain generated_domain)
  (:requirements :strips :typing)
  (:types character location item)

  (:predicates
    (alive ?x - character)
    (at ?x - character ?l - location)
    (at ?x - character ?y - location)
    (at_camp ?x - character)
    (at_castle ?x - character)
    (bandit_in_village ?x - character)
    (bandit_leader_alive ?x - character)
    (bandit_leader_dead ?x - character)
    (connected ?from - location ?to - location)
    (dead ?x - character)
    (has ?x - character ?z - item)
    (has_map ?x - character)
    (has_sword ?x - character)
    (in_forest ?x - character)
    (in_village ?x - character)
  )

  
)