(define (problem generated_problem)
  (:domain generated_domain)
  (:objects
    io - character
    pizza - item
     soldi - item
    pizzeria - location
  )
  (:init
    (at io pizzeria)
    (at pizza pizzeria)
    (at  soldi pizzeria)
    
    (alive io)
  )
  (:goal )
)