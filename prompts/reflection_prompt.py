def get_prompt(state):
    lore = state.get("lore_raw", "")
    domain = state.get("domain_pddl", "")
    problem = state.get("problem_pddl", "")

    system_prompt = "Sei un esperto di pianificazione automatica. Ti occupi di correggere file PDDL non validi per renderli risolvibili da planner classici come Fast Downward."

    user_prompt = f"""Il seguente dominio e problema PDDL non generano alcun piano valido con Fast Downward. Fornisci un JSON con correzioni suggerite e la nuova versione dei file.

RESTITUISCI **SOLO** un oggetto JSON con i seguenti campi:
- "suggestions": lista testuale di modifiche suggerite
- "domain_pddl": nuova versione del dominio
- "problem_pddl": nuova versione del problema

Esempio:
{{
  "suggestions": ["Aggiunta azione per uscire dalla caverna", "Modificato predicato per cavaliere"],
  "domain_pddl": "(define (domain fantasy) ...)",
  "problem_pddl": "(define (problem my_problem) ...)"
}}

### Lore (contesto narrativo)
{lore}

### Dominio PDDL
{domain}

### Problema PDDL
{problem}
"""

    return system_prompt, user_prompt
