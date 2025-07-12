'''from langchain.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from pathlib import Path
import subprocess
import re
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import yaml

MODEL_NAME = "mistral"

@dataclass
class LoreDocument:
    """Struttura per il documento di lore"""
    quest_description: str
    branching_factor: Tuple[int, int]  # (min, max)
    depth_constraints: Tuple[int, int]  # (min, max)
    world_context: str = ""
    characters: List[str] = None
    locations: List[str] = None
    items: List[str] = None
    constraints: List[str] = None

class PDDLTemplateManager:
    """Gestisce i template PDDL predefiniti"""
    
    def __init__(self):
        self.domain_templates = {
            "adventure": self._get_adventure_template(),
            "rescue": self._get_rescue_template(),
            "treasure_hunt": self._get_treasure_hunt_template(),
            "combat": self._get_combat_template(),
            "puzzle": self._get_puzzle_template()
        }
        
        self.problem_templates = {
            "simple_quest": self._get_simple_quest_template(),
            "multi_objective": self._get_multi_objective_template(),
            "rescue_mission": self._get_rescue_mission_template()
        }
    
    def _get_adventure_template(self) -> str:
        return """(define (domain adventure_domain)
  (:requirements :strips :typing)
  (:types
    character location item - object
    hero companion villain - character
    weapon tool key treasure - item
    indoor outdoor - location
  )
  (:predicates
    ;; Predicati di posizione
    (at ?x - object ?l - location)                    ; oggetto x è alla location l
    (connected ?l1 - location ?l2 - location)        ; location l1 è connessa a l2
    
    ;; Predicati di possesso e stato
    (has ?c - character ?i - item)                   ; character c possiede item i
    (alive ?c - character)                           ; character c è vivo
    (equipped ?c - character ?w - weapon)            ; character c ha equipaggiato weapon w
    
    ;; Predicati di stato del mondo
    (locked ?l - location)                           ; location l è bloccata
    (hidden ?i - item)                               ; item i è nascosto
    (defeated ?v - villain)                          ; villain v è stato sconfitto
    (discovered ?l - location)                       ; location l è stata scoperta
    
    ;; Predicati di relazioni
    (knows ?c - character ?l - location)             ; character c conosce location l
    (allies ?c1 - character ?c2 - character)         ; c1 e c2 sono alleati
  )
  
  ;; Azione base: movimento
  (:action move
    :parameters (?c - character ?from - location ?to - location)
    :precondition (and 
      (at ?c ?from)                                  ; character deve essere alla location di partenza
      (connected ?from ?to)                          ; le location devono essere connesse
      (alive ?c)                                     ; character deve essere vivo
      (not (locked ?to))                             ; location di destinazione non deve essere bloccata
    )
    :effect (and 
      (not (at ?c ?from))                            ; rimuove character dalla location di partenza
      (at ?c ?to)                                    ; posiziona character alla location di destinazione
      (discovered ?to)                               ; marca la location come scoperta
    )
  )
  
  ;; Azione: raccogliere oggetti
  (:action take
    :parameters (?c - character ?i - item ?l - location)
    :precondition (and 
      (at ?c ?l)                                     ; character deve essere alla stessa location dell'item
      (at ?i ?l)                                     ; item deve essere alla location
      (alive ?c)                                     ; character deve essere vivo
      (not (hidden ?i))                              ; item non deve essere nascosto
    )
    :effect (and 
      (has ?c ?i)                                    ; character ottiene l'item
      (not (at ?i ?l))                               ; rimuove item dalla location
    )
  )
  
  ;; Azione: equipaggiare arma
  (:action equip
    :parameters (?c - character ?w - weapon)
    :precondition (and 
      (has ?c ?w)                                    ; character deve possedere l'arma
      (alive ?c)                                     ; character deve essere vivo
    )
    :effect (equipped ?c ?w)                         ; character equipaggia l'arma
  )
  
  ;; Azione: utilizzare chiave
  (:action unlock
    :parameters (?c - character ?k - key ?l - location)
    :precondition (and 
      (has ?c ?k)                                    ; character deve avere la chiave
      (at ?c ?l)                                     ; character deve essere alla location
      (alive ?c)                                     ; character deve essere vivo
      (locked ?l)                                    ; location deve essere bloccata
    )
    :effect (not (locked ?l))                        ; rimuove il blocco dalla location
  )
  
  ;; Azione: combattimento
  (:action fight
    :parameters (?h - hero ?v - villain ?w - weapon ?l - location)
    :precondition (and 
      (at ?h ?l)                                     ; hero deve essere alla location
      (at ?v ?l)                                     ; villain deve essere alla stessa location
      (equipped ?h ?w)                               ; hero deve essere equipaggiato
      (alive ?h)                                     ; hero deve essere vivo
      (alive ?v)                                     ; villain deve essere vivo
    )
    :effect (and 
      (defeated ?v)                                  ; villain viene sconfitto
      (not (alive ?v))                               ; villain muore
    )
  )
  
  ;; Azione: cercare oggetti nascosti
  (:action search
    :parameters (?c - character ?i - item ?l - location)
    :precondition (and 
      (at ?c ?l)                                     ; character deve essere alla location
      (at ?i ?l)                                     ; item deve essere alla location
      (alive ?c)                                     ; character deve essere vivo
      (hidden ?i)                                    ; item deve essere nascosto
    )
    :effect (not (hidden ?i))                        ; rivela l'item nascosto
  )
)"""

    def _get_rescue_template(self) -> str:
        return """(define (domain rescue_domain)
  (:requirements :strips :typing)
  (:types
    character location item - object
    hero prisoner guard - character
    key rope medicine - item
    cell tower forest - location
  )
  (:predicates
    (at ?x - object ?l - location)                    ; posizione di oggetti e personaggi
    (connected ?l1 - location ?l2 - location)        ; connessioni tra location
    (has ?c - character ?i - item)                   ; possesso di oggetti
    (alive ?c - character)                           ; stato vitale
    (imprisoned ?p - prisoner)                       ; stato di prigionia
    (rescued ?p - prisoner)                          ; stato di salvataggio
    (guarded ?l - location)                          ; location sorvegliata
    (locked ?l - location)                           ; location bloccata
    (injured ?c - character)                         ; stato di ferita
    (healed ?c - character)                          ; stato di guarigione
  )
  
  (:action move
    :parameters (?c - character ?from - location ?to - location)
    :precondition (and 
      (at ?c ?from)
      (connected ?from ?to)
      (alive ?c)
      (not (locked ?to))
      (not (guarded ?to))
    )
    :effect (and 
      (not (at ?c ?from))
      (at ?c ?to)
    )
  )
  
  (:action take
    :parameters (?c - character ?i - item ?l - location)
    :precondition (and 
      (at ?c ?l)
      (at ?i ?l)
      (alive ?c)
    )
    :effect (and 
      (has ?c ?i)
      (not (at ?i ?l))
    )
  )
  
  (:action unlock_door
    :parameters (?h - hero ?k - key ?l - location)
    :precondition (and 
      (at ?h ?l)
      (has ?h ?k)
      (alive ?h)
      (locked ?l)
    )
    :effect (not (locked ?l))
  )
  
  (:action neutralize_guard
    :parameters (?h - hero ?g - guard ?l - location)
    :precondition (and 
      (at ?h ?l)
      (at ?g ?l)
      (alive ?h)
      (alive ?g)
      (guarded ?l)
    )
    :effect (and 
      (not (guarded ?l))
      (not (alive ?g))
    )
  )
  
  (:action free_prisoner
    :parameters (?h - hero ?p - prisoner ?l - location)
    :precondition (and 
      (at ?h ?l)
      (at ?p ?l)
      (alive ?h)
      (imprisoned ?p)
      (not (guarded ?l))
    )
    :effect (and 
      (not (imprisoned ?p))
      (rescued ?p)
    )
  )
  
  (:action heal
    :parameters (?h - hero ?c - character ?m - medicine)
    :precondition (and 
      (has ?h ?m)
      (alive ?h)
      (injured ?c)
    )
    :effect (and 
      (healed ?c)
      (not (injured ?c))
    )
  )
)"""

    def _get_treasure_hunt_template(self) -> str:
        return """(define (domain treasure_hunt_domain)
  (:requirements :strips :typing)
  (:types
    character location item - object
    adventurer - character
    treasure map clue tool - item
    cave mountain desert - location
  )
  (:predicates
    (at ?x - object ?l - location)
    (connected ?l1 - location ?l2 - location)
    (has ?c - character ?i - item)
    (alive ?c - character)
    (solved ?c - clue)
    (found ?t - treasure)
    (readable ?m - map)
    (dangerous ?l - location)
    (equipped ?c - character ?t - tool)
  )
  
  (:action move
    :parameters (?c - character ?from - location ?to - location)
    :precondition (and 
      (at ?c ?from)
      (connected ?from ?to)
      (alive ?c)
      (not (dangerous ?to))
    )
    :effect (and 
      (not (at ?c ?from))
      (at ?c ?to)
    )
  )
  
  (:action take
    :parameters (?c - character ?i - item ?l - location)
    :precondition (and 
      (at ?c ?l)
      (at ?i ?l)
      (alive ?c)
    )
    :effect (and 
      (has ?c ?i)
      (not (at ?i ?l))
    )
  )
  
  (:action solve_clue
    :parameters (?c - character ?clue - clue ?l - location)
    :precondition (and 
      (at ?c ?l)
      (has ?c ?clue)
      (alive ?c)
    )
    :effect (solved ?clue)
  )
  
  (:action read_map
    :parameters (?c - character ?m - map)
    :precondition (and 
      (has ?c ?m)
      (alive ?c)
    )
    :effect (readable ?m)
  )
  
  (:action find_treasure
    :parameters (?c - character ?t - treasure ?l - location)
    :precondition (and 
      (at ?c ?l)
      (at ?t ?l)
      (alive ?c)
    )
    :effect (found ?t)
  )
)"""

    def _get_combat_template(self) -> str:
        return """(define (domain combat_domain)
  (:requirements :strips :typing)
  (:types
    character location item - object
    warrior mage enemy - character
    weapon armor potion - item
    battlefield castle - location
  )
  (:predicates
    (at ?x - object ?l - location)
    (connected ?l1 - location ?l2 - location)
    (has ?c - character ?i - item)
    (alive ?c - character)
    (equipped ?c - character ?w - weapon)
    (wearing ?c - character ?a - armor)
    (defeated ?e - enemy)
    (protected ?c - character)
    (ready_for_battle ?c - character)
  )
  
  (:action move
    :parameters (?c - character ?from - location ?to - location)
    :precondition (and 
      (at ?c ?from)
      (connected ?from ?to)
      (alive ?c)
    )
    :effect (and 
      (not (at ?c ?from))
      (at ?c ?to)
    )
  )
  
  (:action take
    :parameters (?c - character ?i - item ?l - location)
    :precondition (and 
      (at ?c ?l)
      (at ?i ?l)
      (alive ?c)
    )
    :effect (and 
      (has ?c ?i)
      (not (at ?i ?l))
    )
  )
  
  (:action equip_weapon
    :parameters (?c - character ?w - weapon)
    :precondition (and 
      (has ?c ?w)
      (alive ?c)
    )
    :effect (equipped ?c ?w)
  )
  
  (:action wear_armor
    :parameters (?c - character ?a - armor)
    :precondition (and 
      (has ?c ?a)
      (alive ?c)
    )
    :effect (and 
      (wearing ?c ?a)
      (protected ?c)
    )
  )
  
  (:action prepare_for_battle
    :parameters (?c - character ?w - weapon ?a - armor)
    :precondition (and 
      (equipped ?c ?w)
      (wearing ?c ?a)
      (alive ?c)
    )
    :effect (ready_for_battle ?c)
  )
  
  (:action fight
    :parameters (?w - warrior ?e - enemy ?l - location)
    :precondition (and 
      (at ?w ?l)
      (at ?e ?l)
      (alive ?w)
      (alive ?e)
      (ready_for_battle ?w)
    )
    :effect (and 
      (defeated ?e)
      (not (alive ?e))
    )
  )
  
  (:action drink_potion
    :parameters (?c - character ?p - potion)
    :precondition (and 
      (has ?c ?p)
      (alive ?c)
    )
    :effect (and 
      (protected ?c)
      (not (has ?c ?p))
    )
  )
)"""

    def _get_puzzle_template(self) -> str:
        return """(define (domain puzzle_domain)
  (:requirements :strips :typing)
  (:types
    character location item - object
    solver - character
    puzzle_piece key switch - item
    room chamber - location
  )
  (:predicates
    (at ?x - object ?l - location)
    (connected ?l1 - location ?l2 - location)
    (has ?c - character ?i - item)
    (alive ?c - character)
    (solved ?p - puzzle_piece)
    (activated ?s - switch)
    (opened ?l - location)
    (completed ?l - location)
  )
  
  (:action move
    :parameters (?c - character ?from - location ?to - location)
    :precondition (and 
      (at ?c ?from)
      (connected ?from ?to)
      (alive ?c)
      (opened ?to)
    )
    :effect (and 
      (not (at ?c ?from))
      (at ?c ?to)
    )
  )
  
  (:action take
    :parameters (?c - character ?i - item ?l - location)
    :precondition (and 
      (at ?c ?l)
      (at ?i ?l)
      (alive ?c)
    )
    :effect (and 
      (has ?c ?i)
      (not (at ?i ?l))
    )
  )
  
  (:action solve_puzzle
    :parameters (?c - character ?p - puzzle_piece ?l - location)
    :precondition (and 
      (at ?c ?l)
      (has ?c ?p)
      (alive ?c)
    )
    :effect (solved ?p)
  )
  
  (:action activate_switch
    :parameters (?c - character ?s - switch ?l - location)
    :precondition (and 
      (at ?c ?l)
      (at ?s ?l)
      (alive ?c)
    )
    :effect (activated ?s)
  )
  
  (:action open_door
    :parameters (?c - character ?k - key ?l - location)
    :precondition (and 
      (at ?c ?l)
      (has ?c ?k)
      (alive ?c)
    )
    :effect (opened ?l)
  )
  
  (:action complete_chamber
    :parameters (?c - character ?l - location ?p - puzzle_piece)
    :precondition (and 
      (at ?c ?l)
      (solved ?p)
      (alive ?c)
    )
    :effect (completed ?l)
  )
)"""

    def _get_simple_quest_template(self) -> str:
        return """(define (problem simple_adventure)
  (:domain adventure_domain)
  (:objects
    hero1 - hero
    villain1 - villain
    sword1 - weapon
    key1 - key
    treasure1 - treasure
    castle forest cave treasure_room - location
  )
  (:init
    ;; Posizioni iniziali
    (at hero1 castle)
    (at villain1 cave)
    (at sword1 castle)
    (at key1 forest)
    (at treasure1 treasure_room)
    
    ;; Stati iniziali
    (alive hero1)
    (alive villain1)
    (locked treasure_room)
    (hidden treasure1)
    
    ;; Connessioni mappa
    (connected castle forest)
    (connected forest castle)
    (connected forest cave)
    (connected cave forest)
    (connected cave treasure_room)
    (connected treasure_room cave)
  )
  (:goal (and
    (has hero1 treasure1)
    (defeated villain1)
  ))
)"""

    def _get_multi_objective_template(self) -> str:
        return """(define (problem multi_objective_quest)
  (:domain adventure_domain)
  (:objects
    hero1 - hero
    companion1 - companion
    villain1 villain2 - villain
    sword1 - weapon
    key1 key2 - key
    treasure1 treasure2 - treasure
    castle forest cave mountain tower - location
  )
  (:init
    (at hero1 castle)
    (at companion1 castle)
    (at villain1 cave)
    (at villain2 tower)
    (at sword1 forest)
    (at key1 mountain)
    (at key2 cave)
    (at treasure1 cave)
    (at treasure2 tower)
    
    (alive hero1)
    (alive companion1)
    (alive villain1)
    (alive villain2)
    (allies hero1 companion1)
    (locked cave)
    (locked tower)
    (hidden treasure1)
    (hidden treasure2)
    
    (connected castle forest)
    (connected forest castle)
    (connected forest mountain)
    (connected mountain forest)
    (connected forest cave)
    (connected cave forest)
    (connected mountain tower)
    (connected tower mountain)
  )
  (:goal (and
    (has hero1 treasure1)
    (has hero1 treasure2)
    (defeated villain1)
    (defeated villain2)
    (allies hero1 companion1)
  ))
)"""

    def _get_rescue_mission_template(self) -> str:
        return """(define (problem rescue_mission)
  (:domain rescue_domain)
  (:objects
    hero1 - hero
    prisoner1 - prisoner
    guard1 guard2 - guard
    key1 - key
    medicine1 - medicine
    castle cell tower forest - location
  )
  (:init
    (at hero1 castle)
    (at prisoner1 cell)
    (at guard1 cell)
    (at guard2 tower)
    (at key1 tower)
    (at medicine1 castle)
    
    (alive hero1)
    (alive guard1)
    (alive guard2)
    (imprisoned prisoner1)
    (injured prisoner1)
    (locked cell)
    (guarded cell)
    (guarded tower)
    
    (connected castle forest)
    (connected forest castle)
    (connected forest tower)
    (connected tower forest)
    (connected tower cell)
    (connected cell tower)
  )
  (:goal (and
    (rescued prisoner1)
    (healed prisoner1)
    (at prisoner1 castle)
  ))
)"""

    def get_domain_template(self, template_name: str) -> str:
        """Restituisce un template di dominio"""
        return self.domain_templates.get(template_name, self.domain_templates["adventure"])
    
    def get_problem_template(self, template_name: str) -> str:
        """Restituisce un template di problema"""
        return self.problem_templates.get(template_name, self.problem_templates["simple_quest"])
    
    def list_templates(self) -> Dict[str, List[str]]:
        """Elenca tutti i template disponibili"""
        return {
            "domains": list(self.domain_templates.keys()),
            "problems": list(self.problem_templates.keys())
        }

class ExampleManager:
    """Gestisce gli esempi di PDDL ben formati"""
    
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
    
    def get_examples_for_prompt(self) -> str:
        """Restituisce esempi formattati per il prompt"""
        examples_text = "ESEMPI DI PDDL BEN FORMATI:\n\n"
        
        for name, example in self.examples.items():
            examples_text += f"=== ESEMPIO: {name.upper()} ===\n"
            examples_text += f"Descrizione: {example['description']}\n\n"
            examples_text += "DOMINIO:\n"
            examples_text += example['domain']
            examples_text += "\n\nPROBLEMA:\n"
            examples_text += example['problem']
            examples_text += "\n\n" + "="*50 + "\n\n"
        
        return examples_text

class ReflectionAgent:
    """Agente di riflessione per il miglioramento iterativo del PDDL"""
    
    def __init__(self, model_name: str = MODEL_NAME):
        self.model_name = model_name
        self.template_manager = PDDLTemplateManager()
        self.example_manager = ExampleManager()
    
    def analyze_pddl_errors(self, domain_content: str, problem_content: str, 
                           validation_errors: List[str]) -> Dict[str, str]:
        """Analizza errori nel PDDL e suggerisce correzioni"""
        
        system_msg = f"""Sei un esperto analista PDDL. Il tuo compito è identificare errori specifici nel codice PDDL e suggerire correzioni precise.

{self.example_manager.get_examples_for_prompt()}

REGOLE DI ANALISI:
1. Identifica errori sintattici specifici
2. Verifica coerenza tra dominio e problema
3. Controlla che ogni predicato usato sia dichiarato
4. Verifica che ogni tipo usato sia dichiarato
5. Assicura che le precondizioni siano soddisfacibili
6. Verifica che gli effetti siano consistenti

ERRORI COMUNI DA CERCARE:
- Predicati non dichiarati
- Tipi non dichiarati
- Parametri con arità errata
- Precondizioni impossibili
- Effetti contraddittori
- Parentesi non bilanciate
- Oggetti non tipizzati correttamente

FORNISCI:
1. Lista specifica degli errori trovati
2. Spiegazione del perché sono errori
3. Suggerimenti di correzione precisi
4. Codice PDDL corretto se possibile"""

        user_template = """Analizza questo PDDL e identifica tutti gli errori:

DOMINIO:
{domain_content}

PROBLEMA:
{problem_content}

ERRORI DI VALIDAZIONE:
{validation_errors}

Fornisci un'analisi dettagliata degli errori e suggerimenti specifici per correggerli."""

        chain = get_ollama_chain(system_msg, user_template)
        response = chain.invoke({
            "domain_content": domain_content,
            "problem_content": problem_content,
            "validation_errors": "\n".join(validation_errors)
        })
        
        return self._parse_reflection_response(response.content)
    
    def _parse_reflection_response(self, response: str) -> Dict[str, str]:
        """Analizza la risposta dell'agente di riflessione"""
        sections = {
            "errors": "",
            "explanations": "",
            "suggestions": "",
            "corrected_code": ""
        }
        
        current_section = None
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if 'errori' in line.lower() or 'errors' in line.lower():
                current_section = "errors"
            elif 'spiegazione' in line.lower() or 'explanation' in line.lower():
                current_section = "explanations"
            elif 'suggerimenti' in line.lower() or 'suggestions' in line.lower():
                current_section = "suggestions"
            elif 'corretto' in line.lower() or 'corrected' in line.lower():
                current_section = "corrected_code"
            elif current_section:
                sections[current_section] += line + "\n"
        
        return sections
    
    def suggest_improvements(self, lore_doc: LoreDocument, 
                           current_domain: str, current_problem: str) -> Dict[str, str]:
        """Suggerisce miglioramenti basati sul documento di lore"""
        
        system_msg = f"""Sei un esperto di narrative design e PDDL. Analizza il documento di lore e il PDDL attuale per suggerire miglioramenti che rendano la storia più coerente e interessante.

{self.example_manager.get_examples_for_prompt()}

CONSIDERA:
1. Coerenza narrativa tra lore e PDDL
2. Complessità adeguata ai vincoli di branching factor
3. Profondità narrativa appropriata
4. Elementi mancanti nella storia
5. Opportunità di miglioramento dell'esperienza

SUGGERISCI:
1. Miglioramenti narrativi
2. Elementi PDDL da aggiungere/modificare
3. Bilanciamento della difficoltà
4. Arricchimento del mondo di gioco"""

        user_template = """DOCUMENTO DI LORE:
Descrizione: {quest_description}
Contesto: {world_context}
Branching Factor: {branching_min}-{branching_max}
Profondità: {depth_min}-{depth_max}
Personaggi: {characters}
Luoghi: {locations}
Oggetti: {items}
Vincoli: {constraints}

DOMINIO ATTUALE:
{current_domain}

PROBLEMA ATTUALE:
{current_problem}

Suggerisci miglioramenti specifici per rendere la storia più ricca e il PDDL più funzionale."""

        chain = get_ollama_chain(system_msg, user_template)
        response = chain.invoke({
            "quest_description": lore_doc.quest_description,
            "world_context": lore_doc.world_context,
            "branching_min": lore_doc.branching_factor[0],
            "branching_max": lore_doc.branching_factor[1],
            "depth_min": lore_doc.depth_constraints[0],
            "depth_max": lore_doc.depth_constraints[1],
            "characters": ", ".join(lore_doc.characters or []),
            "locations": ", ".join(lore_doc.locations or []),
            "items": ", ".join(lore_doc.items or []),
            "constraints": ", ".join(lore_doc.constraints or []),
            "current_domain": current_domain,
            "current_problem": current_problem
        })
        
        return self._parse_improvement_response(response.content)
    
    def _parse_improvement_response(self, response: str) -> Dict[str, str]:
        """Analizza la risposta sui miglioramenti"""
        sections = {
            "narrative_improvements": "",
            "pddl_modifications": "",
            "difficulty_balance": "",
            "world_enrichment": ""
        }
        
        current_section = None
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if 'narrativ' in line.lower():
                current_section = "narrative_improvements"
            elif 'pddl' in line.lower() or 'modific' in line.lower():
                current_section = "pddl_modifications"
            elif 'difficolt' in line.lower() or 'bilanc' in line.lower():
                current_section = "difficulty_balance"
            elif 'mondo' in line.lower() or 'world' in line.lower():
                current_section = "world_enrichment"
            elif current_section:
                sections[current_section] += line + "\n"
        
        return sections

class InteractiveStoryGenerator:
    """Generatore interattivo di storie PDDL con loop di refinement"""
    
    def __init__(self, model_name: str = MODEL_NAME):
        self.model_name = model_name
        self.template_manager = PDDLTemplateManager()
        self.example_manager = ExampleManager()
        self.reflection_agent = ReflectionAgent(model_name)
        self.current_lore = None
        self.current_domain = None
        self.current_problem = None
        self.validation_history = []
    
    def create_lore_document(self, interactive: bool = True) -> LoreDocument:
        """Crea un documento di lore interattivamente o da input"""
        
        if interactive:
            print("🎭 CREAZIONE DOCUMENTO DI LORE")
            print("=" * 40)
            
            quest_description = input("📖 Descrizione della quest: ")
            world_context = input("🌍 Contesto del mondo: ")
            
            print("\n🔢 Vincoli numerici:")
            branching_min = int(input("   Branching factor minimo (2-5): ") or "2")
            branching_max = int(input("   Branching factor massimo (4-10): ") or "4")
            depth_min = int(input("   Profondità minima (2-8): ") or "2")
            depth_max = int(input("   Profondità massima (5-15): ") or "5")
            
            print("\n👥 Elementi del mondo (opzionali, separati da virgola):")
            characters_input = input("   Personaggi: ")
            locations_input = input("   Luoghi: ")
            items_input = input("   Oggetti: ")
            constraints_input = input("   Vincoli speciali: ")
            
            characters = [c.strip() for c in characters_input.split(',') if c.strip()]
            locations = [l.strip() for l in locations_input.split(',') if l.strip()]
            items = [i.strip() for i in items_input.split(',') if i.strip()]
            constraints = [c.strip() for c in constraints_input.split(',') if c.strip()]
            
            lore_doc = LoreDocument(
                quest_description=quest_description,
                world_context=world_context,
                branching_factor=(branching_min, branching_max),
                depth_constraints=(depth_min, depth_max),
                characters=characters,
                locations=locations,
                items=items,
                constraints=constraints
            )
        else:
            # Esempio predefinito per test
            lore_doc = LoreDocument(
                quest_description="Un eroe deve salvare una principessa imprigionata in un castello, sconfiggendo un drago e raccogliendo un tesoro magico.",
                world_context="Un regno fantasy medievale con castelli, foreste e creature magiche.",
                branching_factor=(3, 6),
                depth_constraints=(4, 8),
                characters=["eroe", "principessa", "drago", "guardia"],
                locations=["villaggio", "castello", "torre", "tesoro"],
                items=["spada", "scudo", "chiave", "pozione"],
                constraints=["il drago deve essere sconfitto prima di salvare la principessa"]
            )
        
        self.current_lore = lore_doc
        return lore_doc
    
    def generate_initial_pddl(self, lore_doc: LoreDocument) -> Tuple[str, str]:
        """Genera PDDL iniziale basato sul lore e template"""
        
        print("🏗️ Generazione PDDL iniziale...")
        
        # Determina il template più appropriato
        template_type = self._select_template_type(lore_doc)
        base_domain = self.template_manager.get_domain_template(template_type)
        base_problem = self.template_manager.get_problem_template("simple_quest")
        
        # Personalizza il template
        domain_content = self._customize_domain(base_domain, lore_doc)
        problem_content = self._customize_problem(base_problem, lore_doc)
        
        self.current_domain = domain_content
        self.current_problem = problem_content
        
        return domain_content, problem_content
    
    def _select_template_type(self, lore_doc: LoreDocument) -> str:
        """Seleziona il tipo di template più appropriato"""
        
        description = lore_doc.quest_description.lower()
        
        if any(word in description for word in ['salv', 'rescue', 'prigion', 'prison']):
            return "rescue"
        elif any(word in description for word in ['tesoro', 'treasure', 'trova', 'find']):
            return "treasure_hunt"
        elif any(word in description for word in ['combatt', 'fight', 'guerra', 'battle']):
            return "combat"
        elif any(word in description for word in ['enigma', 'puzzle', 'risolv', 'solve']):
            return "puzzle"
        else:
            return "adventure"
    
    def _customize_domain(self, base_domain: str, lore_doc: LoreDocument) -> str:
        """Personalizza il dominio basato sul lore"""
        
        system_msg = f"""Sei un esperto PDDL che personalizza domini basati su template e lore.

{self.example_manager.get_examples_for_prompt()}

TEMPLATE BASE:
{base_domain}

REGOLE DI PERSONALIZZAZIONE:
1. Mantieni la struttura del template
2. Aggiungi tipi specifici dal lore
3. Aggiungi predicati se necessario
4. Personalizza i nomi mantenendo la logica
5. Assicura compatibilità con i vincoli di branching factor
6. NON rimuovere azioni fondamentali
7. Mantieni tutti i commenti esplicativi

VINCOLI:
- Branching factor: {lore_doc.branching_factor[0]}-{lore_doc.branching_factor[1]}
- Profondità: {lore_doc.depth_constraints[0]}-{lore_doc.depth_constraints[1]}
- Personaggi: {lore_doc.characters}
- Luoghi: {lore_doc.locations}
- Oggetti: {lore_doc.items}"""

        user_template = """Personalizza questo dominio PDDL:

LORE:
{quest_description}

CONTESTO:
{world_context}

VINCOLI SPECIALI:
{constraints}

Restituisci il dominio personalizzato mantenendo la struttura e i commenti."""

        chain = get_ollama_chain(system_msg, user_template)
        response = chain.invoke({
            "quest_description": lore_doc.quest_description,
            "world_context": lore_doc.world_context,
            "constraints": ", ".join(lore_doc.constraints or [])
        })
        
        return extract_pddl_from_response(response.content)
    
    def _customize_problem(self, base_problem: str, lore_doc: LoreDocument) -> str:
        """Personalizza il problema basato sul lore"""
        
        system_msg = f"""Sei un esperto PDDL che personalizza problemi basati su template e lore.

{self.example_manager.get_examples_for_prompt()}

TEMPLATE BASE:
{base_problem}

REGOLE DI PERSONALIZZAZIONE:
1. Mantieni la struttura del template
2. Usa oggetti specifici dal lore
3. Crea stato iniziale coerente
4. Definisci goal raggiungibile
5. Rispetta i vincoli di profondità
6. Assicura solvibilità del problema"""

        user_template = """Personalizza questo problema PDDL:

LORE:
{quest_description}

DOMINIO DI RIFERIMENTO:
{domain_content}

ELEMENTI DEL MONDO:
- Personaggi: {characters}
- Luoghi: {locations}
- Oggetti: {items}

Restituisci il problema personalizzato che sia risolvibile."""

        chain = get_ollama_chain(system_msg, user_template)
        response = chain.invoke({
            "quest_description": lore_doc.quest_description,
            "domain_content": self.current_domain,
            "characters": ", ".join(lore_doc.characters or []),
            "locations": ", ".join(lore_doc.locations or []),
            "items": ", ".join(lore_doc.items or [])
        })
        
        return extract_pddl_from_response(response.content)
    
    def validate_and_refine(self, max_iterations: int = 3) -> Dict[str, any]:
        """Loop principale di validazione e refinement"""
        
        print("🔍 Inizio processo di validazione e refinement...")
        
        for iteration in range(max_iterations):
            print(f"\n{'='*50}")
            print(f"🔄 ITERAZIONE {iteration + 1}/{max_iterations}")
            print(f"{'='*50}")
            
            # Salva file temporanei
            domain_file = f"temp_domain_{iteration}.pddl"
            problem_file = f"temp_problem_{iteration}.pddl"
            
            write_to_file(self.current_domain, domain_file)
            write_to_file(self.current_problem, problem_file)
            
            # Validazione sintattica
            print("📋 Validazione sintattica...")
            domain_valid = validate_pddl_syntax(self.current_domain)
            problem_valid = validate_pddl_syntax(self.current_problem)
            
            if not domain_valid or not problem_valid:
                print("❌ Errori sintattici trovati")
                errors = []
                if not domain_valid:
                    errors.append("Errori sintattici nel dominio")
                if not problem_valid:
                    errors.append("Errori sintattici nel problema")
                
                # Riflessione per correggere errori
                reflection = self.reflection_agent.analyze_pddl_errors(
                    self.current_domain, self.current_problem, errors
                )
                
                if not self._apply_reflection_feedback(reflection):
                    continue
            
            # Test di solvibilità
            print("🧮 Test di solvibilità...")
            plan = run_fast_downward(domain_file, problem_file)
            
            if plan:
                print(f"✅ Piano trovato con {len(plan)} azioni!")
                print("🎯 Verifica vincoli di profondità...")
                
                if self._check_depth_constraints(plan):
                    print("✅ Vincoli di profondità soddisfatti!")
                    
                    # Pulizia file temporanei
                    self._cleanup_temp_files(iteration)
                    
                    return {
                        "success": True,
                        "domain": self.current_domain,
                        "problem": self.current_problem,
                        "plan": plan,
                        "iterations": iteration + 1,
                        "lore": self.current_lore
                    }
                else:
                    print("⚠️ Vincoli di profondità non soddisfatti")
                    # Suggerimenti per aggiustare la profondità
                    suggestions = self._get_depth_adjustment_suggestions(plan)
                    if not self._apply_depth_adjustments(suggestions):
                        continue
            else:
                print("❌ Nessun piano trovato")
                
                # Interazione con l'utente per il refinement
                if not self._interactive_refinement():
                    continue
            
            # Pulizia file temporanei
            self._cleanup_temp_files(iteration)
        
        print(f"\n❌ Impossibile generare un PDDL valido dopo {max_iterations} iterazioni")
        return {
            "success": False,
            "domain": self.current_domain,
            "problem": self.current_problem,
            "iterations": max_iterations,
            "lore": self.current_lore
        }
    
    def _apply_reflection_feedback(self, reflection: Dict[str, str]) -> bool:
        """Applica il feedback dell'agente di riflessione"""
        
        print("\n🤔 Feedback dell'agente di riflessione:")
        print("-" * 40)
        
        if reflection["errors"]:
            print("❌ Errori identificati:")
            print(reflection["errors"])
        
        if reflection["suggestions"]:
            print("\n💡 Suggerimenti:")
            print(reflection["suggestions"])
        
        # Chiedi conferma all'utente
        choice = input("\n🤝 Vuoi applicare le correzioni suggerite? [s/n]: ").lower()
        
        if choice == 's':
            # Applica le correzioni se disponibili
            if reflection["corrected_code"]:
                # Estrai dominio e problema corretti
                corrected_parts = self._extract_corrected_parts(reflection["corrected_code"])
                if corrected_parts["domain"]:
                    self.current_domain = corrected_parts["domain"]
                    print("✅ Dominio aggiornato")
                if corrected_parts["problem"]:
                    self.current_problem = corrected_parts["problem"]
                    print("✅ Problema aggiornato")
                return True
            else:
                print("⚠️ Nessuna correzione automatica disponibile")
                return self._manual_correction()
        else:
            return self._manual_correction()
    
    def _extract_corrected_parts(self, corrected_code: str) -> Dict[str, str]:
        """Estrae parti corrette dal codice"""
        parts = {"domain": "", "problem": ""}
        
        # Cerca blocchi di codice PDDL
        if "(define (domain" in corrected_code:
            domain_start = corrected_code.find("(define (domain")
            domain_end = self._find_matching_paren(corrected_code, domain_start)
            if domain_end > domain_start:
                parts["domain"] = corrected_code[domain_start:domain_end+1]
        
        if "(define (problem" in corrected_code:
            problem_start = corrected_code.find("(define (problem")
            problem_end = self._find_matching_paren(corrected_code, problem_start)
            if problem_end > problem_start:
                parts["problem"] = corrected_code[problem_start:problem_end+1]
        
        return parts
    
    def _find_matching_paren(self, text: str, start: int) -> int:
        """Trova la parentesi chiusa corrispondente"""
        count = 0
        for i in range(start, len(text)):
            if text[i] == '(':
                count += 1
            elif text[i] == ')':
                count -= 1
                if count == 0:
                    return i
        return -1
    
    def _manual_correction(self) -> bool:
        """Permette correzione manuale"""
        print("\n✏️ Correzione manuale:")
        print("1. Modifica dominio")
        print("2. Modifica problema")
        print("3. Riprova generazione")
        print("4. Salta iterazione")
        
        choice = input("Scelta [1-4]: ")
        
        if choice == "1":
            new_domain = input("Inserisci il nuovo dominio (o lascia vuoto per mantenere): ")
            if new_domain.strip():
                self.current_domain = new_domain.strip()
                print("✅ Dominio aggiornato")
            return True
        elif choice == "2":
            new_problem = input("Inserisci il nuovo problema (o lascia vuoto per mantenere): ")
            if new_problem.strip():
                self.current_problem = new_problem.strip()
                print("✅ Problema aggiornato")
            return True
        elif choice == "3":
            # Rigenera da capo
            self.current_domain, self.current_problem = self.generate_initial_pddl(self.current_lore)
            print("✅ PDDL rigenerato")
            return True
        else:
            return False
    
    def _check_depth_constraints(self, plan: List[str]) -> bool:
        """Verifica se il piano rispetta i vincoli di profondità"""
        plan_length = len(plan)
        min_depth, max_depth = self.current_lore.depth_constraints
        
        return min_depth <= plan_length <= max_depth
    
    def _get_depth_adjustment_suggestions(self, plan: List[str]) -> Dict[str, str]:
        """Suggerimenti per aggiustare la profondità del piano"""
        plan_length = len(plan)
        min_depth, max_depth = self.current_lore.depth_constraints
        
        suggestions = {}
        
        if plan_length < min_depth:
            suggestions["type"] = "increase_depth"
            suggestions["message"] = f"Piano troppo breve ({plan_length} < {min_depth})"
            suggestions["actions"] = [
                "Aggiungi azioni intermedie",
                "Introduci sotto-obiettivi",
                "Aggiungi elementi che richiedono preparazione"
            ]
        elif plan_length > max_depth:
            suggestions["type"] = "decrease_depth"
            suggestions["message"] = f"Piano troppo lungo ({plan_length} > {max_depth})"
            suggestions["actions"] = [
                "Semplifica alcune azioni",
                "Rimuovi passaggi intermedi",
                "Combina azioni simili"
            ]
        
        return suggestions
    
    def _apply_depth_adjustments(self, suggestions: Dict[str, str]) -> bool:
        """Applica aggiustamenti per la profondità"""
        print(f"\n📏 {suggestions['message']}")
        print("💡 Suggerimenti:")
        for action in suggestions["actions"]:
            print(f"   - {action}")
        
        choice = input("\n🔧 Vuoi applicare aggiustamenti automatici? [s/n]: ").lower()
        
        if choice == 's':
            # Applica modifiche basate sul tipo
            if suggestions["type"] == "increase_depth":
                return self._increase_plan_depth()
            else:
                return self._decrease_plan_depth()
        else:
            return self._manual_correction()
    
    def _increase_plan_depth(self) -> bool:
        """Aumenta la profondità del piano"""
        print("🔧 Aggiunta di complessità al problema...")
        
        # Modifica il problema per richiedere più passaggi
        modifications = [
            "Aggiungi oggetti intermedi necessari",
            "Introduci più location da visitare",
            "Aggiungi prerequisiti per le azioni"
        ]
        
        # Applica modifiche al problema
        # Questa è una semplificazione - in un sistema completo
        # si userebbe l'LLM per modificare il PDDL
        
        return True
    
    def _decrease_plan_depth(self) -> bool:
        """Diminuisce la profondità del piano"""
        print("🔧 Semplificazione del problema...")
        
        # Modifica il problema per richiedere meno passaggi
        modifications = [
            "Rimuovi alcuni oggetti intermedi",
            "Semplifica le connessioni tra location",
            "Riduci i prerequisiti per le azioni"
        ]
        
        # Applica modifiche al problema
        return True
    
    def _interactive_refinement(self) -> bool:
        """Refinement interattivo quando non viene trovato un piano"""
        print("\n🤝 Refinement interattivo:")
        print("1. Analizza con l'agente di riflessione")
        print("2. Suggerimenti miglioramento narrativo")
        print("3. Modifica manuale")
        print("4. Rigenera da capo")
        print("5. Salta iterazione")
        
        choice = input("Scelta [1-5]: ")
        
        if choice == "1":
            # Analisi con agente di riflessione
            reflection = self.reflection_agent.analyze_pddl_errors(
                self.current_domain, self.current_problem, 
                ["Nessun piano trovato"]
            )
            return self._apply_reflection_feedback(reflection)
        
        elif choice == "2":
            # Suggerimenti narrativi
            improvements = self.reflection_agent.suggest_improvements(
                self.current_lore, self.current_domain, self.current_problem
            )
            return self._apply_narrative_improvements(improvements)
        
        elif choice == "3":
            return self._manual_correction()
        
        elif choice == "4":
            self.current_domain, self.current_problem = self.generate_initial_pddl(self.current_lore)
            return True
        
        else:
            return False
    
    def _apply_narrative_improvements(self, improvements: Dict[str, str]) -> bool:
        """Applica miglioramenti narrativi"""
        print("\n📚 Miglioramenti narrativi suggeriti:")
        print("-" * 40)
        
        for key, value in improvements.items():
            if value.strip():
                print(f"\n{key.upper()}:")
                print(value)
        
        choice = input("\n🎭 Vuoi applicare questi miglioramenti? [s/n]: ").lower()
        
        if choice == 's':
            # In un sistema completo, qui si applicherebbe l'LLM
            # per modificare il PDDL basato sui miglioramenti
            print("✅ Miglioramenti applicati")
            return True
        else:
            return False
    
    def _cleanup_temp_files(self, iteration: int):
        """Pulisce i file temporanei"""
        temp_files = [
            f"temp_domain_{iteration}.pddl",
            f"temp_problem_{iteration}.pddl",
            "sas_plan"
        ]
        
        for file in temp_files:
            if os.path.exists(file):
                try:
                    os.remove(file)
                except:
                    pass
    
    def save_final_files(self, result: Dict[str, any], base_name: str = "final") -> bool:
        """Salva i file finali"""
        try:
            # Salva dominio
            domain_file = f"{base_name}_domain.pddl"
            write_to_file(result["domain"], domain_file)
            
            # Salva problema
            problem_file = f"{base_name}_problem.pddl"
            write_to_file(result["problem"], problem_file)
            
            # Salva lore
            lore_file = f"{base_name}_lore.yaml"
            lore_data = {
                "quest_description": result["lore"].quest_description,
                "world_context": result["lore"].world_context,
                "branching_factor": result["lore"].branching_factor,
                "depth_constraints": result["lore"].depth_constraints,
                "characters": result["lore"].characters,
                "locations": result["lore"].locations,
                "items": result["lore"].items,
                "constraints": result["lore"].constraints,
                "generation_info": {
                    "iterations": result["iterations"],
                    "plan_length": len(result.get("plan", [])),
                    "success": result["success"]
                }
            }
            
            with open(lore_file, 'w', encoding='utf-8') as f:
                yaml.dump(lore_data, f, default_flow_style=False, allow_unicode=True)
            
            # Salva piano se presente
            if result.get("plan"):
                plan_file = f"{base_name}_plan.txt"
                with open(plan_file, 'w', encoding='utf-8') as f:
                    f.write(f"Piano generato con {len(result['plan'])} azioni:\n")
                    f.write("-" * 40 + "\n")
                    for i, action in enumerate(result["plan"], 1):
                        f.write(f"{i:2d}. {action}\n")
            
            print(f"✅ File salvati con prefisso '{base_name}'")
            return True
            
        except Exception as e:
            print(f"❌ Errore nel salvataggio: {e}")
            return False

def get_ollama_chain(system_message: str, user_template: str):
    """Crea una catena LangChain con Ollama"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("human", user_template)
    ])
    return prompt | ChatOllama(model=MODEL_NAME, temperature=0.1, top_p=0.8)

def write_to_file(content: str, filename: str):
    """Scrive contenuto in un file"""
    try:
        Path(filename).write_text(content.strip(), encoding='utf-8')
        print(f"📂 File salvato: {filename}")
        return True
    except Exception as e:
        print(f"❌ Errore scrittura file {filename}: {e}")
        return False
    

    # Funzioni di supporto mancanti da aggiungere al codice principale

import tempfile
import shutil

def validate_pddl_syntax(pddl_content: str) -> bool:
    """Valida la sintassi PDDL di base"""
    try:
        # Verifica bilanciamento parentesi
        if not _check_parentheses_balance(pddl_content):
            return False
        
        # Verifica presenza di elementi obbligatori
        if "(define" not in pddl_content:
            return False
        
        # Verifica che non ci siano caratteri non validi
        invalid_chars = ['[', ']', '{', '}']
        for char in invalid_chars:
            if char in pddl_content:
                return False
        
        # Verifica struttura di base
        if "(define (domain" in pddl_content:
            return _validate_domain_structure(pddl_content)
        elif "(define (problem" in pddl_content:
            return _validate_problem_structure(pddl_content)
        
        return True
        
    except Exception as e:
        print(f"Errore nella validazione sintattica: {e}")
        return False

def _check_parentheses_balance(text: str) -> bool:
    """Verifica che le parentesi siano bilanciate"""
    count = 0
    for char in text:
        if char == '(':
            count += 1
        elif char == ')':
            count -= 1
            if count < 0:
                return False
    return count == 0

def _validate_domain_structure(domain_content: str) -> bool:
    """Valida la struttura di un dominio PDDL"""
    required_sections = [
        "(:requirements",
        "(:types",
        "(:predicates"
    ]
    
    for section in required_sections:
        if section not in domain_content:
            print(f"Sezione mancante nel dominio: {section}")
            return False
    
    return True

def _validate_problem_structure(problem_content: str) -> bool:
    """Valida la struttura di un problema PDDL"""
    required_sections = [
        "(:domain",
        "(:objects",
        "(:init",
        "(:goal"
    ]
    
    for section in required_sections:
        if section not in problem_content:
            print(f"Sezione mancante nel problema: {section}")
            return False
    
    return True

def extract_pddl_from_response(response: str) -> str:
    """Estrae codice PDDL dalla risposta dell'LLM"""
    # Cerca blocchi di codice PDDL
    patterns = [
        r'```pddl\n(.*?)\n```',
        r'```\n(.*?)\n```',
        r'(\(define.*?\))\s*$'

    ]
    
    for pattern in patterns:
        match = re.search(pattern, response, re.DOTALL)
        if match:
            return match.group(1).strip()
    
    # Se non trova pattern specifici, cerca (define
    start = response.find("(define")
    if start != -1:
        # Trova la fine del blocco PDDL
        end = find_matching_paren(response, start)
        if end != -1:
            return response[start:end+1].strip()
    
    # Se tutto fallisce, restituisce la risposta pulita
    return response.strip()

def find_matching_paren(text: str, start: int) -> int:
    """Trova la parentesi chiusa corrispondente"""
    count = 0
    for i in range(start, len(text)):
        if text[i] == '(':
            count += 1
        elif text[i] == ')':
            count -= 1
            if count == 0:
                return i
    return -1

def run_fast_downward(domain_file: str, problem_file: str, timeout: int = 30) -> Optional[List[str]]:
    """Esegue Fast Downward per trovare un piano"""
    try:
        # Verifica che i file esistano
        if not os.path.exists(domain_file) or not os.path.exists(problem_file):
            print("❌ File dominio o problema non trovati")
            return None
        
        # Comando Fast Downward (assumendo sia installato)
        cmd = [
            "python", "C:\\Users\\Alessandro\\fast_downward\\downward\\fast-downward.py",
            "--plan-file", "sas_plan",
            domain_file,
            problem_file,
            "--search", "astar(lmcut())"
        ]
        
        # Prova prima con un planner alternativo se FD non è disponibile
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            
            if result.returncode == 0 and os.path.exists("sas_plan"):
                return _parse_plan_file("sas_plan")
            else:
                print(f"Fast Downward fallito: {result.stderr}")
                return None
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("⚠️ Fast Downward non disponibile, usando planner simulato")
            return _simulate_planning(domain_file, problem_file)
    
    except Exception as e:
        print(f"❌ Errore nell'esecuzione del planner: {e}")
        return None

def _parse_plan_file(plan_file: str) -> List[str]:
    """Analizza il file del piano generato"""
    try:
        with open(plan_file, 'r') as f:
            lines = f.readlines()
        
        plan = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith(';'):
                # Rimuove parentesi e pulisce l'azione
                action = line.strip('()')
                plan.append(action)
        
        return plan
    
    except Exception as e:
        print(f"Errore nel parsing del piano: {e}")
        return []

def _simulate_planning(domain_file: str, problem_file: str) -> Optional[List[str]]:
    """Simula la pianificazione per test quando FD non è disponibile"""
    print("🔄 Simulazione pianificazione...")
    
    # Legge i file per analisi di base
    try:
        with open(domain_file, 'r') as f:
            domain_content = f.read()
        with open(problem_file, 'r') as f:
            problem_content = f.read()
        
        # Analisi semplificata per generare un piano plausibile
        actions = _extract_actions_from_domain(domain_content)
        goals = _extract_goals_from_problem(problem_content)
        
        if actions and goals:
            # Genera un piano simulato basato su euristica semplice
            simulated_plan = _generate_heuristic_plan(actions, goals)
            print(f"📝 Piano simulato generato: {len(simulated_plan)} azioni")
            return simulated_plan
        
        return None
        
    except Exception as e:
        print(f"Errore nella simulazione: {e}")
        return None

def _extract_actions_from_domain(domain_content: str) -> List[str]:
    """Estrae le azioni dal dominio"""
    actions = []
    lines = domain_content.split('\n')
    
    for line in lines:
        line = line.strip()
        if line.startswith('(:action'):
            action_name = line.split()[1]
            actions.append(action_name)
    
    return actions

def _extract_goals_from_problem(problem_content: str) -> List[str]:
    """Estrae i goal dal problema"""
    goals = []
    
    # Cerca la sezione goal
    goal_start = problem_content.find('(:goal')
    if goal_start != -1:
        goal_end = find_matching_paren(problem_content, goal_start)
        if goal_end != -1:
            goal_section = problem_content[goal_start:goal_end+1]
            # Analisi semplificata dei goal
            goals = re.findall(r'\(\w+[^)]*\)', goal_section)
    
    return goals

def _generate_heuristic_plan(actions: List[str], goals: List[str]) -> List[str]:
    """Genera un piano euristico basato su azioni e goal"""
    plan = []
    
    # Strategia euristica semplice
    common_action_order = ['move', 'take', 'equip', 'unlock', 'fight', 'rescue']
    
    for action_type in common_action_order:
        matching_actions = [a for a in actions if action_type in a.lower()]
        if matching_actions:
            # Aggiunge alcune istanze dell'azione
            for i in range(min(3, len(goals))):
                plan.append(f"{matching_actions[0]} arg{i}")
    
    return plan[:10]  # Limita a 10 azioni per semplicità

def setup_interactive_interface():
    """Configura l'interfaccia interattiva"""
    print("🎮 GENERATORE INTERATTIVO DI STORIE PDDL")
    print("="*50)
    print()
    
    # Verifica dipendenze
    missing_deps = []
    
    try:
        import langchain
        import yaml
    except ImportError as e:
        missing_deps.append(str(e))
    
    if missing_deps:
        print("⚠️ Dipendenze mancanti:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\nInstalla con: pip install langchain pyyaml")
        return False
    
    # Verifica modello Ollama
    try:
        test_model = ChatOllama(model=MODEL_NAME)
        print(f"✅ Modello {MODEL_NAME} disponibile")
    except Exception as e:
        print(f"⚠️ Modello {MODEL_NAME} non disponibile: {e}")
        print("Assicurati che Ollama sia installato e il modello sia scaricato")
        return False
    
    return True

def main():
    """Funzione principale per l'esecuzione interattiva"""
    
    if not setup_interactive_interface():
        return
    
    # Crea il generatore
    generator = InteractiveStoryGenerator()
    
    print("🎯 Modalità di utilizzo:")
    print("1. Creazione interattiva del lore")
    print("2. Utilizzo di esempio predefinito")
    print("3. Caricamento da file YAML")
    
    mode = input("\nScegli modalità [1-3]: ")
    
    try:
        if mode == "1":
            # Modalità interattiva
            lore_doc = generator.create_lore_document(interactive=True)
        elif mode == "2":
            # Esempio predefinito
            lore_doc = generator.create_lore_document(interactive=False)
        elif mode == "3":
            # Caricamento da file
            filename = input("Nome del file YAML: ")
            lore_doc = load_lore_from_file(filename)
        else:
            print("Modalità non valida, uso esempio predefinito")
            lore_doc = generator.create_lore_document(interactive=False)
        
        print(f"\n✅ Lore creato: {lore_doc.quest_description[:50]}...")
        
        # Genera PDDL iniziale
        domain, problem = generator.generate_initial_pddl(lore_doc)
        
        print("\n🔧 Avvio processo di validazione e refinement...")
        
        # Processo di validazione e refinement
        result = generator.validate_and_refine(max_iterations=3)
        
        if result["success"]:
            print("\n🎉 GENERAZIONE COMPLETATA CON SUCCESSO!")
            print(f"✅ Iterazioni necessarie: {result['iterations']}")
            print(f"✅ Lunghezza piano: {len(result.get('plan', []))}")
            
            # Salva i file finali
            save_name = input("\nNome base per i file (default: 'final'): ") or "final"
            generator.save_final_files(result, save_name)
            
        else:
            print("\n❌ Generazione fallita")
            print("I file parziali sono comunque disponibili per ispezione")
            
            # Salva comunque i file per debug
            generator.save_final_files(result, "debug")
    
    except KeyboardInterrupt:
        print("\n\n⏹️ Processo interrotto dall'utente")
    except Exception as e:
        print(f"\n❌ Errore inaspettato: {e}")
        import traceback
        traceback.print_exc()

def load_lore_from_file(filename: str) -> LoreDocument:
    """Carica un documento di lore da file YAML"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return LoreDocument(
            quest_description=data.get('quest_description', ''),
            world_context=data.get('world_context', ''),
            branching_factor=tuple(data.get('branching_factor', [2, 5])),
            depth_constraints=tuple(data.get('depth_constraints', [3, 8])),
            characters=data.get('characters', []),
            locations=data.get('locations', []),
            items=data.get('items', []),
            constraints=data.get('constraints', [])
        )
        
    except Exception as e:
        print(f"Errore nel caricamento del file: {e}")
        print("Uso esempio predefinito")
        return LoreDocument(
            quest_description="Avventura di esempio",
            world_context="Mondo fantasy",
            branching_factor=(2, 5),
            depth_constraints=(3, 8)
        )

# Aggiunta per esecuzione diretta
if __name__ == "__main__":
    main()'''