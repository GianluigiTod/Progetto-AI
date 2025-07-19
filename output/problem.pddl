(define (problem generated_problem)
  (:domain generated_domain)
  (:objects
    hero bandit_leader - character
    sword map - item
    village forest camp - location
  )
  (:init
    (at hero village)
    (at bandit_leader village)
    (at sword camp)
    (at map camp)
    (connected village forest)
    (connected forest village)
    (connected forest camp)
    (connected camp forest)
    (alive hero)
  )
  (:goal
    (and (not (alive bandit_leader)) (at hero village))
  )
)