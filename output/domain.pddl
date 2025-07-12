;; Dominio generato per: devo trafiggere un uomo
(define (domain generated_domain)
  (:requirements :strips :typing)
  ;; Tipi per personaggi, oggetti e luoghi
  (:types character location item - object)

  ;; Predicati per rappresentare lo stato
  (:predicates
    (defeated ?x - character)
    (at ?x - object ?l - location)
    (alive ?c - character)
    (has ?c - character ?i - item)
    (connected ?l1 - location ?l2 - location)
  )

  ;; Azioni dedotte dalla descrizione
  
  (:action move
    :parameters (?c - character ?from - location ?to - location)
    :precondition (and (at ?c ?from) (connected ?from ?to) (alive ?c))
    :effect (and (not (at ?c ?from)) (at ?c ?to))
  )

  (:action take
    :parameters (?c - character ?i - item ?l - location)
    :precondition (and (at ?c ?l) (at ?i ?l) (alive ?c))
    :effect (and (has ?c ?i) (not (at ?i ?l)))
  )

  (:action trafiggere
    :parameters (?c - character ?o - character ?w - item ?l - location)
    :precondition (and (at ?c ?l) (at ?o ?l) (has ?c ?w) (alive ?c) (alive ?o))
    :effect (and (not (alive ?o)) (defeated ?o))
  )
)