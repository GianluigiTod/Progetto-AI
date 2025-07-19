from llm_interface import LLMInterface
from pddl_inferencer import PDDLInferencer
from lore import LoreDocument
from pddl_syntax_repair_agent import PDDLSyntaxRepairAgent
from llm_pddl_refiner import LLM_PDDLRefiner
import re

class PDDLTemplateManager:
    def __init__(self):
        self.repairer = PDDLSyntaxRepairAgent()

    def generate_domain(self, lore: LoreDocument, llm: LLMInterface) -> str:
        inferencer = PDDLInferencer(lore, llm)
        llm_refiner = LLM_PDDLRefiner(llm)

        raw_predicates = inferencer.infer_predicates()
        predicates = llm_refiner.refine_predicates(raw_predicates)

        def valid_predicate(p: str) -> bool:
            return '?' in p and p.startswith('(') and p.endswith(')')

        sanitized_preds = [p for p in predicates if valid_predicate(p)]

        essential_preds = {
            "(at ?x - character ?l - location)",
            "(alive ?x - character)",
            "(connected ?from - location ?to - location)"
        }

        all_preds = list(set(sanitized_preds).union(essential_preds))
        pred_block = "\n    ".join(sorted(all_preds))

        actions = inferencer.infer_actions()
        repaired_actions = self.repairer.repair_actions(actions)
        action_block = "\n\n  ".join(repaired_actions)

        domain_template = f"""
(define (domain generated_domain)
  (:requirements :strips :typing)
  (:types character location item)

  (:predicates
    {pred_block}
  )

  {action_block}
)
"""
        return domain_template.strip()

    def generate_problem(self, lore: LoreDocument, llm: LLMInterface) -> str:
        inferencer = PDDLInferencer(lore, llm)
        llm_refiner = LLM_PDDLRefiner(llm)

        goal = inferencer.infer_goal()
        goal = self.repairer.repair_goal(goal)

        # Se contiene parole italiane sospette, usa il raffinatore LLM
        if any(k in goal.lower() for k in ["presente", "trovare", "posizionato"]):
            goal = llm_refiner.refine_goal(goal, [
                "at", "alive", "connected", "has", "in_camp", "in_forest", "in_village", "saved_village"
            ])

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

        problem_template = f"""
(define (problem generated_problem)
  (:domain generated_domain)
  (:objects
    {characters} - character
    {items} - item
    {locations} - location
  )
  (:init
    {init_block}
  )
  (:goal
    {goal}
  )
)
"""
        return problem_template.strip()
