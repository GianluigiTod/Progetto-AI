from langchain.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from pathlib import Path
import subprocess

MODEL_NAME = "mistral"

def get_ollama_chain(system_message: str, user_template: str):
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("human", user_template)
    ])
    return prompt | ChatOllama(model=MODEL_NAME, temperature=0.2, top_p=0.9)

def write_to_file(content: str, filename: str):
    Path(filename).write_text(content.strip(), encoding='utf-8')
    print(f"📂 File salvato: {filename}")

def validate_domain_pddl(pddl_code: str):
    system_msg = """
Sei un esperto di PDDL. Ti verrà fornito un file domain PDDL da correggere.
Correggi solo errori di sintassi, tipi, dichiarazioni o predicati incoerenti.
Segui questi principi:
- Non usare | nei tipi: usa tipi astratti (es. Entity)
- Nessun (and ...) in :init o :objects
- Aggiungi solo dichiarazioni mancanti se necessarie
- Mantieni coerenza tra precondizioni ed effetti
- Restituisci SOLO codice PDDL valido
- Il file deve essere accettato da un validatore VAL, quindi è IMPORTANTE che non ci siano errori sintattici

Esempio di errore:
❌ (:parameters (?e - Knight | Demon))
✅ (:types Entity - object Knight Demon - Entity)
    (:parameters (?e - Entity))
"""

    user_template = """
Questo è un file domain PDDL potenzialmente con errori:

{pddl_code}

Correggi solo se necessario. Mantieni i nomi dove possibile.
"""

    chain = get_ollama_chain(system_msg, user_template)
    response = chain.invoke({"pddl_code": pddl_code})
    return response.content.strip()

def validate_problem_pddl(pddl_code: str):
    system_msg = """
Sei un esperto di PDDL. Ti verrà fornito un file problem PDDL da correggere.
Correggi solo errori di sintassi, tipi, dichiarazioni o predicati incoerenti.
Segui questi principi:
- Nessun (and ...) in :init o :objects
- Oggetti e predicati coerenti con il dominio
- Obiettivo deve essere raggiungibile
- Restituisci SOLO codice PDDL valido (no commenti o testo extra)
"""

    user_template = """
Questo è un file problem PDDL potenzialmente con errori:

{pddl_code}

Correggi solo se necessario. Mantieni i nomi dove possibile.
"""

    chain = get_ollama_chain(system_msg, user_template)
    response = chain.invoke({"pddl_code": pddl_code})
    return response.content.strip()

def generate_domain_pddl(lore: str, min_branch: int, max_branch: int, min_depth: int, max_depth: int):
    system_msg = (
        "Sei un assistente esperto di PDDL. Genera un file domain PDDL valido (versione 1.2 o 2.1), "
        "con requisiti :strips e :typing. Rispondi solo con codice PDDL."
    )

    domain_examples = """
ESEMPIO 1:
(define (domain rescue_mission)
  (:requirements :strips :typing)
  (:types student location)
  (:predicates
    (at ?s - student ?l - location)
    (safe ?l - location)
    (rescued ?s - student)
  )
  (:action move
    :parameters (?s - student ?from - location ?to - location)
    :precondition (and (at ?s ?from))
    :effect (and (not (at ?s ?from)) (at ?s ?to))
  )
  (:action rescue
    :parameters (?s - student ?l - location)
    :precondition (and (at ?s ?l) (safe ?l))
    :effect (rescued ?s)
  )
)

ESEMPIO 2:
(define (domain robot_warehouse)
  (:requirements :strips :typing)
  (:types robot package location)
  (:predicates
    (robot_at ?r - robot ?l - location)
    (package_at ?p - package ?l - location)
    (carrying ?r - robot ?p - package)
  )
  (:action pickup
    :parameters (?r - robot ?p - package ?l - location)
    :precondition (and (robot_at ?r ?l) (package_at ?p ?l))
    :effect (and (carrying ?r ?p) (not (package_at ?p ?l)))
  )
  (:action drop
    :parameters (?r - robot ?p - package ?l - location)
    :precondition (and (carrying ?r ?p) (robot_at ?r ?l))
    :effect (and (package_at ?p ?l) (not (carrying ?r ?p)))
  )
)
"""

    user_template = (
        f"{domain_examples}\n\n"
        "Ora genera un nuovo dominio PDDL coerente con questa lore:\n"
        "{lore}\n\n"
        "Branching factor: minimo {min_branch}, massimo {max_branch}\n"
        "Profondità: minimo {min_depth}, massimo {max_depth}\n\n"
        "Requisiti:\n"
        "- Usa tipi coerenti\n"
        "- Solo predicati e azioni rilevanti per la lore\n"
        "- Nessun testo aggiuntivo, solo codice PDDL valido\n"
        "- Nomi in snake_case, consistenti con la lore"
    )
    chain = get_ollama_chain(system_msg, user_template)
    response = chain.invoke({
        "lore": lore,
        "min_branch": min_branch,
        "max_branch": max_branch,
        "min_depth": min_depth,
        "max_depth": max_depth
    })
    return response.content.strip()

