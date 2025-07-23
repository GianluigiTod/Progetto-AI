def get_prompt(lore_text: str):
    system = "Sei un analizzatore esperto di narrazioni interattive. Estrai informazioni logiche per costruire un problema PDDL da un testo di lore fantasy."
    user = f"""
Estrai dal seguente testo:
1. Stato iniziale (init): fatti PDDL validi.
2. Goal: fatti PDDL da raggiungere.
3. Oggetti: entità rilevanti (persone, luoghi, oggetti).
4. Branching factor: [min, max]
5. Profondità (depth): [min, max]

Rispondi in JSON con questo schema:
{{
  "init": [...],
  "goal": [...],
  "objects": [...],
  "branching_factor": [min, max],
  "depth": [min, max]
}}

TESTO:
{lore_text}
"""
    return system, user
