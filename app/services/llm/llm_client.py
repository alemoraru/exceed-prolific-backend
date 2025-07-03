import httpx
from openai import OpenAI
from typing import Dict, Any, Iterator

from app.core.config import OPENAI_API_KEY

# Constants for model types
SUPPORTED_MODELS = {
    "gpt-4o": "openai",
    "llama3.2:3b": "ollama"
}


class BaseModelClient:
    """
    Base class for LLM clients that can generate intervention messages.
    """

    def complete(self, prompt: str) -> str:
        """Generate a completion based on the provided prompt."""
        raise NotImplementedError("This method should be implemented by subclasses.")


class OpenAIClient(BaseModelClient):
    """
    OpenAI client for generating intervention messages.
    """

    def __init__(self, model: str = "gpt-4o"):
        self.model = model
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def complete(self, prompt: str) -> str:
        """
        Call the OpenAI API to generate a completion based on the provided prompt.
        """
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI assistant helping a Python programmer fix a code error"},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content


class OllamaClient(BaseModelClient):
    """
    Ollama client for generating intervention messages.
    See: https://github.com/ollama/ollama/blob/main/docs/api.md
    """

    def __init__(self, model: str = "llama:3.2:3b", temperature: float = 0.7):
        self.model = model
        self.temperature = temperature
        self.base_url = "http://localhost:11434"
        self._client = httpx.Client(timeout=120)

    def complete(self, prompt: str) -> str:
        payload: Dict[str, Any] = {
            "model": self.model,
            "temperature": self.temperature,
            "prompt": prompt,
            "stream": False,
        }
        url = "http://localhost:11434/api/generate"
        response = self._client.post(url, json=payload)
        response.raise_for_status()
        return response.json()["response"]

    def _stream(self, url: str, payload: dict) -> Iterator[str]:
        """Stream responses from the Ollama API."""
        with self._client.stream("POST", url, json=payload) as r:
            for chunk in r.iter_lines():
                if not chunk:
                    continue
                yield httpx.decode_json(chunk)["response"]


class ModelFactory:
    """
    Factory class to create LLM clients based on the model type.
    """

    @staticmethod
    def create_client(model_name: str) -> BaseModelClient:
        client_type = SUPPORTED_MODELS.get(model_name)
        if client_type == "openai":
            return OpenAIClient(model=model_name)
        elif client_type == "ollama":
            return OllamaClient(model=model_name)
        else:
            raise ValueError(f"Unsupported model type: {model_name}")
