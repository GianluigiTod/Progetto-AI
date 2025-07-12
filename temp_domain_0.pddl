(define (domain rescue_fantasy)
      (:requirements :strips :typing)
      (:types
        character location item - object
        hero princess dragon guard - character
        sword shield key treasure - item
        village castle tower forest - location
      )
      (:predicates
        (at ?x - object ?l - location)                    ; posizione di oggetti e personaggi
        (connected ?l1 - location ?l2 - location)        ; connessioni tra location
        (has ?c - character ?i - item)                   ; possesso di oggetti
        (alive ?c - character)                           ; stato vitale
        (imprisoned ?p - princess)                       ; stato di prigionia
        (rescued ?p - princess)                          ; stato di salvataggio
        (guarded ?l - location)                          ; location sorvegliata
        (locked ?l - location)                           ; location bloccata
        (injured ?c - character)                         ; stato di ferita
        (healed ?c - character)                          ; stato di guarigione
        (defeated ?d - dragon)                           ; stato di sconfitta del drago
      )

      (:action move
        :parameters (?c - character ?from - location ?to - location)
        :precondition (and
          (at ?c ?from)
          (connected ?from ?to)
          (alive ?c)
          (not (locked ?to))
          (not (guarded ?to))
        )
        :effect (and
          (not (at ?c ?from))
          (at ?c ?to)
        )
      )

      (:action take
        :parameters (?c - character ?i - item ?l - location)
        :precondition (and
          (at ?c ?l)
          (at ?i ?l)
          (alive ?c)
        )
        :effect (and
          (has ?c ?i)
          (not (at ?i ?l))
        )
      )

      (:action unlock_door
        :parameters (?h - hero ?k - key ?l - location)
        :precondition (and
          (at ?h ?l)
          (has ?h ?k)
          (alive ?h)
          (locked ?l)
        )
        :effect (not (locked ?l))
      )

      (:action neutralize_guard
        :parameters (?h - hero ?g - guard ?l - location)
        :precondition (and
          (at ?h ?l)
          (at ?g ?l)
          (alive ?h)
          (alive ?g)
          (guarded ?l)
        )
        :effect (and
          (not (guarded ?l))
          (not (alive ?g))
        )
      )

      (:action free_princess
        :parameters (?h - hero ?p - princess ?l - location)
        :precondition (and
          (at ?h ?l)
          (at ?p ?l)
          (alive ?h)
          (imprisoned ?p)
          (not (guarded ?l))
          (defeated ?d)
        )
        :effect (and
          (not (imprisoned ?p))
          (rescued ?p)
        )
      )

      (:action fight_dragon
        :parameters (?h - hero ?d - dragon ?l - location)
        :precondition (and
          (at ?h ?l)
          (at ?d ?l)
          (alive ?h)
          (alive ?d)
          (defeated ?d)
        )
        :effect (and
          (not (alive ?d))
          (defeated ?d)
        )
      )

      (:action heal
        :parameters (?h - hero ?c - character ?m - medicine)
        :precondition (and
          (has ?h ?m)
          (alive ?h)
          (injured ?c)
        )
        :effect (and
          (healed ?c)
          (not (injured ?c))
        )
      )
   )