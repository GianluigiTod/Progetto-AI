def get_prompt(parsed: dict):
    system = "Genera un file domain.pddl STRIPS coerente con una storia fantasy. Includi solo azioni necessarie, con parametri ben definiti e commenti su ogni riga."

    user = f"""
Costruisci un file `domain.pddl` che permetta di pianificare azioni coerenti con il seguente contesto:

- Oggetti: {parsed['objects']}
- Stato iniziale: {parsed['init']}
- Goal: {parsed['goal']}
- Branching factor: {parsed['branching_factor']}
- Profondità: {parsed['depth']}

Definisci:
- Predicati essenziali
- 3–5 azioni STRIPS ben formate

Usa commenti per spiegare ogni riga in italiano.
"""
    return system, user