def generate_problem_pddl(lore: str, domain_content: str):
    system_msg = (
        "Sei un assistente specializzato in problemi PDDL. Genera un problem PDDL valido e coerente "
        "per il dominio fornito. Rispondi solo con codice PDDL."
    )

    problem_examples = """
ESEMPIO 1:
(define (problem rescue_scenario)
  (:domain rescue_mission)
  (:objects alice bob - student
            forest base - location)
  (:init
    (at alice forest)
    (at bob forest)
    (safe forest)
  )
  (:goal (and (rescued alice) (rescued bob)))
)

ESEMPIO 2:
(define (problem warehouse_problem)
  (:domain robot_warehouse)
  (:objects r1 - robot
            p1 p2 - package
            zone_a zone_b - location)
  (:init
    (robot_at r1 zone_a)
    (package_at p1 zone_a)
    (package_at p2 zone_b)
  )
  (:goal (and (package_at p1 zone_b) (package_at p2 zone_a)))
)
"""

    user_template = (
        f"{problem_examples}\n\n"
        "Lore: {lore}\n\n"
        "Dominio:\n{domain_content}\n\n"
        "Crea un problema PDDL con:\n"
        "- Oggetti ben tipizzati\n"
        "- Stato iniziale coerente con i predicati\n"
        "- Obiettivo semplice ma raggiungibile\n"
        "- Solo nomi in snake_case\n"
        "- Solo codice PDDL"
    )
    chain = get_ollama_chain(system_msg, user_template)
    response = chain.invoke({
        "lore": lore,
        "domain_content": domain_content
    })
    return response.content.strip()

def generate_complete_pddl(lore: str, min_branch: int, max_branch: int, min_depth: int, max_depth: int):
    print("🚀 Generazione dominio...")
    raw_domain = generate_domain_pddl(lore, min_branch, max_branch, min_depth, max_depth)
    print("🔍 Validazione dominio...")
    fixed_domain = validate_domain_pddl(raw_domain)
    write_to_file(fixed_domain, "domain.pddl")

    print("✔ Dominio pronto!\n\n🚀 Generazione problema...")
    raw_problem = generate_problem_pddl(lore, fixed_domain)
    print("🔍 Validazione problema...")
    fixed_problem = validate_problem_pddl(raw_problem)
    write_to_file(fixed_problem, "problem.pddl")

    print("✅ PDDL completato e validato.")
    return {"domain": fixed_domain, "problem": fixed_problem}

def plan_with_fast_downward(domain, problem, strategy="astar(lmcut())"):
    subprocess.run([
        "python",
        "C:\\Users\\Alessandro\\fast_downward\\downward\\fast-downward.py",
        domain,
        problem,
        "--search", strategy,
        "--plan-file", "sas_plan"
    ], check=True)

    with open("sas_plan", "r", encoding="utf-8") as f:
        return [line.strip() for line in f]

if __name__ == "__main__":
    lore_text = input("📖 Inserisci la descrizione dell'avventura: ")
    min_b = int(input("🔢 Branching factor minimo: "))
    max_b = int(input("🔢 Branching factor massimo: "))
    min_d = int(input("🌱 Profondità minima: "))
    max_d = int(input("🌲 Profondità massima: "))

    # Genera dominio e problema PDDL
    pddl_files = generate_complete_pddl(lore_text, min_b, max_b, min_d, max_d)

    # Esegui planner Fast Downward e stampa il piano
    print("🚀 Pianificazione in corso...")
    plan = plan_with_fast_downward("domain.pddl", "problem.pddl")
    print("\n📋 Piano trovato:")
    for step in plan:
        print(step)
