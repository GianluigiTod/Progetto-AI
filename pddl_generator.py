from langchain.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

def generate_plan_steps(goal, obstacle, lore, depth=3):
    # LLM genera elenco coerente di passi da seguire
    prompt_text = f"""Genera una sequenza di azioni logiche (non PDDL) che siano al massimo {depth} per raggiungere questo obiettivo: {goal}, superando questo ostacolo: {obstacle}.
    Usa questi indizi se rilevanti: {lore}
    Elenca in ordine numerato, una azione per riga."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Sei un esperto nella scrittura di titoli di azioni."),
        ("human", prompt_text)
    ])
    chain = prompt | ChatOllama(model='mistral')
    response = chain.invoke({"input":  f"Goal:{goal}, ostacolo: {obstacle}, lore_hints:{lore}, depth:{depth}"})
    text=response.content
    return [line.strip() for line in text.split("\n") if line.strip()]

def generate_pddl_actions(plan_steps: list[str]) -> str:
    # Traduci ogni step in PDDL
    pddl_actions = []
    for step in plan_steps:
        pddl_actions.append(convert_to_pddl(step, pddl_actions))
    return "\n".join(pddl_actions)


def convert_to_pddl(step: str, previous_actions: list[str]) -> str:
    examples = [
        {
            "input": "Supera il drago con un incantesimo",
            "output": """(:action cast-spell
                :parameters (?h - hero ?d - dragon)
                :precondition (has-spell ?h fireball)
                :effect (defeated ?d))"""
        },
        {
            "input": "Il cavaliere apre la porta con una chiave d'oro",
            "output": """(:action apri-porta
                :parameters (?c - cavaliere ?p - porta ?k - chiave)
                :precondition (and (ha ?c ?k) (bloccata ?p))
                :effect (and (not (bloccata ?p)) (aperta ?p)))"""
        },
        {
            "input": "L'eroe scala una scala per raggiungere una torre",
            "output": """(:action scala
                :parameters (?e - eroe ?s - scala ?t - torre)
                :precondition (and (alla-base ?e ?s) (collegata ?s ?t))
                :effect (and (in-cima ?e ?t) (not (alla-base ?e ?s))))"""
        }
    ]

    # Costruisci la stringa con le azioni PDDL già generate
    context_actions = "\n\n".join(previous_actions) if previous_actions else "(nessuna azione precedente)"
    
    # Costruisci gli esempi come stringa
    examples_as_string = "\n\n".join(
        f"Input: {ex['input']}\nOutput:\n{ex['output']}" for ex in examples
    )

    # Correggi il prompt template per usare le variabili corrette
    prompt_text = """Sei un assistente che converte descrizioni di azioni in azioni PDDL. Ecco le azioni già generate finora:
{context_actions}

Di seguito alcuni esempi di input/output per farti capire lo stile richiesto:
{examples}

Ora converti la seguente azione descritta in linguaggio naturale in una nuova azione PDDL coerente con quelle sopra. Definisci :action, :parameters, :precondition e :effect.
Azione da convertire: {step}"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Sei un esperto nella scrittura di azioni PDDL coerenti."),
        ("human", prompt_text)
    ])

    chain = prompt | ChatOllama(model="mistral")

    # Correggi l'invocazione per usare le variabili del template
    response = chain.invoke({
        "context_actions": context_actions, 
        "step": step, 
        "examples": examples_as_string
    })
    return response.content.strip()



'''
def generate_pddl_actions(goal, obstacle, depth=3):
    examples = [
        {
            "input": "Supera il drago con un incantesimo",
            "output": """(:action cast-spell
                :parameters (?h - hero ?d - dragon)
                :precondition (has-spell ?h fireball)
                :effect (defeated ?d))"""
        },
        {
            "input": "Il cavaliere apre la porta con una chiave d'oro",
            "output": """(:action apri-porta
                :parameters (?c - cavaliere ?p - porta ?k - chiave)
                :precondition (and (ha ?c ?k) (bloccata ?p))
                :effect (and (not (bloccata ?p)) (aperta ?p)))"""
        },
        {
            "input": "L'eroe scala una scala per raggiungere una torre",
            "output": """(:action scala
                :parameters (?e - eroe ?s - scala ?t - torre)
                :precondition (and (alla-base ?e ?s) (collegata ?s ?t))
                :effect (and (in-cima ?e ?t) (not (alla-base ?e ?s))))"""
        }
    ]

    prompt = ChatPromptTemplate.from_messages([
        ("system", f"Genera al massimo {depth} azioni PDDL per raggiungere: {goal}. Ostacolo: {obstacle}"),
        *[("human", ex["input"]) for ex in examples],
        *[("ai", ex["output"]) for ex in examples],
        ("human", "Genera azioni per: {input}")
    ])

    chain = prompt | ChatOllama(model="mistral")
    response = chain.invoke({"input": f"Goal: {goal}, ostacolo: {obstacle}"})
    return response.content
'''

def save_to_pddl_file(actions, filename):
    with open(filename, "w") as f:
        f.write(f"(define (domain quest)\n{actions}\n)")