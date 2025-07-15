# validation.py (run_fast_downward + validate_pddl_syntax)
import os
import subprocess
from pathlib import Path
from typing import List, Optional
from lore import LoreDocument

def validate_pddl_syntax(pddl_content: str) -> bool:
    """Controlla se il contenuto PDDL ha parentesi bilanciate e contiene 'define'."""
    return "(define" in pddl_content and pddl_content.count('(') == pddl_content.count(')')

def run_fast_downward(domain_file: str, problem_file: str, timeout: int = 30, lore: Optional[LoreDocument] = None) -> Optional[List[str]]:
    """
    Esegue Fast Downward per risolvere il problema PDDL.
    Ritorna lista di azioni se successo, None altrimenti.
    """
    output_dir = Path("output")
    plan_file = output_dir / "sas_plan"

    domain_path = os.path.abspath(domain_file)
    problem_path = os.path.abspath(problem_file)
    fd_script_path = os.path.abspath(os.path.join("fast-downward", "fast-downward.py"))

    try:
        if plan_file.exists():
            plan_file.unlink()

        if not os.path.exists(domain_path) or not os.path.exists(problem_path):
            print(f"❌ File PDDL mancanti:\n  ➤ {domain_path}\n  ➤ {problem_path}")
            return None

        # Esegui Fast Downward
        result = subprocess.run(
            [
                "python", fd_script_path,
                domain_path,
                problem_path,
                "--search", "astar(lmcut())"
            ],
            cwd=".",  # esecuzione da root progetto
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            text=True
        )

        if not plan_file.exists():
            print("⚠️ Fast Downward non ha generato un piano.")
            print("STDOUT:\n", result.stdout)
            print("STDERR:\n", result.stderr)
            return None

        plan_lines = plan_file.read_text(encoding="utf-8").splitlines()
        actions = [line.strip() for line in plan_lines if line and not line.startswith(";")]

        # Salva anche output/plan.txt
        plan_txt = output_dir / "plan.txt"
        plan_txt.write_text("\n".join(actions), encoding="utf-8")

        return actions if actions else None

    except Exception as e:
        print(f"❌ Errore durante esecuzione Fast Downward: {e}")
        return None
