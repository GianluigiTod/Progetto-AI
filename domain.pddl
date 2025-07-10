(define (domain tree_rescue_domain)
(:requirements :strips :typing)
(:types
)
(:predicates
(at ?x - object ?l - location)
(has ?c - character ?i - item)
(alive ?c - character)
(connected ?l1 - location ?l2 - location)
(on-ground ?l - location)
(on-tree ?l - location)
)
(:action climb
:parameters (?c - character ?l - location)
:precondition (and (at ?c ?l) (on-tree ?l) (alive ?c))
:effect (not (on-tree ?l))
)
(:action descend
:parameters (?c - character ?l - location)
:precondition (and (at ?c ?l) (on-ground ?l) (alive ?c))
:effect (not (on-ground ?l))
)
(:action take_ladder
:parameters (?c - character ?l - location)
:precondition (and (at ?c ?l) (at ladder ?l) (alive ?c))
:effect (has ?c ladder)
(not (at ladder ?l))
)
(:action place_ladder
:parameters (?c - character ?l1 - location ?l2 - location)
:precondition (and (at ?c ?l1) (has ?c ladder) (connected ?l1 ?l2) (not (on-ground ?l2)) (not (on-tree ?l2)))
:effect (and (at ladder ?l2) (on-ground ?l2))
)
(:action rescue
:parameters (?c - character ?l - location)
:precondition (and (at ?c ?l) (has ?c ladder) (on-tree cat) (alive ?c) (not (on-ground cat)))
:effect (and (at cat ?l) (on-ground cat))
)
)