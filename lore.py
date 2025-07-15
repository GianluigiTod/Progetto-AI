# lore.py
from dataclasses import dataclass, asdict
from typing import List, Tuple
import yaml
import os

@dataclass
class LoreDocument:
    quest_description: str
    branching_factor: Tuple[int, int]
    depth_constraints: Tuple[int, int]
    world_context: str = ""
    characters: List[str] = None
    locations: List[str] = None
    items: List[str] = None
    constraints: List[str] = None

    def to_yaml(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(asdict(self), f, allow_unicode=True)

    @staticmethod
    def from_yaml(path: str) -> 'LoreDocument':
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return LoreDocument(**data)
