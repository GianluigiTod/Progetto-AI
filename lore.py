from pydantic import BaseModel, Field, validator
from typing import List, Tuple, Optional
import yaml
import os

class LoreDocument(BaseModel):
    quest_description: str
    branching_factor: Tuple[int, int]
    depth_constraints: Tuple[int, int]
    world_context: Optional[str] = ""
    characters: List[str] = Field(default_factory=list)
    locations: List[str] = Field(default_factory=list)
    items: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)

    @validator("branching_factor", "depth_constraints")
    def check_tuple_length(cls, v):
        if len(v) != 2:
            raise ValueError("I vincoli devono avere esattamente due elementi (min, max)")
        return v

    def to_yaml(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(self.dict(), f, allow_unicode=True)

    @staticmethod
    def from_yaml(path: str) -> 'LoreDocument':
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return LoreDocument(**data)
