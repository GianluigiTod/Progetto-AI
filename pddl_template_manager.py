from typing import Dict, List


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
