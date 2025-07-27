import subprocess
import tempfile
import os

def validate_with_fast_downward(domain_pddl: str, problem_pddl: str, debug=False):
    with tempfile.TemporaryDirectory() as tmpdir:
        domain_path = os.path.join(tmpdir, "domain.pddl")
        problem_path = os.path.join(tmpdir, "problem.pddl")

        with open(domain_path, "w") as f:
            f.write(domain_pddl)
        with open(problem_path, "w") as f:
            f.write(problem_pddl)

        try:
            result = subprocess.run(
                [
                    "python",
                    "C:\\Users\\Salva\\downward\\fast-downward.py",
                    domain_path,
                    problem_path,
                    "--search", "astar(blind())"
                ],
                capture_output=True,
                text=True,
                timeout=30
            )

            if debug or True:
                print("📤 STDOUT:\n", result.stdout)
                print("❌ STDERR:\n", result.stderr)

            # Cerca il file del piano nella cartella corrente
            plan_file_path = os.path.join(os.getcwd(), "sas_plan")
            if os.path.exists(plan_file_path):
                with open(plan_file_path, "r") as f:
                    lines = f.readlines()

                plan = [line.strip() for line in lines if line.strip() and not line.startswith(";")]

                # Salva il piano come "generated_plan.txt"
                with open("generated_plan.txt", "w") as f_out:
                    f_out.write("\n".join(plan))

                return True, plan

        except Exception as e:
            print("❌ Errore durante l'esecuzione di Fast Downward:", e)

        return False, []
