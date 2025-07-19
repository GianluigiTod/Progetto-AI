# llm_interface.py
from abc import ABC, abstractmethod

class LLMInterface(ABC):
    @abstractmethod
    def run_prompt(self, prompt: str) -> str:
        pass

