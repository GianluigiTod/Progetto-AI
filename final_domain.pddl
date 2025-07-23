(define (domain fantasy-world)

  ;; Definizione dei tipi
  (:types
    entity location
  )

  ;; Definizione dei predicati
  (:predicates
    (location ?x - entity ?y - entity) ;; L'oggetto ?x si trova nella posizione ?y
    (at ?x - entity ?y - location) ;; L'entità ?x si trova nella posizione ?y
    (has ?x - entity ?y - entity) ;; L'oggetto ?x possiede l'oggetto ?y
    (defeated ?x - entity) ;; La creatura ?x è stata sconfitta
  )

  ;; Azione: Spostare il cavaliere da una posizione all'altra
  (:action move
    :parameters (?from - location ?to - location)
    :precondition (and (at knight ?from))
    :effect (and (not (at knight ?from))
                 (at knight ?to))
    ;; Il cavaliere si sposta da ?from a ?to
  )

  ;; Azione: Combattere il drago
  (:action fight-dragon
    :parameters ()
    :precondition (and (at knight cave) (at dragon cave) (not (defeated dragon)))
    :effect (defeated dragon)
    ;; Il cavaliere sconfigge il drago nella caverna
  )

  ;; Azione: Prendere l'amuleto
  (:action take-amulet
    :parameters ()
    :precondition (and (at knight cave) (location amulet cave) (defeated dragon))
    :effect (and (not (location amulet cave))
                 (has knight amulet))
    ;; Il cavaliere prende l'amuleto dalla caverna dopo aver sconfitto il drago
  )

  ;; Azione: Spostare il drago da una posizione all'altra (opzionale)
  (:action move-dragon
    :parameters (?from - location ?to - location)
    :precondition (and (at dragon ?from) (not (defeated dragon)))
    :effect (and (not (at dragon ?from))
                 (at dragon ?to))
    ;; Il drago si sposta da ?from a ?to
  )
)