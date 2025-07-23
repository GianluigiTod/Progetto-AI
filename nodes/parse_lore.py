from prompts.parse_lore_prompt import get_prompt
from utils.ask_openai import ask_openai
from utils.json_tools import clean_json_output 
import json
import re


def parse_lore(state):
    system, user = get_prompt(state['lore_raw'])
    result = ask_openai(system, user)

    result_cleaned = clean_json_output(result)

    if not result_cleaned:
        print("❌ JSON non trovato nella risposta.")
        print("🔍 Output ricevuto:\n", result)
        raise ValueError("La risposta non contiene JSON valido.")

    parsed = json.loads(result_cleaned)


    return {**state, "lore_parsed": parsed}
