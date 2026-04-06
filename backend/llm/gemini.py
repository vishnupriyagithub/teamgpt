# llm/gemini.py
import os
from google import genai
from google.genai.errors import ClientError
from llm.base import LLMProvider

MODEL_NAME = "gemini-3-flash-preview"

class GeminiLLM(LLMProvider):
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not set")

        self.client = genai.Client(api_key=api_key)

    def generate(self, prompt: str) -> str:
        try:
            response = self.client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
            )

            if not response or not getattr(response, "text", None):
                return "I don't know."

            return response.text.strip()

        except ClientError as e:
            if "RESOURCE_EXHAUSTED" in str(e):
                raise RuntimeError(
                    "⚠️ AI quota temporarily exceeded. Please try again in a few seconds."
                )
            raise RuntimeError("⚠️ AI service error.")

        except Exception as e:
            raise RuntimeError(f"LLM generation error: {str(e)}")
