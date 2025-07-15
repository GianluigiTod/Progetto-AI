# interactive_story_generator.py
from lore import LoreDocument
from pddl_template_manager import PDDLTemplateManager
from reflection_agent import ReflectionAgent
from utils import write_to_file
from validation import validate_pddl_syntax, run_fast_downward

class InteractiveStoryGenerator:
    def __init__(self):
        self.template_manager = PDDLTemplateManager()
        self.reflection_agent = ReflectionAgent()
        self.current_lore = None
        self.current_domain = None
        self.current_problem = None

    def create_lore_document(self, interactive: bool = True) -> LoreDocument:
        if interactive:
            desc = input("Descrizione della quest: ")
            ctx = input("Contesto del mondo: ")
            bf_min, bf_max = int(input("Branching min: ")), int(input("Branching max: "))
            d_min, d_max = int(input("Depth min: ")), int(input("Depth max: "))
            chars = input("Personaggi: ").split(',')
            locs = input("Luoghi: ").split(',')
            items = input("Oggetti: ").split(',')
            constr = input("Vincoli: ").split(',')
        else:
            desc = "Un eroe deve liberare un villaggio infestato da banditi."
            ctx = "Regno montano con castelli, grotte e accampamenti."
            bf_min, bf_max = 2, 4
            d_min, d_max = 3, 7
            chars = ["hero", "bandit_leader"]
            locs = ["village", "forest", "camp"]
            items = ["sword", "map"]
            constr = []

        self.current_lore = LoreDocument(desc, (bf_min, bf_max), (d_min, d_max), ctx, chars, locs, items, constr)
        return self.current_lore

    def generate_initial_pddl(self):
        self.current_domain = self.template_manager.generate_domain(self.current_lore)
        self.current_problem = self.template_manager.generate_problem(self.current_lore)
        write_to_file(self.current_domain, "domain.pddl")
        write_to_file(self.current_problem, "problem.pddl")

    def validate_and_refine(self, max_iter=3):
        for i in range(max_iter):
            print(f"\nITERAZIONE {i+1}")
            if not (validate_pddl_syntax(self.current_domain) and validate_pddl_syntax(self.current_problem)):
                print("❌ Sintassi non valida. Provo a correggere...")
                reflection = self.reflection_agent.analyze_pddl_errors(self.current_domain, self.current_problem, ["Errore sintattico"])
                print(reflection["suggestions"])
                continue

            plan = run_fast_downward("output/domain.pddl", "output/problem.pddl", lore=self.current_lore)
            if plan:
                print(f"✅ Piano trovato con {len(plan)} azioni:")
                for a in plan:
                    print(f"  ➤ {a}")
                write_to_file("\n".join(plan), "plan.txt")
                return True

            print("❌ Nessun piano trovato. Suggerimenti:")
            suggestion = self.reflection_agent.suggest_improvements(self.current_lore, self.current_domain, self.current_problem)
            print(suggestion["suggestions"])
            choice = input("Vuoi rigenerare? [y/n]: ").lower()
            if choice == 'y':
                self.generate_initial_pddl()
        return False
