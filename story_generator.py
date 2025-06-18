from langchain.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

def generate_story(steps, lore_hints=None):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Sei un narratore fantasy. Usa le azioni {steps} per creare una storia con un linguaggio naturale usando anche i lore hints: {lore_hints} mantenendo la sequenza della storia uguale a quella delle azioni."),
        ("human", """
        steps: {steps}
        lore_hints: {lore_hints}
        """)
    ])

    chain = prompt | ChatOllama(model="mistral", temperature=0.2)
    response = chain.invoke({
        "steps": steps,
        "lore_hints": lore_hints or "Nessun hint fornito."
    })
    return response.content

