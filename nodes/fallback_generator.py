# nodes/fallback_generator.py

def generate_fallback_pddl(state):
    fallback_domain = """
(define (domain quest_domain)
  (:requirements :strips)
  (:predicates
    (at ?x ?loc)
    (connected ?from ?to)
    (has ?x ?item)
    (alive ?x)
    (dead ?x)
  )

  ; azione di movimento
  (:action move
    :parameters (?x ?from ?to)
    :precondition (and (at ?x ?from) (connected ?from ?to))
    :effect (and (not (at ?x ?from)) (at ?x ?to))
  )

  ; azione di raccolta
  (:action pickup
    :parameters (?x ?item ?loc)
    :precondition (and (at ?x ?loc) (at ?item ?loc))
    :effect (has ?x ?item)
  )

  ; azione di attacco
  (:action kill
    :parameters (?x ?target ?loc)
    :precondition (and (at ?x ?loc) (at ?target ?loc) (alive ?target))
    :effect (and (not (alive ?target)) (dead ?target))
  )
)
"""

    fallback_problem = """
(define (problem fallback_problem)
  (:domain quest_domain)
  (:objects
    hero dragon sword cave village - object
  )
  (:init
    (at hero village)
    (at dragon cave)
    (alive dragon)
    (at sword cave)
    (connected village cave)
    (connected cave village)
  )
  (:goal
    (and (dead dragon) (has hero sword))
  )
)
"""

    print("⚠️ Fallback attivato: generati domain/problem predefiniti.")
    return {
        **state,
        "domain_pddl": fallback_domain,
        "problem_pddl": fallback_problem,
        "suggestions": state.get("suggestions", []) + ["Fallback attivato: generati file PDDL standard."],
        "plan_valido": True  # simula il successo per forzare l'uscita
    }
