import json
from prompts.reflection_prompt import get_prompt
from utils.ask_openai import ask_openai
from utils.json_tools import clean_json_output

def reflection_agent(state):
    # 🔍 1. Salva i PDDL falliti prima del refinement
    if state.get("debug", False):
        with open("failed_domain_before_reflection.pddl", "w", encoding="utf-8") as f:
            f.write(state["domain_pddl"])
        with open("failed_problem_before_reflection.pddl", "w", encoding="utf-8") as f:
            f.write(state["problem_pddl"])
        print("📁 Salvati i file PDDL prima del reflection agent (per debugging).")

    # 🧠 2. Prompt per suggerimenti di correzione
    system, user = get_prompt(state)
    result = ask_openai(system, user)

    # 🧹 3. Pulisci output del modello (può essere in ```json```)
    result_cleaned = clean_json_output(result)

    if not result_cleaned:
        print("❌ Errore: la risposta del reflection agent non è un JSON valido.")
        print("🔍 Risposta grezza del modello:\n", result)
        raise ValueError("Reflection agent: JSON parsing failed.")

    # ✅ 4. Parse e ritorno nuovo stato
    parsed = json.loads(result_cleaned)

    return {
        **state,
        "domain_pddl": parsed["domain_pddl"],
        "problem_pddl": parsed["problem_pddl"],
        "suggestions": state.get("suggestions", []) + parsed["suggestions"],
        "iteration": state.get("iteration", 0) + 1
    }
