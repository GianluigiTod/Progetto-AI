from prompts.generate_problem_prompt import get_prompt
from utils.ask_openai import ask_openai

def generate_problem(state):
    system, user = get_prompt(state['lore_parsed'])
    result = ask_openai(system, user)
    return {**state, "problem_pddl": result}
