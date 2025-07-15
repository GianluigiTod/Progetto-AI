# reflection_agent_llm.py
from typing import Dict, List
from lore import LoreDocument
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate

class ReflectionAgent:
    def __init__(self):
        self.llm = ChatOllama(model="mistral")

    def analyze_pddl_errors(self, domain: str, problem: str, errors: List[str]) -> Dict[str, str]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Aiuta a correggere errori nei file PDDL fornendo suggerimenti precisi."),
            ("human", "DOMINIO:\n{domain}\n\nPROBLEMA:\n{problem}\n\nERRORI:\n{errors}\n\nSuggerisci come correggere.")
        ])
        response = prompt | self.llm
        result = response.invoke({"domain": domain, "problem": problem, "errors": "\n".join(errors)}).content
        return {"suggestions": result.strip()}

    def suggest_improvements(self, lore: LoreDocument, domain: str, problem: str) -> Dict[str, str]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Suggerisci miglioramenti narrativi e strutturali basati sul lore e sui file PDDL."),
            ("human", "Lore: {lore}\n\nDomain:\n{domain}\n\nProblem:\n{problem}\n\nSuggerimenti?")
        ])
        response = prompt | self.llm
        result = response.invoke({
            "lore": f"Descrizione: {lore.quest_description}\nContesto: {lore.world_context}",
            "domain": domain,
            "problem": problem
        }).content
        return {"suggestions": result.strip()}