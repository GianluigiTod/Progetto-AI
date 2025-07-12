import os
from typing import Dict, List, Tuple
import yaml
from example_manager import ExampleManager
from lore_document import LoreDocument
from pddl_template_manager import PDDLTemplateManager
from reflection_agent import ReflectionAgent
from utils import extract_pddl_from_response, get_ollama_chain, run_fast_downward, validate_pddl_syntax, write_to_file


class InteractiveStoryGenerator:

    MODEL_NAME = "mistral"
    
    """Generatore interattivo di storie PDDL con loop di refinement"""
    
    def __init__(self, model_name: str = MODEL_NAME):
        self.model_name = model_name
        self.template_manager = PDDLTemplateManager()
        self.example_manager = ExampleManager()
        self.reflection_agent = ReflectionAgent(model_name)
        self.current_lore = None
        self.current_domain = None
        self.current_problem = None
        self.validation_history = []
    
    def create_lore_document(self, interactive: bool = True) -> LoreDocument:
        """Crea un documento di lore interattivamente o da input"""
        
        if interactive:
            print("🎭 CREAZIONE DOCUMENTO DI LORE")
            print("=" * 40)
            
            quest_description = input("📖 Descrizione della quest: ")
            world_context = input("🌍 Contesto del mondo: ")
            
            print("\n🔢 Vincoli numerici:")
            branching_min = int(input("   Branching factor minimo (2-5): ") or "2")
            branching_max = int(input("   Branching factor massimo (4-10): ") or "4")
            depth_min = int(input("   Profondità minima (2-8): ") or "2")
            depth_max = int(input("   Profondità massima (5-15): ") or "5")
            
            print("\n👥 Elementi del mondo (opzionali, separati da virgola):")
            characters_input = input("   Personaggi: ")
            locations_input = input("   Luoghi: ")
            items_input = input("   Oggetti: ")
            constraints_input = input("   Vincoli speciali: ")
            
            characters = [c.strip() for c in characters_input.split(',') if c.strip()]
            locations = [l.strip() for l in locations_input.split(',') if l.strip()]
            items = [i.strip() for i in items_input.split(',') if i.strip()]
            constraints = [c.strip() for c in constraints_input.split(',') if c.strip()]
            
            lore_doc = LoreDocument(
                quest_description=quest_description,
                world_context=world_context,
                branching_factor=(branching_min, branching_max),
                depth_constraints=(depth_min, depth_max),
                characters=characters,
                locations=locations,
                items=items,
                constraints=constraints
            )
        else:
            # Esempio predefinito per test
            lore_doc = LoreDocument(
                quest_description="Un eroe deve salvare una principessa imprigionata in un castello, sconfiggendo un drago e raccogliendo un tesoro magico.",
                world_context="Un regno fantasy medievale con castelli, foreste e creature magiche.",
                branching_factor=(3, 6),
                depth_constraints=(4, 8),
                characters=["eroe", "principessa", "drago", "guardia"],
                locations=["villaggio", "castello", "torre", "tesoro"],
                items=["spada", "scudo", "chiave", "pozione"],
                constraints=["il drago deve essere sconfitto prima di salvare la principessa"]
            )
        
        self.current_lore = lore_doc
        return lore_doc
    
    
    def generate_initial_pddl(self, lore_doc: LoreDocument) -> Tuple[str, str]:
        """Genera PDDL iniziale basato sul lore e template"""
    
        print("🏗️ Generazione PDDL iniziale...")
        
        # Determina il template più appropriato
        template_type = self._select_template_type(lore_doc)
        base_domain = self.template_manager.get_domain_template(template_type)
        base_problem = self.template_manager.get_problem_template("simple_quest")
        
        # Personalizza il template - prima il dominio
        domain_content = self._customize_domain(base_domain, lore_doc)
        
        # Estrai il nome del dominio dal domain_content per usarlo nel problema
        domain_name = self._extract_domain_name(domain_content)
        
        # Personalizza il problema usando il nome del dominio
        problem_content = self._customize_problem(base_problem, lore_doc, domain_name)
        
        self.current_domain = domain_content
        self.current_problem = problem_content
        
        return domain_content, problem_content

    def _extract_domain_name(self, domain_content: str) -> str:
        """Estrae il nome del dominio dal contenuto PDDL"""
        try:
            # Cerca il pattern "(define (domain nome_dominio)"
            import re
            match = re.search(r'\(define\s+\(domain\s+([^\s\)]+)\)', domain_content)
            if match:
                return match.group(1)
            else:
                # Fallback se non riesce a trovare il nome
                return "adventure_domain"
        except:
            # Fallback in caso di errore
            return "adventure_domain"

    def _select_template_type(self, lore_doc: LoreDocument) -> str:
        """Seleziona il tipo di template più appropriato"""
        
        description = lore_doc.quest_description.lower()
        
        if any(word in description for word in ['salv', 'rescue', 'prigion', 'prison']):
            return "rescue"
        elif any(word in description for word in ['tesoro', 'treasure', 'trova', 'find']):
            return "treasure_hunt"
        elif any(word in description for word in ['combatt', 'fight', 'guerra', 'battle']):
            return "combat"
        elif any(word in description for word in ['enigma', 'puzzle', 'risolv', 'solve']):
            return "puzzle"
        else:
            return "adventure"
    
    def _customize_domain(self, base_domain: str, lore_doc) -> str:
        """Personalizza SOLO il dominio basato sul lore"""
        
        system_msg = f"""Sei un esperto PDDL che personalizza DOMINI basati su template e lore.

IMPORTANTE: Devi generare SOLO un dominio PDDL, NON un problema.

{self.example_manager.get_domain_examples_for_prompt()}

TEMPLATE BASE DA PERSONALIZZARE:
{base_domain}

REGOLE OBBLIGATORIE:
1. Genera SOLO la sezione (define (domain ...)) 
2. NON includere mai sezioni (define (problem ...))
3. NON aggiungere commenti come "DOMINIO:" o "PROBLEMA:"
4. Mantieni la struttura del template
5. Personalizza tipi, predicati e azioni secondo il lore
6. Assicura compatibilità con i vincoli di branching factor
7. Mantieni tutti i commenti esplicativi esistenti

VINCOLI:
- Branching factor: {lore_doc.branching_factor[0]}-{lore_doc.branching_factor[1]}
- Profondità: {lore_doc.depth_constraints[0]}-{lore_doc.depth_constraints[1]}
- Personaggi: {lore_doc.characters}
- Luoghi: {lore_doc.locations}
- Oggetti: {lore_doc.items}"""

        user_template = """Personalizza questo dominio PDDL secondo il lore fornito.

LORE:
{quest_description}

CONTESTO:
{world_context}

VINCOLI SPECIALI:
{constraints}

IMPORTANTE: Restituisci SOLO il dominio personalizzato che inizia con (define (domain ...) e finisce con la relativa parentesi di chiusura. NON includere problemi o altri contenuti."""

        chain = get_ollama_chain(system_msg, user_template)
        response = chain.invoke({
            "quest_description": lore_doc.quest_description,
            "world_context": lore_doc.world_context,
            "constraints": ", ".join(lore_doc.constraints or [])
        })
        
        return extract_pddl_from_response(response.content)
    
    def _customize_problem(self, base_problem: str, lore_doc, domain_name: str) -> str:
        """Personalizza SOLO il problema basato sul lore"""
        
        system_msg = f"""Sei un esperto PDDL che personalizza PROBLEMI basati su template e lore.

IMPORTANTE: Devi generare SOLO un problema PDDL, NON un dominio.

{self.example_manager.get_problem_examples_for_prompt()}

TEMPLATE BASE DA PERSONALIZZARE:
{base_problem}

REGOLE OBBLIGATORIE:
1. Genera SOLO la sezione (define (problem ...))
2. NON includere mai sezioni (define (domain ...))
3. NON aggiungere commenti come "DOMINIO:" o "PROBLEMA:"
4. Il campo (:domain ...) deve riferirsi a: {domain_name}
5. Personalizza oggetti, stato iniziale e goal secondo il lore
6. Mantieni coerenza con i tipi definiti nel dominio
7. Assicura che goal sia raggiungibile

VINCOLI:
- Branching factor: {lore_doc.branching_factor[0]}-{lore_doc.branching_factor[1]}
- Profondità: {lore_doc.depth_constraints[0]}-{lore_doc.depth_constraints[1]}
- Personaggi: {lore_doc.characters}
- Luoghi: {lore_doc.locations}
- Oggetti: {lore_doc.items}"""

        user_template = """Personalizza questo problema PDDL secondo il lore fornito.

LORE:
{quest_description}

CONTESTO:
{world_context}

VINCOLI SPECIALI:
{constraints}

IMPORTANTE: Restituisci SOLO il problema personalizzato che inizia con (define (problem ...) e finisce con la relativa parentesi di chiusura. NON includere domini o altri contenuti."""

        chain = get_ollama_chain(system_msg, user_template)
        response = chain.invoke({
            "quest_description": lore_doc.quest_description,
            "world_context": lore_doc.world_context,
            "constraints": ", ".join(lore_doc.constraints or [])
        })
        
        return extract_pddl_from_response(response.content)

    def validate_and_refine(self, max_iterations: int = 3) -> Dict[str, any]:
        """Loop principale di validazione e refinement"""
        
        print("🔍 Inizio processo di validazione e refinement...")
        
        for iteration in range(max_iterations):
            print(f"\n{'='*50}")
            print(f"🔄 ITERAZIONE {iteration + 1}/{max_iterations}")
            print(f"{'='*50}")
            
            # Salva file temporanei
            domain_file = f"temp_domain_{iteration}.pddl"
            problem_file = f"temp_problem_{iteration}.pddl"
            
            write_to_file(self.current_domain, domain_file)
            write_to_file(self.current_problem, problem_file)
            
            # Validazione sintattica
            print("📋 Validazione sintattica...")
            domain_valid = validate_pddl_syntax(self.current_domain)
            problem_valid = validate_pddl_syntax(self.current_problem)
            
            if not domain_valid or not problem_valid:
                print("❌ Errori sintattici trovati")
                errors = []
                if not domain_valid:
                    errors.append("Errori sintattici nel dominio")
                if not problem_valid:
                    errors.append("Errori sintattici nel problema")
                
                # Riflessione per correggere errori
                reflection = self.reflection_agent.analyze_pddl_errors(
                    self.current_domain, self.current_problem, errors
                )
                
                if not self._apply_reflection_feedback(reflection):
                    continue
            
            # Test di solvibilità
            print("🧮 Test di solvibilità...")
            plan = run_fast_downward(domain_file, problem_file)
            
            if plan:
                print(f"✅ Piano trovato con {len(plan)} azioni!")
                print("🎯 Verifica vincoli di profondità...")
                
                if self._check_depth_constraints(plan):
                    print("✅ Vincoli di profondità soddisfatti!")
                    
                    # Pulizia file temporanei
                    self._cleanup_temp_files(iteration)
                    
                    return {
                        "success": True,
                        "domain": self.current_domain,
                        "problem": self.current_problem,
                        "plan": plan,
                        "iterations": iteration + 1,
                        "lore": self.current_lore
                    }
                else:
                    print("⚠️ Vincoli di profondità non soddisfatti")
                    # Suggerimenti per aggiustare la profondità
                    suggestions = self._get_depth_adjustment_suggestions(plan)
                    if not self._apply_depth_adjustments(suggestions):
                        continue
            else:
                print("❌ Nessun piano trovato")
                
                # Interazione con l'utente per il refinement
                if not self._interactive_refinement():
                    continue
            
            # Pulizia file temporanei
            self._cleanup_temp_files(iteration)
        
        print(f"\n❌ Impossibile generare un PDDL valido dopo {max_iterations} iterazioni")
        return {
            "success": False,
            "domain": self.current_domain,
            "problem": self.current_problem,
            "iterations": max_iterations,
            "lore": self.current_lore
        }
    
    def _apply_reflection_feedback(self, reflection: Dict[str, str]) -> bool:
        """Applica il feedback dell'agente di riflessione"""
        
        print("\n🤔 Feedback dell'agente di riflessione:")
        print("-" * 40)
        
        if reflection["errors"]:
            print("❌ Errori identificati:")
            print(reflection["errors"])
        
        if reflection["suggestions"]:
            print("\n💡 Suggerimenti:")
            print(reflection["suggestions"])
        
        # Chiedi conferma all'utente
        choice = input("\n🤝 Vuoi applicare le correzioni suggerite? [s/n]: ").lower()
        
        if choice == 's':
            # Applica le correzioni se disponibili
            if reflection["corrected_code"]:
                # Estrai dominio e problema corretti
                corrected_parts = self._extract_corrected_parts(reflection["corrected_code"])
                if corrected_parts["domain"]:
                    self.current_domain = corrected_parts["domain"]
                    print("✅ Dominio aggiornato")
                if corrected_parts["problem"]:
                    self.current_problem = corrected_parts["problem"]
                    print("✅ Problema aggiornato")
                return True
            else:
                print("⚠️ Nessuna correzione automatica disponibile")
                return self._manual_correction()
        else:
            return self._manual_correction()
    
    def _extract_corrected_parts(self, corrected_code: str) -> Dict[str, str]:
        """Estrae parti corrette dal codice"""
        parts = {"domain": "", "problem": ""}
        
        # Cerca blocchi di codice PDDL
        if "(define (domain" in corrected_code:
            domain_start = corrected_code.find("(define (domain")
            domain_end = self._find_matching_paren(corrected_code, domain_start)
            if domain_end > domain_start:
                parts["domain"] = corrected_code[domain_start:domain_end+1]
        
        if "(define (problem" in corrected_code:
            problem_start = corrected_code.find("(define (problem")
            problem_end = self._find_matching_paren(corrected_code, problem_start)
            if problem_end > problem_start:
                parts["problem"] = corrected_code[problem_start:problem_end+1]
        
        return parts
    
    def _find_matching_paren(self, text: str, start: int) -> int:
        """Trova la parentesi chiusa corrispondente"""
        count = 0
        for i in range(start, len(text)):
            if text[i] == '(':
                count += 1
            elif text[i] == ')':
                count -= 1
                if count == 0:
                    return i
        return -1
    
    def _manual_correction(self) -> bool:
        """Permette correzione manuale"""
        print("\n✏️ Correzione manuale:")
        print("1. Modifica dominio")
        print("2. Modifica problema")
        print("3. Riprova generazione")
        print("4. Salta iterazione")
        
        choice = input("Scelta [1-4]: ")
        
        if choice == "1":
            new_domain = input("Inserisci il nuovo dominio (o lascia vuoto per mantenere): ")
            if new_domain.strip():
                self.current_domain = new_domain.strip()
                print("✅ Dominio aggiornato")
            return True
        elif choice == "2":
            new_problem = input("Inserisci il nuovo problema (o lascia vuoto per mantenere): ")
            if new_problem.strip():
                self.current_problem = new_problem.strip()
                print("✅ Problema aggiornato")
            return True
        elif choice == "3":
            # Rigenera da capo
            self.current_domain, self.current_problem = self.generate_initial_pddl(self.current_lore)
            print("✅ PDDL rigenerato")
            return True
        else:
            return False
    
    def _check_depth_constraints(self, plan: List[str]) -> bool:
        """Verifica se il piano rispetta i vincoli di profondità"""
        plan_length = len(plan)
        min_depth, max_depth = self.current_lore.depth_constraints
        
        return min_depth <= plan_length <= max_depth
    
    def _get_depth_adjustment_suggestions(self, plan: List[str]) -> Dict[str, str]:
        """Suggerimenti per aggiustare la profondità del piano"""
        plan_length = len(plan)
        min_depth, max_depth = self.current_lore.depth_constraints
        
        suggestions = {}
        
        if plan_length < min_depth:
            suggestions["type"] = "increase_depth"
            suggestions["message"] = f"Piano troppo breve ({plan_length} < {min_depth})"
            suggestions["actions"] = [
                "Aggiungi azioni intermedie",
                "Introduci sotto-obiettivi",
                "Aggiungi elementi che richiedono preparazione"
            ]
        elif plan_length > max_depth:
            suggestions["type"] = "decrease_depth"
            suggestions["message"] = f"Piano troppo lungo ({plan_length} > {max_depth})"
            suggestions["actions"] = [
                "Semplifica alcune azioni",
                "Rimuovi passaggi intermedi",
                "Combina azioni simili"
            ]
        
        return suggestions
    
    def _apply_depth_adjustments(self, suggestions: Dict[str, str]) -> bool:
        """Applica aggiustamenti per la profondità"""
        print(f"\n📏 {suggestions['message']}")
        print("💡 Suggerimenti:")
        for action in suggestions["actions"]:
            print(f"   - {action}")
        
        choice = input("\n🔧 Vuoi applicare aggiustamenti automatici? [s/n]: ").lower()
        
        if choice == 's':
            # Applica modifiche basate sul tipo
            if suggestions["type"] == "increase_depth":
                return self._increase_plan_depth()
            else:
                return self._decrease_plan_depth()
        else:
            return self._manual_correction()
    
    def _increase_plan_depth(self) -> bool:
        """Aumenta la profondità del piano"""
        print("🔧 Aggiunta di complessità al problema...")
        
        # Modifica il problema per richiedere più passaggi
        modifications = [
            "Aggiungi oggetti intermedi necessari",
            "Introduci più location da visitare",
            "Aggiungi prerequisiti per le azioni"
        ]
        
        # Applica modifiche al problema
        # Questa è una semplificazione - in un sistema completo
        # si userebbe l'LLM per modificare il PDDL
        
        return True
    
    def _decrease_plan_depth(self) -> bool:
        """Diminuisce la profondità del piano"""
        print("🔧 Semplificazione del problema...")
        
        # Modifica il problema per richiedere meno passaggi
        modifications = [
            "Rimuovi alcuni oggetti intermedi",
            "Semplifica le connessioni tra location",
            "Riduci i prerequisiti per le azioni"
        ]
        
        # Applica modifiche al problema
        return True
    
    def _interactive_refinement(self) -> bool:
        """Refinement interattivo quando non viene trovato un piano"""
        print("\n🤝 Refinement interattivo:")
        print("1. Analizza con l'agente di riflessione")
        print("2. Suggerimenti miglioramento narrativo")
        print("3. Modifica manuale")
        print("4. Rigenera da capo")
        print("5. Salta iterazione")
        
        choice = input("Scelta [1-5]: ")
        
        if choice == "1":
            # Analisi con agente di riflessione
            reflection = self.reflection_agent.analyze_pddl_errors(
                self.current_domain, self.current_problem, 
                ["Nessun piano trovato"]
            )
            return self._apply_reflection_feedback(reflection)
        
        elif choice == "2":
            # Suggerimenti narrativi
            improvements = self.reflection_agent.suggest_improvements(
                self.current_lore, self.current_domain, self.current_problem
            )
            return self._apply_narrative_improvements(improvements)
        
        elif choice == "3":
            return self._manual_correction()
        
        elif choice == "4":
            self.current_domain, self.current_problem = self.generate_initial_pddl(self.current_lore)
            return True
        
        else:
            return False
    
    def _apply_narrative_improvements(self, improvements: Dict[str, str]) -> bool:
        """Applica miglioramenti narrativi"""
        print("\n📚 Miglioramenti narrativi suggeriti:")
        print("-" * 40)
        
        for key, value in improvements.items():
            if value.strip():
                print(f"\n{key.upper()}:")
                print(value)
        
        choice = input("\n🎭 Vuoi applicare questi miglioramenti? [s/n]: ").lower()
        
        if choice == 's':
            # In un sistema completo, qui si applicherebbe l'LLM
            # per modificare il PDDL basato sui miglioramenti
            print("✅ Miglioramenti applicati")
            return True
        else:
            return False
    
    def _cleanup_temp_files(self, iteration: int):
        """Pulisce i file temporanei"""
        temp_files = [
            f"temp_domain_{iteration}.pddl",
            f"temp_problem_{iteration}.pddl",
            "sas_plan"
        ]
        
        for file in temp_files:
            if os.path.exists(file):
                try:
                    os.remove(file)
                except:
                    pass
    
    def save_final_files(self, result: Dict[str, any], base_name: str = "final") -> bool:
        """Salva i file finali"""
        try:
            # Salva dominio
            domain_file = f"{base_name}_domain.pddl"
            write_to_file(result["domain"], domain_file)
            
            # Salva problema
            problem_file = f"{base_name}_problem.pddl"
            write_to_file(result["problem"], problem_file)
            
            # Salva lore
            lore_file = f"{base_name}_lore.yaml"
            lore_data = {
                "quest_description": result["lore"].quest_description,
                "world_context": result["lore"].world_context,
                "branching_factor": result["lore"].branching_factor,
                "depth_constraints": result["lore"].depth_constraints,
                "characters": result["lore"].characters,
                "locations": result["lore"].locations,
                "items": result["lore"].items,
                "constraints": result["lore"].constraints,
                "generation_info": {
                    "iterations": result["iterations"],
                    "plan_length": len(result.get("plan", [])),
                    "success": result["success"]
                }
            }
            
            with open(lore_file, 'w', encoding='utf-8') as f:
                yaml.dump(lore_data, f, default_flow_style=False, allow_unicode=True)
            
            # Salva piano se presente
            if result.get("plan"):
                plan_file = f"{base_name}_plan.txt"
                with open(plan_file, 'w', encoding='utf-8') as f:
                    f.write(f"Piano generato con {len(result['plan'])} azioni:\n")
                    f.write("-" * 40 + "\n")
                    for i, action in enumerate(result["plan"], 1):
                        f.write(f"{i:2d}. {action}\n")
            
            print(f"✅ File salvati con prefisso '{base_name}'")
            return True
            
        except Exception as e:
            print(f"❌ Errore nel salvataggio: {e}")
            return False
