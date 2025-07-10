(define (domain princess_rescue)
  (:requirements :strips :typing)
  (:types
    character location item - object
    hero princess dragon guard - character
    weapon shield potion - item
  )
  (:predicates
    (at ?x - object ?l - location)
    (has ?c - character ?i - item)
    (alive ?c - character)
    (imprisoned ?p - princess)
    (rescued ?p - princess)
    (guarded ?l - location)
    (connected ?l1 - location ?l2 - location)
  )
  (:action move
    :parameters (?c - character ?from - location ?to - location)
    :precondition (and (at ?c ?from) (connected ?from ?to) (alive ?c) (not (guarded ?to)))
    :effect (and (not (at ?c ?from)) (at ?c ?to))
  )
  (:action take
    :parameters (?c - character ?i - item ?l - location)
    :precondition (and (at ?c ?l) (at ?i ?l) (alive ?c))
    :effect (and (has ?c ?i) (not (at ?i ?l)))
  )
  (:action equip
    :parameters (?c - character ?w - weapon)
    :precondition (and (has ?c ?w) (alive ?c))
    :effect (equipped ?c ?w)
  )
  (:action fight
    :parameters (?h - hero ?d - dragon ?w - weapon ?l - location)
    :precondition (and (at ?h ?l) (at ?d ?l) (equipped ?h ?w) (alive ?h) (alive ?d))
    :effect (and (defeated ?d) (not (alive ?d)))
  )
  (:action rescue
    :parameters (?h - hero ?p - princess ?l - location)
    :precondition (and (at ?h ?l) (at ?p ?l) (alive ?h) (imprisoned ?p) (not (guarded ?l)))
    :effect (and (rescued ?p) (not (imprisoned ?p)))
  )
  (:action guard
    :parameters (?g - guard ?l - location)
    :precondition (and (at ?g ?l) (alive ?g))
    :effect (guarded ?l)
  )
)

PROBLEMA:
(define (problem princess_rescue_quest)
  (:domain princess_rescue)
  (:objects
    hero1 - hero
    princess1 - princess
    dragon1 - dragon
    guard1 - guard
    sword1 - weapon
    shield1 - shield
    potion1 - potion
    village castle tower treasure - location
  )
  (:init
    (at hero1 village)
    (at princess1 castle)
    (at dragon1 tower)
    (at sword1 village)
    (at shield1 village)
    (at potion1 village)
    (at guard1 castle)
    (alive hero1)
    (alive dragon1)
    (imprisoned princess1)
    (guarded castle)
    (locked treasure)
    (hidden treasure)
    (connected village castle)
    (connected castle tower)
    (connected tower village)
  )
  (:goal (and
    (rescued princess1)
    (at princess1 village)
    (has hero1 treasure)
    (defeated dragon1)
  ))
)