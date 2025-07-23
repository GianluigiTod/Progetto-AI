import subprocess
import tempfile
import os

def validate_with_fast_downward(domain_pddl: str, problem_pddl: str, debug=False) -> bool:
    with tempfile.TemporaryDirectory() as tmpdir:
        domain_path = os.path.join(tmpdir, "domain.pddl")
        problem_path = os.path.join(tmpdir, "problem.pddl")
        plan_path = os.path.join(tmpdir, "sas_plan")

        with open(domain_path, "w") as f:
            f.write(domain_pddl)
        with open(problem_path, "w") as f:
            f.write(problem_pddl)

        try:
            result = subprocess.run(
                [
                    "python",
                    "C:\\Users\\Alessandro\\fast_downward\\downward\\fast-downward.py",
                    domain_path,
                    problem_path,
                    "--search", f"astar(blind())"
                ],
                capture_output=True,
                text=True,
                timeout=15
            )

            if debug:
                print("📤 Fast Downward output:\n", result.stdout)

            # Se il planner ha trovato una soluzione, copia il piano
            if "Solution found!" in result.stdout:
                final_plan_path = os.path.join(os.getcwd(), "plan.txt")
                if os.path.exists(plan_path):
                    with open(plan_path, "r") as src, open(final_plan_path, "w") as dst:
                        dst.write(src.read())
                return True

        except Exception as e:
            print("❌ Errore planner:", e)

        return False
