def get_prompt(parsed: dict):
    system = "Genera un file STRIPS PDDL valido (problem.pddl) con commenti, che descrive un problema di pianificazione per una quest fantasy."

    user = f"""
Usa questi dati:
- Oggetti: {parsed['objects']}
- Init: {parsed['init']}
- Goal: {parsed['goal']}

Crea un file PDDL chiamato `problem.pddl`, con struttura:

(define (problem my_problem)
  (:domain quest_domain)
  (:objects
    ; descrizione oggetti
  )
  (:init
    ; stato iniziale
  )
  (:goal
    (and
      ; goal
    )
  )
)

Ogni riga deve essere commentata in italiano.
"""
    return system, user
