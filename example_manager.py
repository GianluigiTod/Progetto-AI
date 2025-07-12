from typing import Dict, List, Optional


class ExampleManager:
    """Gestisce gli esempi di PDDL ben formati con separazione chiara di domini e problemi"""
    
    def __init__(self):
        self.examples = self._load_examples()
    
    def _load_examples(self) -> Dict[str, Dict[str, str]]:
        """Carica esempi di PDDL dalla libreria interna"""
        return {
            "classic_adventure": {
                "description": "Avventura classica con eroe, villain e tesoro",
                "domain": """(define (domain classic_adventure)
  (:requirements :strips :typing)
  (:types
    character location item - object
    hero villain - character
    weapon treasure - item
  )
  (:predicates
    (at ?x - object ?l - location)
    (has ?c - character ?i - item)
    (alive ?c - character)
    (equipped ?c - character ?w - weapon)
    (defeated ?v - villain)
    (connected ?l1 - location ?l2 - location)
  )
  (:action move
    :parameters (?c - character ?from - location ?to - location)
    :precondition (and (at ?c ?from) (connected ?from ?to) (alive ?c))
    :effect (and (not (at ?c ?from)) (at ?c ?to))
  )
  (:action take
    :parameters (?c - character ?i - item ?l - location)
    :precondition (and (at ?c ?l) (at ?i ?l) (alive ?c))
    :effect (and (has ?c ?i) (not (at ?i ?l)))
  )
  (:action equip
    :parameters (?c - character ?w - weapon)
    :precondition (and (has ?c ?w) (alive ?c))
    :effect (equipped ?c ?w)
  )
  (:action fight
    :parameters (?h - hero ?v - villain ?w - weapon ?l - location)
    :precondition (and (at ?h ?l) (at ?v ?l) (equipped ?h ?w) (alive ?h) (alive ?v))
    :effect (and (defeated ?v) (not (alive ?v)))
  )
)""",
                "problem": """(define (problem hero_quest)
  (:domain classic_adventure)
  (:objects
    hero1 - hero
    villain1 - villain
    sword1 - weapon
    treasure1 - treasure
    castle dungeon - location
  )
  (:init
    (at hero1 castle)
    (at villain1 dungeon)
    (at sword1 castle)
    (at treasure1 dungeon)
    (alive hero1)
    (alive villain1)
    (connected castle dungeon)
    (connected dungeon castle)
  )
  (:goal (and
    (has hero1 treasure1)
    (defeated villain1)
  ))
)"""
            },
            "rescue_mission": {
                "description": "Missione di salvataggio con chiavi e guardie",
                "domain": """(define (domain rescue_ops)
  (:requirements :strips :typing)
  (:types
    character location item - object
    hero prisoner guard - character
    key - item
  )
  (:predicates
    (at ?x - object ?l - location)
    (has ?c - character ?i - item)
    (alive ?c - character)
    (imprisoned ?p - prisoner)
    (rescued ?p - prisoner)
    (locked ?l - location)
    (connected ?l1 - location ?l2 - location)
  )
  (:action move
    :parameters (?c - character ?from - location ?to - location)
    :precondition (and (at ?c ?from) (connected ?from ?to) (alive ?c) (not (locked ?to)))
    :effect (and (not (at ?c ?from)) (at ?c ?to))
  )
  (:action take
    :parameters (?c - character ?i - item ?l - location)
    :precondition (and (at ?c ?l) (at ?i ?l) (alive ?c))
    :effect (and (has ?c ?i) (not (at ?i ?l)))
  )
  (:action unlock
    :parameters (?c - character ?k - key ?l - location)
    :precondition (and (at ?c ?l) (has ?c ?k) (alive ?c) (locked ?l))
    :effect (not (locked ?l))
  )
  (:action rescue
    :parameters (?h - hero ?p - prisoner ?l - location)
    :precondition (and (at ?h ?l) (at ?p ?l) (alive ?h) (imprisoned ?p) (not (locked ?l)))
    :effect (and (rescued ?p) (not (imprisoned ?p)))
  )
)""",
                "problem": """(define (problem prison_break)
  (:domain rescue_ops)
  (:objects
    hero1 - hero
    prisoner1 - prisoner
    guard1 - guard
    key1 - key
    entrance prison_cell - location
  )
  (:init
    (at hero1 entrance)
    (at prisoner1 prison_cell)
    (at guard1 prison_cell)
    (at key1 entrance)
    (alive hero1)
    (alive guard1)
    (imprisoned prisoner1)
    (locked prison_cell)
    (connected entrance prison_cell)
    (connected prison_cell entrance)
  )
  (:goal (and
    (rescued prisoner1)
    (at prisoner1 entrance)
  ))
)"""
            }
        }
    
    def get_example(self, name: str) -> Optional[Dict[str, str]]:
        """Restituisce un esempio specifico"""
        return self.examples.get(name)
    
    def list_examples(self) -> List[str]:
        """Elenca tutti gli esempi disponibili"""
        return list(self.examples.keys())
    
    def get_domain_examples_for_prompt(self) -> str:
        """Restituisce SOLO esempi di domini per prompt di personalizzazione dominio"""
        examples_text = "ESEMPI DI DOMINI PDDL VALIDI:\n\n"
        
        for name, example in self.examples.items():
            examples_text += f"# DOMINIO: {name.replace('_', ' ').title()}\n"
            examples_text += f"# {example['description']}\n\n"
            examples_text += example['domain']
            examples_text += "\n\n"
        
        return examples_text
    
    def get_problem_examples_for_prompt(self) -> str:
        """Restituisce SOLO esempi di problemi per prompt di personalizzazione problema"""
        examples_text = "ESEMPI DI PROBLEMI PDDL VALIDI:\n\n"
        
        for name, example in self.examples.items():
            examples_text += f"# PROBLEMA: {name.replace('_', ' ').title()}\n"
            examples_text += f"# {example['description']}\n\n"
            examples_text += example['problem']
            examples_text += "\n\n"
        
        return examples_text

    
    
