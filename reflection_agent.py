# reflection_agent.py
from typing import Dict, List
from lore import LoreDocument

class ReflectionAgent:
    def __init__(self):
        pass  # In futuro si può collegare a un LLM

    def analyze_pddl_errors(self, domain: str, problem: str, errors: List[str]) -> Dict[str, str]:
        """
        Analizza errori di parsing o logica nei file PDDL.
        """
        return {
            "errors": "Errore di coerenza tra predicati",
            "explanations": "Il predicato 'has' è usato ma non definito nel dominio",
            "suggestions": "Aggiungi il predicato nel blocco (:predicates)",
            "corrected_code": domain  # Per semplicità restituiamo il codice non modificato
        }

    def suggest_improvements(self, lore: LoreDocument, domain: str, problem: str) -> Dict[str, str]:
        """
        Suggerisce miglioramenti narrativi o strutturali se il planner fallisce.
        """
        suggestions = {}
        if lore and lore.quest_description:
            if "uccidere" in lore.quest_description.lower():
                suggestions["narrative_improvements"] = "Inserire una missione secondaria per ottenere un'arma."
                suggestions["pddl_modifications"] = "Aggiungere l'azione 'attack' e l'oggetto 'arma'."
                suggestions["difficulty_balance"] = "Ridurre la forza del nemico nel dominio."
                suggestions["world_enrichment"] = "Aggiungi luogo 'armeria'."
            else:
                suggestions["narrative_improvements"] = "Aggiungere un personaggio alleato."
                suggestions["pddl_modifications"] = "Aggiungere l'azione 'join' e 'assist'."
                suggestions["difficulty_balance"] = "Ridurre i passaggi obbligatori per l'obiettivo."
                suggestions["world_enrichment"] = "Espandi la mappa con un nuovo villaggio."

        return suggestions