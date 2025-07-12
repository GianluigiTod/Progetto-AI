# src/validation.py
import os
import re
from typing import List, Optional
from lore import LoreDocument
from pddl_inferencer import PDDLInferencer

def validate_pddl_syntax(pddl_content: str) -> bool:
    """Basic check for PDDL formatting correctness."""
    return "(define" in pddl_content and pddl_content.count('(') == pddl_content.count(')')

def run_fast_downward(domain_file: str, problem_file: str, timeout: int = 30, lore: Optional[LoreDocument] = None) -> Optional[List[str]]:
    """
    Simulated planner that returns a dynamically inferred plan based on the lore and inferred actions.
    """
    try:
        if os.path.exists(domain_file) and os.path.exists(problem_file):
            if not lore or not lore.characters or not lore.locations:
                return None

            inferencer = PDDLInferencer(lore)
            goal = inferencer.infer_goal()
            actions = []

            main_char = lore.characters[0].strip()
            target_char = lore.characters[1].strip() if len(lore.characters) > 1 else None
            current_location = lore.locations[0].strip()
            final_location = lore.locations[-1].strip()

            # Muovi verso le location successive
            for loc in lore.locations[1:]:
                actions.append(f"move {main_char} {loc.strip()}")
                current_location = loc.strip()

            # Prendi tutti gli oggetti nella location finale
            for item in lore.items or []:
                actions.append(f"take {main_char} {item.strip()} {current_location}")

            # Rileva il verbo d'azione principale dal goal
            action_verbs = inferencer.infer_actions()
            main_action = None
            for act in action_verbs:
                match = re.search(r"\(:action\s+(\w+)", act)
                if match:
                    action_name = match.group(1)
                    if action_name not in ["move", "take"]:
                        main_action = action_name
                        break

            if main_action and target_char:
                weapon = lore.items[0].strip() if lore.items else "item"
                actions.append(f"{main_action} {main_char} {target_char} {weapon} {current_location}")
            elif lore.items:
                actions.append(f"use {main_char} {lore.items[0].strip()} {current_location}")

            # ✅ Restituisco il piano costruito
            return actions

    except Exception as e:
        print("Errore planner:", e)

    return None

