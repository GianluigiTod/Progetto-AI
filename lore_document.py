from dataclasses import dataclass
from typing import List, Tuple


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