# pddl_template_manager.py
from lore import LoreDocument
from pddl_inferencer import PDDLInferencer

class PDDLTemplateManager:
    def generate_domain(self, lore: LoreDocument) -> str:
        """Genera il contenuto del file domain.pddl con commenti."""
        inferencer = PDDLInferencer(lore)
        predicates = inferencer.infer_predicates()
        actions = inferencer.infer_actions()

        predicates_str = "\n    ".join(predicates)
        actions_str = "\n".join(actions)

        return f"""
;; Dominio generato per: {lore.quest_description}
(define (domain generated_domain)
  (:requirements :strips :typing)
  ;; Tipi per personaggi, oggetti e luoghi
  (:types character location item - object)

  ;; Predicati per rappresentare lo stato
  (:predicates
    {predicates_str}
  )

  ;; Azioni dedotte dalla descrizione
  {actions_str}
)
"""

    def generate_problem(self, lore: LoreDocument) -> str:
        """Genera il contenuto del file problem.pddl con commenti."""
        inferencer = PDDLInferencer(lore)
        goal = inferencer.infer_goal()

        characters = "\n    ".join([f"{char} - character" for char in lore.characters])
        items = "\n    ".join([f"{item} - item" for item in lore.items])
        locations = "\n    ".join([f"{loc} - location" for loc in lore.locations])

        init_chars = "\n    ".join([f"(at {char} {lore.locations[0]})" for char in lore.characters])
        init_items = "\n    ".join([f"(at {item} {lore.locations[-1]})" for item in lore.items])
        connections = "\n    ".join([
            f"(connected {lore.locations[i]} {lore.locations[i+1]})\n    (connected {lore.locations[i+1]} {lore.locations[i]})"
            for i in range(len(lore.locations)-1)
        ])

        return f"""
;; Problema generato per: {lore.quest_description}
(define (problem generated_problem)
  (:domain generated_domain)

  ;; Oggetti utilizzati nella storia
  (:objects
    {characters}
    {items}
    {locations}
  )

  ;; Stato iniziale della storia
  (:init
    {init_chars}          ;; Posizione iniziale dei personaggi
    {init_items}          ;; Posizione iniziale degli oggetti
    {connections}         ;; Connessioni tra i luoghi
    (alive {lore.characters[0]})  ;; Il protagonista è vivo
  )

  ;; Obiettivo finale della storia
  (:goal {goal})
)
"""