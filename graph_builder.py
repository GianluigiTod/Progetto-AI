from langgraph.graph import StateGraph
from nodes import (
    parse_lore, generate_problem, generate_domain,
    validate_pddl, reflection_agent, finalize_output,generate_fallback_pddl
)

MAX_ITER = 3

def guard_validation(state):
    if state["plan_valido"]:
        return "finalize_output"
    elif state.get("iteration", 0) >= MAX_ITER:
        return "finalize_output" 

    #elif state.get("iteration", 0) >= MAX_ITER:
        #return "generate_fallback"
    else:
        return "reflection_agent"

def build_graph():
    builder = StateGraph(state_schema=dict)
    builder.add_node("parse_lore", parse_lore)
    builder.add_node("generate_problem", generate_problem)
    builder.add_node("generate_domain", generate_domain)
    builder.add_node("validate_pddl", validate_pddl)
    builder.add_node("reflection_agent", reflection_agent)
    #builder.add_node("generate_fallback", generate_fallback_pddl)
    builder.add_node("finalize_output", finalize_output)

    builder.set_entry_point("parse_lore")
    builder.add_edge("parse_lore", "generate_problem")
    builder.add_edge("generate_problem", "generate_domain")
    builder.add_edge("generate_domain", "validate_pddl")
    builder.add_conditional_edges("validate_pddl", guard_validation, {
        "finalize_output": "finalize_output",
        "reflection_agent": "reflection_agent",
        #"generate_fallback": "generate_fallback"
    })
    builder.add_edge("reflection_agent", "validate_pddl")
    #builder.add_edge("generate_fallback", "finalize_output")
    builder.set_finish_point("finalize_output")

    return builder.compile()
