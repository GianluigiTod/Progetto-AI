<<<<<<< HEAD

from typing import Dict, List
from example_manager import ExampleManager
from lore_document import LoreDocument
from pddl_template_manager import PDDLTemplateManager
from utils import get_ollama_chain


MODEL_NAME = "mistral"

class ReflectionAgent:

    
    """Agente di riflessione per il miglioramento iterativo del PDDL"""
    
    def __init__(self, model_name: str = MODEL_NAME):
        self.model_name = model_name
        self.template_manager = PDDLTemplateManager()
        self.example_manager = ExampleManager()
    
    def analyze_pddl_errors(self, domain_content: str, problem_content: str, 
                           validation_errors: List[str]) -> Dict[str, str]:
        """Analizza errori nel PDDL e suggerisce correzioni"""
        
        system_msg = f"""Sei un esperto analista PDDL. Il tuo compito è identificare errori specifici nel codice PDDL e suggerire correzioni precise.

{self.example_manager.get_domain_examples_for_prompt()}
{self.example_manager.get_problem_examples_for_prompt()}

REGOLE DI ANALISI:
1. Identifica errori sintattici specifici
2. Verifica coerenza tra dominio e problema
3. Controlla che ogni predicato usato sia dichiarato
4. Verifica che ogni tipo usato sia dichiarato
5. Assicura che le precondizioni siano soddisfacibili
6. Verifica che gli effetti siano consistenti

ERRORI COMUNI DA CERCARE:
- Predicati non dichiarati
- Tipi non dichiarati
- Parametri con arità errata
- Precondizioni impossibili
- Effetti contraddittori
- Parentesi non bilanciate
- Oggetti non tipizzati correttamente

FORNISCI:
1. Lista specifica degli errori trovati
2. Spiegazione del perché sono errori
3. Suggerimenti di correzione precisi
4. Codice PDDL corretto se possibile"""

        user_template = """Analizza questo PDDL e identifica tutti gli errori:

DOMINIO:
{domain_content}

PROBLEMA:
{problem_content}

ERRORI DI VALIDAZIONE:
{validation_errors}

Fornisci un'analisi dettagliata degli errori e suggerimenti specifici per correggerli."""

        chain = get_ollama_chain(system_msg, user_template)
        response = chain.invoke({
            "domain_content": domain_content,
            "problem_content": problem_content,
            "validation_errors": "\n".join(validation_errors)
        })
        
        return self._parse_reflection_response(response.content)
    
    def _parse_reflection_response(self, response: str) -> Dict[str, str]:
        """Analizza la risposta dell'agente di riflessione"""
        sections = {
            "errors": "",
            "explanations": "",
            "suggestions": "",
            "corrected_code": ""
        }
        
        current_section = None
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if 'errori' in line.lower() or 'errors' in line.lower():
                current_section = "errors"
            elif 'spiegazione' in line.lower() or 'explanation' in line.lower():
                current_section = "explanations"
            elif 'suggerimenti' in line.lower() or 'suggestions' in line.lower():
                current_section = "suggestions"
            elif 'corretto' in line.lower() or 'corrected' in line.lower():
                current_section = "corrected_code"
            elif current_section:
                sections[current_section] += line + "\n"
        
        return sections
    
    def suggest_improvements(self, lore_doc: LoreDocument, 
                           current_domain: str, current_problem: str) -> Dict[str, str]:
        """Suggerisce miglioramenti basati sul documento di lore"""
        
        system_msg = f"""Sei un esperto di narrative design e PDDL. Analizza il documento di lore e il PDDL attuale per suggerire miglioramenti che rendano la storia più coerente e interessante.

{self.example_manager.get_domain_examples_for_prompt}
{self.example_manager.get_problem_examples_for_prompt}

CONSIDERA:
1. Coerenza narrativa tra lore e PDDL
2. Complessità adeguata ai vincoli di branching factor
3. Profondità narrativa appropriata
4. Elementi mancanti nella storia
5. Opportunità di miglioramento dell'esperienza

SUGGERISCI:
1. Miglioramenti narrativi
2. Elementi PDDL da aggiungere/modificare
3. Bilanciamento della difficoltà
4. Arricchimento del mondo di gioco"""

        user_template = """DOCUMENTO DI LORE:
Descrizione: {quest_description}
Contesto: {world_context}
Branching Factor: {branching_min}-{branching_max}
Profondità: {depth_min}-{depth_max}
Personaggi: {characters}
Luoghi: {locations}
Oggetti: {items}
Vincoli: {constraints}

DOMINIO ATTUALE:
{current_domain}

PROBLEMA ATTUALE:
{current_problem}

Suggerisci miglioramenti specifici per rendere la storia più ricca e il PDDL più funzionale."""

        chain = get_ollama_chain(system_msg, user_template)
        response = chain.invoke({
            "quest_description": lore_doc.quest_description,
            "world_context": lore_doc.world_context,
            "branching_min": lore_doc.branching_factor[0],
            "branching_max": lore_doc.branching_factor[1],
            "depth_min": lore_doc.depth_constraints[0],
            "depth_max": lore_doc.depth_constraints[1],
            "characters": ", ".join(lore_doc.characters or []),
            "locations": ", ".join(lore_doc.locations or []),
            "items": ", ".join(lore_doc.items or []),
            "constraints": ", ".join(lore_doc.constraints or []),
            "current_domain": current_domain,
            "current_problem": current_problem
        })
        
        return self._parse_improvement_response(response.content)
    
    def _parse_improvement_response(self, response: str) -> Dict[str, str]:
        """Analizza la risposta sui miglioramenti"""
        sections = {
            "narrative_improvements": "",
            "pddl_modifications": "",
            "difficulty_balance": "",
            "world_enrichment": ""
        }
        
        current_section = None
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if 'narrativ' in line.lower():
                current_section = "narrative_improvements"
            elif 'pddl' in line.lower() or 'modific' in line.lower():
                current_section = "pddl_modifications"
            elif 'difficolt' in line.lower() or 'bilanc' in line.lower():
                current_section = "difficulty_balance"
            elif 'mondo' in line.lower() or 'world' in line.lower():
                current_section = "world_enrichment"
            elif current_section:
                sections[current_section] += line + "\n"
        
        return sections
=======
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
>>>>>>> feature-samba
