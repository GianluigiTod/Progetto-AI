from llm_interface import LLMInterface
from typing import Literal

class LLM_PDDLRefiner:
    """
    Usa un LLM per correggere nomi di predicati/goal non dichiarati nel dominio PDDL.
    Lavora SOLO a livello sintattico e semantico, senza aggiunte creative.
    """

    def __init__(self, llm: LLMInterface):
        self.llm = llm

    def refine_goal(self, goal: str, declared_predicates: list[str]) -> str:
        """
        Elimina o corregge predicati non presenti tra quelli dichiarati.
        """
        prompt = f"""
Sei un assistente per la validazione di PDDL.

Ecco la lista dei predicati dichiarati nel dominio:
{chr(10).join(f"- {p}" for p in declared_predicates)}

Ecco il goal attuale (può contenere predicati errati):
{goal}

✅ Compito:
- Rimuovi o correggi i predicati che NON sono nella lista.
- Non aggiungere nulla.
- Restituisci solo il goal corretto, in una singola riga valida PDDL.
- Non usare commenti né spiegazioni.

Risultato:
"""
        return self.llm.run_prompt(prompt).strip()

    def refine_predicates(self, raw_predicates: list[str]) -> list[str]:
        """
        Rimuove predicati non validi (con nomi narrativi, variabili malformate o assenti).
        """
        prompt = """
Sei un assistente PDDL. Ricevi una lista di predicati grezzi e devi restituire solo quelli validi.

Esempi validi:
- (at ?c - character ?l - location)
- (has ?c - character ?i - item)

Esempi NON validi:
- (presente ?c ?l)
- (ha ?c ?i)
- (flame ?c ?i)

REGOLE:
- Tutti i nomi devono essere atomici (nessun accento o verbo italiano).
- Tutti gli argomenti devono avere tipo.
- Tutto deve essere tra parentesi.

Restituisci solo quelli validi, uno per riga:
"""
        input_block = "\n".join(raw_predicates)
        full_prompt = f"{prompt}\n{input_block}"
        cleaned = self.llm.run_prompt(full_prompt).strip()
        return [line.strip() for line in cleaned.splitlines() if line.startswith("(")]
