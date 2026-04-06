# llm/local.py
import requests
from llm.base import LLMProvider

class LocalLLM(LLMProvider):
    def __init__(self):
        self.url = "http://localhost:1234/v1/completions"
        self.model_name = "phi-3-mini-4k-instruct"

    def generate(self, prompt: str) -> str:
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "max_tokens": 256,
            "temperature": 0.2,

        }
        try:
            r = requests.post(self.url, json=payload, timeout=180)
            r.raise_for_status()
        

            data = r.json()
            if not data.get("choices"):
                raise RuntimeError("Local LLM return no choices")
            text = data["choices"][0].get("text", "").strip()
            if not text:
                raise RuntimeError("Local LLM returned empty text")
            return text
        except requests.Timeout:
            raise RuntimeError("Local LLM request timed out")
        except requests.ConnectionError:
            raise RuntimeError("Local LLM connection error")
        
        except Exception as e:
            raise RuntimeError(f"Local LLM generation error: {str(e)}")
