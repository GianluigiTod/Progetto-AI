from langchain.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

def generate_story(pddl, lore_hints=None):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Sei un narratore fantasy. Usa le azioni in formato pddl {pddl} per creare una storia. Puoi abbellirla, usando "
        "i lore hints: {lore_hints} e anche altro, però devi mantenere le azioni in pddl come sequenza principale"),
        ("human", """
        pddl: {pddl}
        lore_hints: {lore_hints}
        """)
    ])

    chain = prompt | ChatOllama(model="mistral")
    response = chain.invoke({
        "pddl" : pddl,
        "lore_hints": lore_hints or "Nessun hint fornito."
    })
    return response.content

