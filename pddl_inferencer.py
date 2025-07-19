from typing import List
from lore import LoreDocument
from online_llm_client import OnlineLLMClient
from langchain.prompts import ChatPromptTemplate
import re

class PDDLInferencer:
    def __init__(self, lore: LoreDocument, llm: OnlineLLMClient):
        self.lore = lore
        self.llm = llm
        self.replacement_map = self._build_replacement_map()

    def _build_replacement_map(self) -> dict:
        def normalize_name(name: str) -> str:
            # Rimuove spazi e caratteri non validi nei nomi di variabili
            return name.strip().lower().replace(" ", "_").replace("-", "_")

        mapping = {}

        for c in self.lore.characters or []:
            var = normalize_name(c)
            mapping[c] = f"?char_{var} - character"

        for l in self.lore.locations or []:
            var = normalize_name(l)
            mapping[l] = f"?loc_{var} - location"

        for i in self.lore.items or []:
            var = normalize_name(i)
            mapping[i] = f"?item_{var} - item"

        return mapping

    def _normalize_text(self, text: str) -> str:
        for concrete, variable in self.replacement_map.items():
            pattern = re.compile(rf'\b{re.escape(concrete)}\b', re.IGNORECASE)
            text = pattern.sub(variable, text)
        return text

    def infer_predicates(self) -> List[str]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
⚠️ ATTENZIONE: Genera SOLO predicati validi in sintassi PDDL STRIPS.
Non usare testo narrativo. Ogni riga è un predicato.

✅ Formato accettato:
(nome_predicato ?x - tipo ?y - tipo)
❌ NON usare ":predicate", "function", testo libero.

Esempi validi:
(at ?c - character ?l - location)
(has ?c - character ?i - item)
(alive ?c - character)
(connected ?from - location ?to - location)

