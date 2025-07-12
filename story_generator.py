# story_generator.py
from lore import LoreDocument
from pddl_template_manager import PDDLTemplateManager
from reflection_agent import ReflectionAgent
from validation import validate_pddl_syntax, run_fast_downward
from utils import write_to_file
import os

class InteractiveStoryGenerator:
    def __init__(self):
        self.template_manager = PDDLTemplateManager()
        self.reflection_agent = ReflectionAgent()
        self.current_lore = None
        self.current_domain = None
        self.current_problem = None

    def create_lore_document(self, interactive: bool = True) -> LoreDocument:
        if interactive:
            print("🎭 CREAZIONE DOCUMENTO DI LORE")
            quest_description = input("📖 Descrizione della quest: ")
            world_context = input("🌍 Contesto del mondo: ")
            branching_min = int(input("Branching min (2-5): "))
            branching_max = int(input("Branching max (4-10): "))
            depth_min = int(input("Profondità min (2-8): "))
            depth_max = int(input("Profondità max (5-15): "))
            characters = [x.strip() for x in input("Personaggi (virgola): ").split(',')]
            locations = [x.strip() for x in input("Luoghi (virgola): ").split(',')]
            items = [x.strip() for x in input("Oggetti (virgola): ").split(',')]
            constraints = [x.strip() for x in input("Vincoli (virgola): ").split(',')]
        else:
            quest_description = "Un eroe deve salvare una principessa intrappolata nel castello."
            world_context = "Regno fantasy medievale."
            branching_min, branching_max = (2, 4)
            depth_min, depth_max = (2, 6)
            characters = ["hero", "princess"]
            locations = ["village", "forest", "castle"]
            items = ["sword", "key"]
            constraints = ["il drago deve essere sconfitto"]

        self.current_lore = LoreDocument(
            quest_description,
            (branching_min, branching_max),
            (depth_min, depth_max),
            world_context,
            characters,
            locations,
            items,
            constraints
        )
        self.current_lore.to_yaml("output/final_lore.yaml")
        return self.current_lore

    def generate_initial_pddl(self):
        print("🏗️ Generazione PDDL iniziale...")
        domain = self.template_manager.generate_domain(self.current_lore)
        problem = self.template_manager.generate_problem(self.current_lore)
        self.current_domain = domain
        self.current_problem = problem
        write_to_file(domain, "domain.pddl")
        write_to_file(problem, "problem.pddl")
        return domain, problem

    def validate_and_refine(self, max_iterations: int = 3):
        print("🔍 Inizio processo di validazione e refinement...")
        for i in range(max_iterations):
            print(f"\n{'='*50}\n🔄 ITERAZIONE {i+1}/{max_iterations}\n{'='*50}")
            domain_file = f"temp_domain_{i}.pddl"
            problem_file = f"temp_problem_{i}.pddl"
            write_to_file(self.current_domain, domain_file)
            write_to_file(self.current_problem, problem_file)

            print("📋 Validazione sintattica...")
            if not validate_pddl_syntax(self.current_domain) or not validate_pddl_syntax(self.current_problem):
                print("❌ Errori di sintassi rilevati nel PDDL")
                continue

            print("🧮 Test di solvibilità tramite planner...")
            plan = run_fast_downward(domain_file, problem_file, lore=self.current_lore)
            if plan:
                print(f"✅ Piano trovato con {len(plan)} azioni!")
                for action in plan:
                    print("  ➤", action)
                write_to_file("\n".join(plan), f"plan_iter_{i}.txt")
                return True
            else:
                print("❌ Nessun piano trovato")
                print("🤝 Avvio agent di riflessione per suggerimenti...")
                suggestions = self.reflection_agent.suggest_improvements(self.current_lore, self.current_domain, self.current_problem)
                for k, v in suggestions.items():
                    print(f"{k.replace('_', ' ').capitalize()}: {v}")
                scelta = input("Accettare suggerimenti e rigenerare? [y/n]: ").lower()
                if scelta == 'y':
                    self.generate_initial_pddl()
        return False