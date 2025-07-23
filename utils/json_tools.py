import re

def clean_json_output(text):
    # Rimuovi blocchi markdown (```json, ```pddl, ecc.)
    text = re.sub(r"```[a-zA-Z]*", "", text)
    text = text.replace("```", "")
    text = text.strip()

    # Cerca solo la parte JSON
    json_start = text.find("{")
    json_end = text.rfind("}")
    if json_start != -1 and json_end != -1:
        return text[json_start:json_end+1]
    return ""
