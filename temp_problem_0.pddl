(define (problem dragon_rescue)
     (:objects
       hero1 - hero
       princess1 - princess
       dragon1 - drago
       sword1 - spada
       key1 - chiave
       treasure1 - tesoro
       village castle tower prison - location
     )
     (:init
       (at hero1 village)
       (at princess1 prison)
       (at dragon1 tower)
       (at sword1 village)
       (at key1 forest)
       (at treasure1 castle)

       (alive hero1)
       (imprisoned princess1)
       (alive dragon1)
       (locked prison)
       (hidden treasure1)

       (connected village forest)
       (connected forest village)
       (connected forest castle)
       (connected castle tower)
       (connected tower prison)
       (connected prison tower)
     )
     (:goal (and
             (rescued princess1)
             (at princess1 village)
             (defeated dragon1)
             (has hero1 treasure1)
           ))
     (:action take-key
       :parameters (?x - hero ?y - key)
       :precondition (and
                      (at ?x ?y)
                      (at ?y forest)
                      (alive ?x)
                    )
       :effect (and
                (at ?x ?y)
                (not (at ?y forest))
                (at ?x ?y)
                (not (locked ?y))
              ))
     (:action open-door
       :parameters (?x - hero ?y - location)
       :precondition (and
                      (at ?x ?y)
                      (alive ?x)
                      (locked ?y)
                    )
       :effect (and
                (at ?x ?y)
                (not (locked ?y))
              ))
     (:action fight-dragon
       :parameters (?x - hero)
       :precondition (and
                      (at ?x tower)
                      (alive ?x)
                      (alive dragon1)
                    )
       :effect (if (not (defeated dragon1))
                   (and
                     (at ?x tower)
                     (not (alive dragon1))
                     (defeated dragon1))
                   (and
                     (at ?x village)
                     (not (alive hero1))
                     (defeated dragon1))))
     (:action rescue-princess
       :parameters (?x - hero)
       :precondition (and
                      (at ?x prison)
                      (alive ?x)
                      (rescued princess1)
                    )
       :effect (and
                (at ?x village)
                (not (imprisoned princess1))
                (at princess1 village)
              ))
     (:action get-treasure
       :parameters (?x - hero)
       :precondition (and
                      (at ?x castle)
                      (alive ?x)
                      (has hero1 sword1)
                    )
       :effect (and
                (at ?x castle)
                (not (hidden treasure1))
                (has hero1 treasure1)
              ))
   )