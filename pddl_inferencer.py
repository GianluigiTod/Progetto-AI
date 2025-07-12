from lore import LoreDocument
from typing import List
import re
import spacy

nlp = spacy.load("it_core_news_md")  # usa un modello con word embeddings

class PDDLInferencer:
    def __init__(self, lore: LoreDocument):
        self.lore = lore

    def infer_predicates(self) -> List[str]:
        base_predicates = [
            "(at ?x - object ?l - location)",
            "(has ?c - character ?i - item)",
            "(connected ?l1 - location ?l2 - location)",
            "(alive ?c - character)"
        ]

        dynamic_predicates = []
        if re.search(r"salvare|rescue", self.lore.quest_description, re.IGNORECASE):
            dynamic_predicates.append("(rescued ?c - character)")
        if re.search(r"distrarre|distract", self.lore.quest_description, re.IGNORECASE):
            dynamic_predicates.append("(distracted ?c - character)")
        if re.search(r"parlare|talk|convincere|convince", self.lore.quest_description, re.IGNORECASE):
            dynamic_predicates.append("(convinced ?c - character)")

        dynamic_predicates += self._extract_dynamic_predicates()
        return list(set(base_predicates + dynamic_predicates))

    def infer_actions(self) -> List[str]:
        actions = []

        actions.append("""
  (:action move
    :parameters (?c - character ?from - location ?to - location)
    :precondition (and (at ?c ?from) (connected ?from ?to) (alive ?c))
    :effect (and (not (at ?c ?from)) (at ?c ?to))
  )""")

        if self.lore.items:
            actions.append("""
  (:action take
    :parameters (?c - character ?i - item ?l - location)
    :precondition (and (at ?c ?l) (at ?i ?l) (alive ?c))
    :effect (and (has ?c ?i) (not (at ?i ?l)))
  )""")

        if re.search(r"salvare|rescue", self.lore.quest_description, re.IGNORECASE):
            actions.append("""
  (:action rescue
    :parameters (?c - character ?p - character ?l - location)
    :precondition (and (at ?c ?l) (at ?p ?l) (alive ?c))
    :effect (rescued ?p)
  )""")

        if re.search(r"distrarre|distract", self.lore.quest_description, re.IGNORECASE):
            actions.append("""
  (:action distract
    :parameters (?c - character ?t - character ?l - location)
    :precondition (and (at ?c ?l) (at ?t ?l) (alive ?c) (alive ?t))
    :effect (distracted ?t)
  )""")

        if re.search(r"parlare|talk|convincere|convince", self.lore.quest_description, re.IGNORECASE):
            actions.append("""
  (:action convince
    :parameters (?c - character ?t - character ?l - location)
    :precondition (and (at ?c ?l) (at ?t ?l) (alive ?c) (alive ?t))
    :effect (convinced ?t)
  )""")

        actions += self._extract_dynamic_actions()
        return actions

    def infer_goal(self) -> str:
        q = self.lore.quest_description.lower()
        if "salvare" in q and len(self.lore.characters) > 1:
            return f"(rescued {self.lore.characters[1]})"
        elif "convincere" in q and len(self.lore.characters) > 1:
            return f"(convinced {self.lore.characters[1]})"
        elif "distrarre" in q and len(self.lore.characters) > 1:
            return f"(distracted {self.lore.characters[1]})"
        elif verb := self._extract_main_verb():
            if len(self.lore.characters) > 1:
                if self._is_lethal_verb(verb):
                    return f"(defeated {self.lore.characters[1]})"
                else:
                    return f"({verb}ed {self.lore.characters[1]})"
        elif self.lore.items:
            return f"(has {self.lore.characters[0]} {self.lore.items[0]})"
        else:
            return f"(at {self.lore.characters[0]} {self.lore.locations[-1]})"

    def _extract_main_verb(self) -> str:
        doc = nlp(self.lore.quest_description)
        for token in doc:
            if token.pos_ == "VERB" and token.lemma_ not in ["essere", "avere"]:
                return token.lemma_
        return ""

    def _extract_dynamic_actions(self) -> List[str]:
        doc = nlp(self.lore.quest_description)
        actions = []
        existing = {"move", "take", "attack", "rescue", "distract", "convince"}

        for token in doc:
            if token.pos_ == "VERB" and token.lemma_ not in existing and token.lemma_ not in ["essere", "avere"]:
                name = token.lemma_
                if self._is_lethal_verb(name):
                    effect = f"(and (not (alive ?o)) (defeated ?o))"
                else:
                    effect = f"({name}ed ?o)"

                action = f"""
  (:action {name}
    :parameters (?c - character ?o - character ?w - item ?l - location)
    :precondition (and (at ?c ?l) (at ?o ?l) (has ?c ?w) (alive ?c) (alive ?o))
    :effect {effect}
  )"""
                actions.append(action)

        return actions

    def _extract_dynamic_predicates(self) -> List[str]:
        doc = nlp(self.lore.quest_description)
        predicates = []
        existing = {"at", "has", "connected", "alive", "rescued", "defeated", "distracted", "convinced"}

        for token in doc:
            if token.pos_ == "VERB" and token.lemma_ not in existing and token.lemma_ not in ["essere", "avere"]:
                lemma = token.lemma_
                if self._is_lethal_verb(lemma):
                    predicates.append("(defeated ?x - character)")
                else:
                    pred_name = lemma + "ed"
                    predicates.append(f"({pred_name} ?x - character)")

        return predicates

    def _is_lethal_verb(self, lemma: str) -> bool:
        """Stima dinamicamente se un verbo implica sconfitta/morte, usando similarità semantica."""
        base_doc = nlp(lemma)
        if not base_doc or not base_doc.vector_norm:
            return False

        lethal_archetypes = ["uccidere", "sconfiggere", "eliminare", "ammazzare"]
        similarities = []

        for lethal in lethal_archetypes:
            lethal_doc = nlp(lethal)
            if lethal_doc and lethal_doc.vector_norm:
                sim = base_doc.similarity(lethal_doc)
                similarities.append(sim)

        return any(score > 0.75 for score in similarities)


