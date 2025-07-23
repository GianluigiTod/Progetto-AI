(define (problem my_problem)
  (:domain fantasy-world)
  (:objects
    knight - entity  ; il cavaliere che deve compiere la quest
    village - location  ; il villaggio dove inizia il cavaliere
    cave - location  ; la caverna dove si trova il drago e l'amuleto
    dragon - entity  ; il drago che protegge l'amuleto
    amulet - entity  ; l'amuleto che il cavaliere deve ottenere
  )
  (:init
    (at knight village)  ; il cavaliere si trova inizialmente nel villaggio
    (at dragon cave)     ; il drago si trova nella caverna
    (location amulet cave)     ; l'amuleto si trova nella caverna
  )
  (:goal
    (and
      (has knight amulet)      ; il cavaliere deve ottenere l'amuleto
      (defeated dragon)        ; il drago deve essere sconfitto
    )
  )
)