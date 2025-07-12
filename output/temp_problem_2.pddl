;; Problema generato per: devo trafiggere un drago
(define (problem generated_problem)
  (:domain generated_domain)

  ;; Oggetti utilizzati nella storia
  (:objects
    io - character
    drago - character
    forcone - item
    castello - location
    ponte - location
  )

  ;; Stato iniziale della storia
  (:init
    (at io castello)
    (at drago castello)          ;; Posizione iniziale dei personaggi
    (at forcone ponte)          ;; Posizione iniziale degli oggetti
    (connected castello ponte)
    (connected ponte castello)         ;; Connessioni tra i luoghi
    (alive io)  ;; Il protagonista è vivo
  )

  ;; Obiettivo finale della storia
  (:goal (trafiggere io drago))
)