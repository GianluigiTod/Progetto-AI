import re
from typing import List

class PDDLSyntaxRepairAgent:
    """
    Ripulisce e corregge sintatticamente azioni e goal PDDL generati da LLM.
    """

    def repair_actions(self, actions: List[str]) -> List[str]:
        cleaned = []
        for action in actions:
            if not action.startswith("(:action"):
                continue
            if ":parameters" not in action or ":precondition" not in action or ":effect" not in action:
                continue
            action = self._remove_malformed_predicates(action)
            action = self._ensure_parameters_match_variables(action)
            cleaned.append(action.strip())
        return cleaned

    def repair_goal(self, goal: str) -> str:
        # Rimuove tipi dalle variabili (es: ?x - character -> ?x)
        goal = re.sub(r'(\?[a-zA-Z0-9_]+)\s*-\s*[a-zA-Z]+', r'\1', goal)
        # Se è vuoto, fallback minimo
        if not re.search(r'\([^)]+\)', goal):
            return "(and (true))"
        return goal.strip()

    def _remove_malformed_predicates(self, text: str) -> str:
        # Elimina predicati nidificati tipo (has (sword))
        return re.sub(r'\([a-zA-Z0-9_\-]+\s+\([^()]+\)\)', '', text)

    def _ensure_parameters_match_variables(self, action_text: str) -> str:
        # Estrae parametri esistenti
        param_block = re.search(r":parameters\s*\(([^)]*)\)", action_text)
        declared_vars = set()
        if param_block:
            tokens = param_block.group(1).split()
            for i in range(0, len(tokens)-1, 2):
                if tokens[i].startswith("?"):
                    declared_vars.add(tokens[i])

        used_vars = set(re.findall(r"\?\w+", action_text))
        missing = used_vars - declared_vars
        if missing:
            extra = " ".join(f"{v} - object" for v in missing)
            action_text = re.sub(r":parameters\s*\(([^)]*)\)",
                                 lambda m: f":parameters ({m.group(1).strip()} {extra})",
                                 action_text)
        return action_text
