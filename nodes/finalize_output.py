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
    if os.path.exists("plan.txt"):
        print(" - plan.txt (soluzione trovata)")
    else:
        print(" - Nessun piano generato")

    return state
