(define (domain fantasy-world)

  ;; Definizione degli oggetti nel dominio
  (:constants
    forcone ; Costante per il forcone
  )

  ;; Definizione dei predicati
  (:predicates
    (has-player ?item) ;; Il giocatore possiede un oggetto
    (is-dragon) ;; Lo stato del drago (es. fire-breathing)
    (dragon-dead) ;; Il drago è morto
    (player-near-dragon) ;; Il giocatore è vicino al drago
  )

  ;; Azione: Avvicinarsi al drago
  (:action approach-dragon
    :parameters ()
    :precondition (and (has-player forcone) (is-dragon))
    :effect (player-near-dragon)
    ;; Il giocatore si avvicina al drago solo se ha il forcone e il drago è in grado di sputare fuoco
  )

  ;; Azione: Usare il forcone sul drago
  (:action use-pitchfork
    :parameters ()
    :precondition (and (has-player forcone) (player-near-dragon))
    :effect (and (not (is-dragon)) (dragon-dead))
    ;; Il giocatore usa il forcone sul drago, spegnendo il suo fuoco e uccidendolo
  )

  ;; Azione: Fuggire dal drago
  (:action flee-from-dragon
    :parameters ()
    :precondition (and (is-dragon) (not (player-near-dragon)))
    :effect (not (player-near-dragon))
    ;; Il giocatore fugge dal drago se non è già vicino e il drago è ancora in grado di sputare fuoco
  )
)