from langchain.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

def generate_quest(goal, obstacle, lore_hints=None):

    system_template = "Sei un abile narratore di storie fantasy. Genera una breve descrizione di una missione basata su un obiettivo e un ostacolo."
    user_template = "Obiettivo: {goal}\nOstacolo: {obstacle}\nLore aggiuntiva: {lore_hints}\nDescrizione della missione:"

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_template),
        ("human", user_template),
    ])

    goal = input("Inserisci l'obiettivo della missione (es. 'recupera la spada antica'): ")
    obstacle = input("Inserisci l'ostacolo (es. 'esiste un drago che la protegge'): ")

    model = ChatOllama(model="mistral")
    chain = prompt | model

    response = chain.invoke({"goal": goal, "obstacle": obstacle, "lore": lore_hints})
    print(response.content)













