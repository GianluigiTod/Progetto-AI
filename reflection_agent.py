from typing import Dict, List
from lore import LoreDocument
from llm_interface import LLMInterface
from langchain.prompts import ChatPromptTemplate
import re

class ReflectionAgent:
    def __init__(self, llm: LLMInterface):
        self.llm = llm

    def analyze_pddl_errors(self, domain: str, problem: str, errors: List[str]) -> Dict[str, str]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Aiuta a correggere errori nei file PDDL fornendo suggerimenti precisi."),
            ("human", "DOMINIO:\n{domain}\n\nPROBLEMA:\n{problem}\n\nERRORI:\n{errors}\n\nSuggerisci come correggere.")
        ])
        formatted = prompt.format_messages(domain=domain, problem=problem, errors="\n".join(errors))
        prompt_text = "\n".join(m.content for m in formatted)
        result = self.llm.run_prompt(prompt_text)
        return {"suggestions": result.strip()}

    def suggest_improvements(self, lore: LoreDocument, domain: str, problem: str) -> Dict[str, str]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Suggerisci solo miglioramenti sintattici e strutturali dei file PDDL."),
            ("human", "Ecco i file PDDL: Lore: {lore}\n\nDomain:\n{domain}\n\nProblem:\n{problem}\n\nSuggerisci solo modifiche sintattiche o errori di struttura. Non suggerire espansioni narrative.")

        ])
        lore_text = f"Descrizione: {lore.quest_description}\nContesto: {lore.world_context}"
        formatted = prompt.format_messages(lore=lore_text, domain=domain, problem=problem)
        prompt_text = "\n".join(m.content for m in formatted)
        result = self.llm.run_prompt(prompt_text)
        return {"suggestions": result.strip()}

    def extract_error_lines(self, pddl_text: str) -> List[str]:
        # Analizza righe sospette (e.g., con variabili tipate male o predicati malformati)
        lines = pddl_text.splitlines()
        return [l for l in lines if re.search(r'\?\w+\s*-', l) or '((' in l or ')' not in l]
