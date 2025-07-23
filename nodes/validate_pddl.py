from utils.fast_downward import validate_with_fast_downward

def validate_pddl(state):
    is_valid = validate_with_fast_downward(state["domain_pddl"], state["problem_pddl"])
    return {**state, "plan_valido": is_valid}
