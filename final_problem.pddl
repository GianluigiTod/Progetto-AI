(define (problem my_problem)
  (:domain fantasy-world) ; Specifica il dominio a cui appartiene il problema

  (:objects
    player ; Oggetti coinvolti nel problema
  )

  (:init
    (has-player forcone) ; Stato iniziale: il giocatore possiede il forcone
    (is-dragon) ; Stato iniziale: il drago è in grado di sputare fuoco
  )

  (:goal
    (and
      (dragon-dead) ; Obiettivo: il drago deve essere morto
    )
  )
)