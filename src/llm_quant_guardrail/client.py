import os
from typing import List, Dict
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)


class LLMClient:
    """
    Thin wrapper around the OpenAI client.
    """

    def __init__(self, model: str | None = None) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set in environment or .env")

        self.client = OpenAI(api_key=api_key)
        self.model = model or os.getenv("LLM_MODEL", "gpt-4.1")

    def chat(self, system: str, messages: List[Dict[str, str]]) -> str:
        """
        Call the chat completion API and return the assistant's text.
        `messages` should NOT include the system message; pass that separately.
        """
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system}] + messages,
        )
        return resp.choices[0].message.content
