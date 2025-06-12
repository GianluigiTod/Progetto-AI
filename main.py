# main.py
# Punto d'ingresso: crea un grafo LangGraph che collega story e PDDL

from story_generator import generate_story
from pddl_generator import *
from langgraph.graph import StateGraph, START
from typing_extensions import TypedDict
from langchain.chains import LLMChain

# 1. Definiamo lo schema dello stato che passerà tra i nodi
type PDDL = str

class GameState(TypedDict):
    goal: str
    obstacle: str
    lore_hints: str
    story: str
    pddl: PDDL
    depth: int

# 2. Nodo: genera la storia da goal/ostacolo/lore
def story_node(state: GameState) -> dict:
    #story = generate_story(state["goal"], state["obstacle"], state.get("lore_hints", ""))
    story= generate_story(state["pddl"], state.get("lore_hints", ""))
    return {"story": story}

# 3. Nodo: genera le azioni PDDL e salva su file
def pddl_node(state: GameState) -> dict:
    steps = generate_plan_steps(state["goal"], state["obstacle"], state["lore_hints"], state["depth"])
    pddl = generate_pddl_actions(steps)
    save_to_pddl_file(pddl, "./pddl/domain.pddl")
    return {"pddl": pddl}

# 4. Costruiamo il grafo
graph_builder = (
    StateGraph(GameState)
    .add_node("generate_story", story_node)
    .add_node("generate_pddl", pddl_node)
    .add_edge(START, "generate_pddl")
    .add_edge("generate_pddl", "generate_story")
)


graph=graph_builder.compile()

# 5. Input da terminale e invocazione del grafo
if __name__ == "__main__":
    goal = input("Obiettivo della missione: ")
    obstacle = input("Ostacolo principale: ")
    lore = input("Lore aggiuntiva (opzionale): ")
    depth_input = input("Depth della storia (opzionale): ")
    depth = int(depth_input) if depth_input.strip().isdigit() else 3

    input_state: GameState = {
        "goal": goal,
        "obstacle": obstacle,
        "lore_hints": lore,
        "depth": depth,
        "story": "",
        "pddl": ""
    }

    result = graph.invoke(input_state)

    print("\n--- Azioni PDDL ---\n")
    print(result["pddl"])


    print("\n--- Storia generata ---\n")
    print(result["story"])