✅ Restituisci SOLO predicati, uno per riga, senza descrizione.
"""),

            ("human", "Lore: {lore}\n\nPredicati:")
        ])
        formatted_prompt = prompt.format_messages(lore=self._format_lore())
        prompt_text = "\n".join(m.content for m in formatted_prompt)
        result = self.llm.run_prompt(prompt_text)
        raw_preds = self._parse_list(result)
        normalized_preds = [self._normalize_text(p) for p in raw_preds]
        sanitized_preds = [self._sanitize_predicate(p) for p in normalized_preds]
        return sanitized_preds

    def _sanitize_predicate(self, predicate: str) -> str:

        # Rimuove predicati con nomi malformati come knows-?x
        predicate = re.sub(r'([^\s(]+)-\?[\w_]+', r'\1', predicate)

        # Rimuove variabili usate come tipo (!)
        predicate = re.sub(r'-\s*\?[a-zA-Z0-9_]+', '- object', predicate)

        return predicate


    def infer_actions(self) -> List[str]:
    

        prompt = ChatPromptTemplate.from_messages([
            ("system", """
    ATTENZIONE: genera SOLO azioni PDDL valide in STRIPS.
    Ogni azione deve seguire esattamente questo template:

    (:action <nome>
    :parameters (?p1 - tipo1 ?p2 - tipo2 ...)
    :precondition (and ...)
    :effect (and ...)
    )

    Tutte le variabili usate in precondition/effect devono essere dichiarate in :parameters!
    """),
            ("human", f"Lore: {self._format_lore()}\n\nAzioni:")
        ])

        formatted_prompt = prompt.format_messages()
        prompt_text = "\n".join(m.content for m in formatted_prompt)
        result = self.llm.run_prompt(prompt_text)
        actions = self._split_actions(result)
        normalized = [self._normalize_text(a) for a in actions]
        cleaned = [self._fix_malformed_pddl_action_block(a) for a in normalized]
        return list(dict.fromkeys(cleaned))

    def _fix_malformed_pddl_action_block(self, action_text: str) -> str:

        def fix_params_block(match):
            raw = match.group(1)
            tokens = raw.strip().split()
            fixed = []
            seen = set()
            for i in range(0, len(tokens) - 1, 2):
                var, typ = tokens[i], tokens[i + 1]
                if var.startswith("?") and "-" not in var and (var, typ) not in seen:
                    fixed.append(f"{var} {typ}")
                    seen.add((var, typ))
            return f":parameters ({' '.join(fixed)})"

        action_text = re.sub(r":parameters\s*\(([^)]*)\)", fix_params_block, action_text)
        action_text = re.sub(r"([a-zA-Z0-9_()-]+)-\s*\?", r"\1 ?", action_text)
        action_text = action_text.replace("\\?", "?").replace("\\", "")
        action_text = re.sub(r"\(:action\s+([^\s()]+)", lambda m: f"(:action {re.sub(r'[^a-zA-Z0-9_]', '_', m.group(1))}", action_text)
        return action_text



    def infer_goal(self) -> str:
   
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
    ATTENZIONE: genera SOLO il goal PDDL valido.
    ❌ NON usare variabili con '- tipo' nel goal.
    ✅ Usa predicati concreti, uno per riga, nel blocco (and ...)

    Esempio corretto:
    (and (not (alive bandit_leader)) (at hero village))
    """),
            ("human", f"Lore: {self._format_lore()}\n\nGoal:")
        ])

        formatted_prompt = prompt.format_messages()
        prompt_text = "\n".join(m.content for m in formatted_prompt)
        result = self.llm.run_prompt(prompt_text)
        raw = result.strip()

        # Pulizia finale
        return self._sanitize_goal(raw)
    def _sanitize_goal(self, goal: str) -> str:
   
        goal = re.sub(r'\(and\s+\.\.\.\)', '', goal)
        goal = re.sub(r'(\?[a-zA-Z0-9_]+)\s*-\s*\w+', r'\1', goal)
        goal = re.sub(r'\(\s*\)', '', goal)
        tokens = re.findall(r'\([^\)]+\)', goal)
        unique = list(dict.fromkeys(tokens))
        if not unique:
            return "(and (true))"
        elif len(unique) == 1:
            return unique[0]
        else:
            return f"(and {' '.join(unique)})"


    def _format_lore(self) -> str:
        return f"""
Descrizione: {self.lore.quest_description}
Contesto: {self.lore.world_context}
Personaggi: {', '.join(self.lore.characters or [])}
Luoghi: {', '.join(self.lore.locations or [])}
Oggetti: {', '.join(self.lore.items or [])}
Vincoli: {', '.join(self.lore.constraints or [])}
        """

    def _parse_list(self, text: str) -> List[str]:
        lines = text.splitlines()
        valid = []
        for line in lines:
            line = line.strip()
            if (
                line.startswith('(')
                and '-' in line
                and not any(c in line for c in [":predicate", "function"])
            ):
                valid.append(line)
        return valid

    def _split_actions(self, text: str) -> List[str]:
        actions = []
        stack = 0
        current = []

        for line in text.splitlines():
            line = line.strip()
            if line.startswith("(:action"):
                if current:
                    actions.append(self._fix_action("\n".join(current)))
                    current = []
                stack = 0
            stack += line.count('(') - line.count(')')
            current.append(line)
            if stack == 0 and current:
                actions.append(self._fix_action("\n".join(current)))
                current = []
        if current:
            actions.append(self._fix_action("\n".join(current)))

        return [a.strip() for a in actions if a.strip().startswith("(:action")]

    def _fix_action(self, action_text: str) -> str:
        def wrap_clause(text, keyword):
            pattern = rf"(:{keyword})\\s*\\(([^()]+)\\)"
            return re.sub(pattern, rf":{keyword} (and (\2))", text)
        fixed = wrap_clause(action_text, "precondition")
        fixed = wrap_clause(fixed, "effect")
        return fixed

    def _sanitize_goal(self, goal: str) -> str:
        goal = goal.replace("present", "at")
        if goal.startswith("(and") and goal.endswith(")"):
            return goal
        matches = re.findall(r'\([^\(\)]+\)', goal)
        if not matches:
            return f"(and {goal})"
        return f"(and {' '.join(matches)})"
    
    def _ensure_parameters_match_variables(self, action_text: str) -> str:
        """
        Controlla che tutte le variabili usate in precondition/effect siano nei :parameters.
        Se manca qualcosa, la aggiunge con tipo generico - object (fallback sicuro).
        """
        import re

        # Estrai parametri esistenti
        param_block = re.search(r":parameters\s*\(([^)]*)\)", action_text)
        existing_vars = set()
        param_list = []

        if param_block:
            tokens = param_block.group(1).split()
            for i in range(0, len(tokens) - 1, 2):  # (?x - type)
                if tokens[i].startswith("?"):
                    existing_vars.add(tokens[i])
                    param_list.append((tokens[i], tokens[i + 1]))

        # Trova tutte le variabili usate nel testo
        used_vars = set(re.findall(r"\?[\w_]+", action_text))

        # Variabili mancanti
        missing = used_vars - existing_vars

        # Aggiungi variabili mancanti con tipo generico - object
        if missing:
            additions = [(v, "- object") for v in sorted(missing)]
            new_param_str = " ".join(f"{v} {t}" for v, t in param_list + additions)
            action_text = re.sub(r":parameters\s*\([^)]*\)", f":parameters ({new_param_str})", action_text)

        return action_text

