;; Problema generato per: devo trafiggere un uomo
(define (problem generated_problem)
  (:domain generated_domain)

  ;; Oggetti utilizzati nella storia
  (:objects
    io - character
    uomo - character
    coltello - item
    pizzeria - location
  )

  ;; Stato iniziale della storia
  (:init
    (at io pizzeria)
    (at uomo pizzeria)          ;; Posizione iniziale dei personaggi
    (at coltello pizzeria)          ;; Posizione iniziale degli oggetti
             ;; Connessioni tra i luoghi
    (alive io)  ;; Il protagonista è vivo
  )

  ;; Obiettivo finale della storia
  (:goal (defeated uomo))
)