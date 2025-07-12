from langchain.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from pathlib import Path
import subprocess
import re
import os
from typing import List, Optional
import yaml

MODEL_NAME = "mistral"


def get_ollama_chain(system_message: str, user_template: str):
    """Crea una catena LangChain con Ollama"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("human", user_template)
    ])
    return prompt | ChatOllama(model=MODEL_NAME, temperature=0.1, top_p=0.8)

def write_to_file(content: str, filename: str):
    """Scrive contenuto in un file"""
    try:
        Path(filename).write_text(content.strip(), encoding='utf-8')
        print(f"📂 File salvato: {filename}")
        return True
    except Exception as e:
        print(f"❌ Errore scrittura file {filename}: {e}")
        return False
    

    # Funzioni di supporto mancanti da aggiungere al codice principale

import tempfile
import shutil

from lore_document import LoreDocument

def validate_pddl_syntax(pddl_content: str) -> bool:
    """Valida la sintassi PDDL di base"""
    try:
        # Verifica bilanciamento parentesi
        if not _check_parentheses_balance(pddl_content):
            return False
        
        # Verifica presenza di elementi obbligatori
        if "(define" not in pddl_content:
            return False
        
        # Verifica che non ci siano caratteri non validi
        invalid_chars = ['[', ']', '{', '}']
        for char in invalid_chars:
            if char in pddl_content:
                return False
        
        # Verifica struttura di base
        if "(define (domain" in pddl_content:
            return _validate_domain_structure(pddl_content)
        elif "(define (problem" in pddl_content:
            return _validate_problem_structure(pddl_content)
        
        return True
        
    except Exception as e:
        print(f"Errore nella validazione sintattica: {e}")
        return False

def _check_parentheses_balance(text: str) -> bool:
    """Verifica che le parentesi siano bilanciate"""
    count = 0
    for char in text:
        if char == '(':
            count += 1
        elif char == ')':
            count -= 1
            if count < 0:
                return False
    return count == 0

def _validate_domain_structure(domain_content: str) -> bool:
    """Valida la struttura di un dominio PDDL"""
    required_sections = [
        "(:requirements",
        "(:types",
        "(:predicates"
    ]
    
    for section in required_sections:
        if section not in domain_content:
            print(f"Sezione mancante nel dominio: {section}")
            return False
    
    return True

def _validate_problem_structure(problem_content: str) -> bool:
    """Valida la struttura di un problema PDDL"""
    required_sections = [
        "(:domain",
        "(:objects",
        "(:init",
        "(:goal"
    ]
    
    for section in required_sections:
        if section not in problem_content:
            print(f"Sezione mancante nel problema: {section}")
            return False
    
    return True

def extract_pddl_from_response(response: str) -> str:
    """Estrae codice PDDL dalla risposta dell'LLM"""
    # Cerca blocchi di codice PDDL
    patterns = [
        r'```pddl\n(.*?)\n```',
        r'```\n(.*?)\n```',
        r'(\(define.*?\))\s*$'

    ]
    
    for pattern in patterns:
        match = re.search(pattern, response, re.DOTALL)
        if match:
            return match.group(1).strip()
    
    # Se non trova pattern specifici, cerca (define
    start = response.find("(define")
    if start != -1:
        # Trova la fine del blocco PDDL
        end = find_matching_paren(response, start)
        if end != -1:
            return response[start:end+1].strip()
    
    # Se tutto fallisce, restituisce la risposta pulita
    return response.strip()

def find_matching_paren(text: str, start: int) -> int:
    """Trova la parentesi chiusa corrispondente"""
    count = 0
    for i in range(start, len(text)):
        if text[i] == '(':
            count += 1
        elif text[i] == ')':
            count -= 1
            if count == 0:
                return i
    return -1

def run_fast_downward(domain_file: str, problem_file: str, timeout: int = 30) -> Optional[List[str]]:
    """Esegue Fast Downward per trovare un piano"""
    try:
        # Verifica che i file esistano
        if not os.path.exists(domain_file) or not os.path.exists(problem_file):
            print("❌ File dominio o problema non trovati")
            return None
        
        # Comando Fast Downward (assumendo sia installato)
        cmd = [
            "python", "C:\\Users\\Alessandro\\fast_downward\\downward\\fast-downward.py",
            "--plan-file", "sas_plan",
            domain_file,
            problem_file,
            "--search", "astar(lmcut())"
        ]
        
        # Prova prima con un planner alternativo se FD non è disponibile
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            
            if result.returncode == 0 and os.path.exists("sas_plan"):
                return _parse_plan_file("sas_plan")
            else:
                print(f"Fast Downward fallito: {result.stderr}")
                return None
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("⚠️ Fast Downward non disponibile, usando planner simulato")
            return _simulate_planning(domain_file, problem_file)
    
    except Exception as e:
        print(f"❌ Errore nell'esecuzione del planner: {e}")
        return None

