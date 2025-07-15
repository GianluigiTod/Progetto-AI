(define (domain generated_domain)
  (:requirements :strips :typing)
  (:types character location item - object)
  (:predicates
    (?char_bandit_leader - character ?char_bandit_leader - character - character)
    (alive ?char_bandit_leader - character - character)
    (alive ?char_hero - character - character)
    (alive ?x - character)
    (at ?char_hero - character - character ?loc_village - location)
    (at ?x - character ?l - location)
    (connected ?from - location ?to - location)
    (connected ?loc_forest - location ?loc_camp - location - location)
    (connected ?loc_village - location ?loc_forest - location - location)
    (in ?loc_forest - location ?char_bandit_leader - character - location)
  )

  
)