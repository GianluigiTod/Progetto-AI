import re
from typing import List
from lore import LoreDocument
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate

class PDDLInferencer:
    def __init__(self, lore: LoreDocument):
        self.lore = lore
        self.llm = ChatOllama(model="mistral")
        self.replacement_map = self._build_replacement_map()

    def _build_replacement_map(self) -> dict:
        """
        Costruisce un dizionario mappa: nome_concreto -> variabile tipizzata PDDL
        Es: 'castello' -> '?loc_castello - location'
        """
        mapping = {}
        for c in self.lore.characters or []:
            var_name = c.strip().replace(" ", "_").lower()
            mapping[c] = f"?char_{var_name} - character"
        for l in self.lore.locations or []:
            var_name = l.strip().replace(" ", "_").lower()
            mapping[l] = f"?loc_{var_name} - location"
        for i in self.lore.items or []:
            var_name = i.strip().replace(" ", "_").lower()
            mapping[i] = f"?item_{var_name} - item"
        return mapping

    def _normalize_text(self, text: str) -> str:
        """
        Sostituisce i nomi concreti con variabili tipizzate nel testo PDDL.
        """
        for concrete, variable in self.replacement_map.items():
            # Usa \b per corrispondenza solo parole intere, case insensitive
            pattern = re.compile(rf'\b{re.escape(concrete)}\b', re.IGNORECASE)
            text = pattern.sub(variable, text)
        return text

    def infer_predicates(self) -> List[str]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
ATTENZIONE: restituisci SOLO predicati PDDL validi, uno per riga.
Non usare (:predicate ...) o linguaggio naturale.
Formato richiesto: (nome ?x - tipo ?y - tipo)
Esempi:
(at ?c - character ?l - location)
(alive ?c - character)
(connected ?from - location ?to - location)
"""),
            ("human", "Lore: {lore}\n\nPredicati:")
        ])
        result = (prompt | self.llm).invoke({"lore": self._format_lore()}).content
        raw_preds = self._parse_list(result)
        normalized_preds = [self._normalize_text(p) for p in raw_preds]
        return normalized_preds

    def infer_actions(self) -> List[str]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
ATTENZIONE: restituisci SOLO azioni PDDL in formato STRIPS.
Ogni azione deve iniziare con (:action nome), e includere :parameters, :precondition, :effect.
Formato richiesto:
(:action <nome>
 :parameters (?p1 - tipo1 ?p2 - tipo2)
 :precondition (and <predicati>)
 :effect (and <effetti>)
)
NON usare 'function', 'param', testo narrativo o altri formati.
"""),
            ("human", "Lore: {lore}\n\nAzioni:")
        ])
        result = (prompt | self.llm).invoke({"lore": self._format_lore()}).content
        actions = self._split_actions(result)
        normalized_actions = [self._normalize_text(a) for a in actions]
        return normalized_actions

    def infer_goal(self) -> str:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
ATTENZIONE: restituisci SOLO il goal PDDL valido.
Formato richiesto:
(and (predicato1) (predicato2))
Esempio:
(and (not (alive bandit_leader)) (at hero village))
"""),
            ("human", "Lore: {lore}\n\nGoal:")
        ])
        result = (prompt | self.llm).invoke({"lore": self._format_lore()}).content
        sanitized_goal = self._sanitize_goal(result.strip())
        normalized_goal = self._normalize_text(sanitized_goal)
        return normalized_goal

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
        """Assicura che preconditions ed effects siano wrappati in (and ...)"""
        def wrap_clause(text, keyword):
            pattern = rf"(:{keyword})\s*\(([^()]+)\)"
            return re.sub(pattern, rf":{keyword} (and (\2))", text)
        fixed = wrap_clause(action_text, "precondition")
        fixed = wrap_clause(fixed, "effect")
        return fixed

    def _sanitize_goal(self, goal: str) -> str:
        # Sostituisci predicati non definiti come 'present' con predicati definiti 'at'
        goal = goal.replace("present", "at")
        if goal.startswith("(and") and goal.endswith(")"):
            return goal
        matches = re.findall(r'\([^\(\)]+\)', goal)
        if not matches:
            return f"(and {goal})"
        return f"(and {' '.join(matches)})"
