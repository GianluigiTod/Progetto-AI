from pddl_inferencer import PDDLInferencer
from lore import LoreDocument

class PDDLTemplateManager:
    def generate_domain(self, lore: LoreDocument) -> str:
        inferencer = PDDLInferencer(lore)
        predicates = inferencer.infer_predicates()
        actions = inferencer.infer_actions()

        def valid_predicate(p: str) -> bool:
            # Il predicato deve contenere variabili e parentesi bilanciate
            if '?' not in p:
                return False
            if not (p.startswith('(') and p.endswith(')')):
                return False
            return True

        sanitized_preds = [p for p in predicates if valid_predicate(p)]

        # Predicati essenziali con corretta sintassi
        essential_preds = {
            "(at ?x - character ?l - location)",
            "(alive ?x - character)",
            "(connected ?from - location ?to - location)"
        }

        # Unisci evitando duplicati
        all_preds = list(set(sanitized_preds).union(essential_preds))

        pred_block = "\n    ".join(sorted(all_preds))
        action_block = "\n\n  ".join(actions)

        return f"""(define (domain generated_domain)
  (:requirements :strips :typing)
  (:types character location item - object)
  (:predicates
    {pred_block}
  )

  {action_block}
)
"""

    def generate_problem(self, lore: LoreDocument) -> str:
        inferencer = PDDLInferencer(lore)
        goal = inferencer.infer_goal()

        # Sostituisci eventuali predicati non definiti come 'present' con 'at'
        goal = goal.replace("present", "at")

        # Assicura che il goal sia racchiuso in (and ...)
        goal = goal.strip()
        if not goal.startswith("(and"):
            goal = f"(and {goal})"

        # Oggetti senza '?', con tipi specificati dopo la lista
        characters = " ".join(c.strip() for c in lore.characters)
        items = " ".join(i.strip() for i in lore.items)
        locations = " ".join(l.strip() for l in lore.locations)

        init_lines = []
        start_loc = lore.locations[0].strip()
        end_loc = lore.locations[-1].strip()

        for c in lore.characters:
            init_lines.append(f"(at {c.strip()} {start_loc})")
        for i in lore.items:
            init_lines.append(f"(at {i.strip()} {end_loc})")

        for i in range(len(lore.locations) - 1):
            a = lore.locations[i].strip()
            b = lore.locations[i + 1].strip()
            init_lines.append(f"(connected {a} {b})")
            init_lines.append(f"(connected {b} {a})")

        if lore.characters:
            init_lines.append(f"(alive {lore.characters[0].strip()})")

        init_block = "\n    ".join(init_lines)

        return f"""(define (problem generated_problem)
  (:domain generated_domain)
  (:objects
    {characters} - character
    {items} - item
    {locations} - location
  )
  (:init
    {init_block}
  )
  (:goal {goal})
)
"""
