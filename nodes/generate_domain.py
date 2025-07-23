from prompts.generate_domain_prompt import get_prompt
from utils.ask_openai import ask_openai

def generate_domain(state):
    system, user = get_prompt(state['lore_parsed'])
    result = ask_openai(system, user)
    return {**state, "domain_pddl": result}
