# online_llm_client.py
import requests
import time
from llm_interface import LLMInterface
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("TOGETHER_API_KEY")

class OnlineLLMClient(LLMInterface):
    def __init__(self, model: str = "deepseek-ai/DeepSeek-R1", api_key: str = ""):
        self.api_url = "https://api.together.xyz/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.model = model

    def run_prompt(self, prompt: str) -> str:
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "Sei un assistente esperto in PDDL."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1024,
            "temperature": 0.7
        }

        for attempt in range(3):
            response = requests.post(self.api_url, json=body, headers=self.headers)
            if response.status_code == 429:
                wait = 2 ** attempt
                print(f"⚠️ Rate limit. Riprovo tra {wait}s...")
                time.sleep(wait)
                continue

            try:
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"].strip()
            except Exception as e:
                print(f"❌ Errore nella risposta LLM: {e}")
                print("👉 Risposta server:", response.text)
                raise

        raise RuntimeError("❌ Troppi tentativi falliti.")