def _parse_plan_file(plan_file: str) -> List[str]:
    """Analizza il file del piano generato"""
    try:
        with open(plan_file, 'r') as f:
            lines = f.readlines()
        
        plan = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith(';'):
                # Rimuove parentesi e pulisce l'azione
                action = line.strip('()')
                plan.append(action)
        
        return plan
    
    except Exception as e:
        print(f"Errore nel parsing del piano: {e}")
        return []

def _simulate_planning(domain_file: str, problem_file: str) -> Optional[List[str]]:
    """Simula la pianificazione per test quando FD non è disponibile"""
    print("🔄 Simulazione pianificazione...")
    
    # Legge i file per analisi di base
    try:
        with open(domain_file, 'r') as f:
            domain_content = f.read()
        with open(problem_file, 'r') as f:
            problem_content = f.read()
        
        # Analisi semplificata per generare un piano plausibile
        actions = _extract_actions_from_domain(domain_content)
        goals = _extract_goals_from_problem(problem_content)
        
        if actions and goals:
            # Genera un piano simulato basato su euristica semplice
            simulated_plan = _generate_heuristic_plan(actions, goals)
            print(f"📝 Piano simulato generato: {len(simulated_plan)} azioni")
            return simulated_plan
        
        return None
        
    except Exception as e:
        print(f"Errore nella simulazione: {e}")
        return None

def _extract_actions_from_domain(domain_content: str) -> List[str]:
    """Estrae le azioni dal dominio"""
    actions = []
    lines = domain_content.split('\n')
    
    for line in lines:
        line = line.strip()
        if line.startswith('(:action'):
            action_name = line.split()[1]
            actions.append(action_name)
    
    return actions

def _extract_goals_from_problem(problem_content: str) -> List[str]:
    """Estrae i goal dal problema"""
    goals = []
    
    # Cerca la sezione goal
    goal_start = problem_content.find('(:goal')
    if goal_start != -1:
        goal_end = find_matching_paren(problem_content, goal_start)
        if goal_end != -1:
            goal_section = problem_content[goal_start:goal_end+1]
            # Analisi semplificata dei goal
            goals = re.findall(r'\(\w+[^)]*\)', goal_section)
    
    return goals

def _generate_heuristic_plan(actions: List[str], goals: List[str]) -> List[str]:
    """Genera un piano euristico basato su azioni e goal"""
    plan = []
    
    # Strategia euristica semplice
    common_action_order = ['move', 'take', 'equip', 'unlock', 'fight', 'rescue']
    
    for action_type in common_action_order:
        matching_actions = [a for a in actions if action_type in a.lower()]
        if matching_actions:
            # Aggiunge alcune istanze dell'azione
            for i in range(min(3, len(goals))):
                plan.append(f"{matching_actions[0]} arg{i}")
    
    return plan[:10]  # Limita a 10 azioni per semplicità

def setup_interactive_interface():
    """Configura l'interfaccia interattiva"""
    print("🎮 GENERATORE INTERATTIVO DI STORIE PDDL")
    print("="*50)
    print()
    
    # Verifica dipendenze
    missing_deps = []
    
    try:
        import langchain
        import yaml
    except ImportError as e:
        missing_deps.append(str(e))
    
    if missing_deps:
        print("⚠️ Dipendenze mancanti:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\nInstalla con: pip install langchain pyyaml")
        return False
    
    # Verifica modello Ollama
    try:
        test_model = ChatOllama(model=MODEL_NAME)
        print(f"✅ Modello {MODEL_NAME} disponibile")
    except Exception as e:
        print(f"⚠️ Modello {MODEL_NAME} non disponibile: {e}")
        print("Assicurati che Ollama sia installato e il modello sia scaricato")
        return False
    
    return True

def load_lore_from_file(filename: str) -> LoreDocument:
    """Carica un documento di lore da file YAML"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return LoreDocument(
            quest_description=data.get('quest_description', ''),
            world_context=data.get('world_context', ''),
            branching_factor=tuple(data.get('branching_factor', [2, 5])),
            depth_constraints=tuple(data.get('depth_constraints', [3, 8])),
            characters=data.get('characters', []),
            locations=data.get('locations', []),
            items=data.get('items', []),
            constraints=data.get('constraints', [])
        )
        
    except Exception as e:
        print(f"Errore nel caricamento del file: {e}")
        print("Uso esempio predefinito")
        return LoreDocument(
            quest_description="Avventura di esempio",
            world_context="Mondo fantasy",
            branching_factor=(2, 5),
            depth_constraints=(3, 8)
        )