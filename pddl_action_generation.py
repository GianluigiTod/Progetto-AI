from langchain.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

# Esempi few-shot per insegnare il formato PDDL all'LLM
examples = [
    {
        "input": "Il cavaliere apre la porta con una chiave d'oro",
        "output": """(:action apri-porta
           :parameters (?c - cavaliere ?p - porta ?k - chiave)
           :precondition (and (ha ?c ?k) (bloccata ?p))
           :effect (and (not (bloccata ?p)) (aperta ?p)))"""
    },
    {
        "input": "L’eroe scala una scala per raggiungere una torre",
        "output": """(:action scala
           :parameters (?e - eroe ?s - scala ?t - torre)
           :precondition (and (alla-base ?e ?s) (collegata ?s ?t))
           :effect (and (in-cima ?e ?t) (not (alla-base ?e ?s))))"""
    }
]

# Template con few-shot examples
prompt = ChatPromptTemplate.from_messages([
    ("system", "Converti la descrizione in un'azione PDDL usando questi esempi:"),
    *[("human", ex["input"]) for ex in examples],
    *[("ai", ex["output"]) for ex in examples],
    ("human", "{input}"),
])

# Collegamento al modello (usa lo stesso dell'Esercizio 1.1)
model = ChatOllama(model="mistral")
chain = prompt | model

# Test con un nuovo input
input_narrazione = input("Descrivi un'azione (es. 'Il mago lancia un incantesimo per illuminare la stanza'): ")
response = chain.invoke({"input": input_narrazione})
print("\nAzione PDDL generata:")
print(response.content)