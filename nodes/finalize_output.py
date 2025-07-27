import json
import os

def finalize_output(state):
    with open("final_domain.pddl", "w") as f:
        f.write(state["domain_pddl"])
    with open("final_problem.pddl", "w") as f:
        f.write(state["problem_pddl"])
    with open("suggestions_log.json", "w") as f:
        json.dump(state.get("suggestions", []), f, indent=2)
    print("✅ Output scritto su file.")
    print("📁 File salvati:")
    print(" - final_domain.pddl")
    print(" - final_problem.pddl")

    # ✅ Salvataggio piano generato
    if state.get("plan_valido") and "plan" in state:
        with open("generated_plan.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(state["plan"]))
        print(" - generated_plan.txt (piano salvato)")
    elif os.path.exists("plan.txt"):
        print(" - plan.txt (soluzione trovata)")
    else:
        print(" - Nessun piano generato")

    # ✅ (Opzionale) stampa del piano
    if state.get("plan_valido") and "plan" in state:
        print("\n📜 Piano generato:")
        for step in state["plan"]:
            print(" ", step)

    return state
