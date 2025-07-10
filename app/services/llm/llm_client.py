from typing import Any, Dict, Iterator

import httpx
from openai import OpenAI

from app.core.config import OLLAMA_URL, OPENAI_API_KEY
from app.utils.enums import ModelType

# Constants for model types
SUPPORTED_MODELS = {
    ModelType.OPENAI_GPT_4O.value: "openai",
    ModelType.OLLAMA_LLAMA3_2_3B.value: "ollama",
    ModelType.OLLAMA_LLAMA3_8B.value: "ollama",
    ModelType.OLLAMA_CODELLAMA_7B.value: "ollama",
    ModelType.OLLAMA_CODELLAMA_13B.value: "ollama",
    ModelType.OLLAMA_MISTRAL_7B.value: "ollama",
    ModelType.OLLAMA_CODESTRAL_22B.value: "ollama",
    ModelType.OLLAMA_DEEPSEEK_R1_14B.value: "ollama",
    ModelType.OLLAMA_QWEN3_14B.value: "ollama",
    ModelType.OLLAMA_QWEN2_5_CODER_3_B.value: "ollama",
    ModelType.OLLAMA_QWEN2_5_CODER_7_B.value: "ollama",
    ModelType.OLLAMA_QWEN2_5_CODER_14_B.value: "ollama",
}


class BaseModelClient:
    """
    Base class for LLM clients that can generate intervention messages.
    """

    def complete(self, prompt: str, system_prompt: str = None) -> str:
        """Generate a completion based on the provided prompt."""
        raise NotImplementedError("This method should be implemented by subclasses.")


class OpenAIClient(BaseModelClient):
    """
    OpenAI client for generating intervention messages.
    """

    def __init__(self, model: str = "gpt-4o"):
        self.model = model
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def complete(self, prompt: str, system_prompt: str = None) -> str:
        """
        Call the OpenAI API to generate a completion based on the provided prompt.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        system_prompt
                        if system_prompt
                        else "You are an AI assistant helping a Python programmer understand a code error"
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content


class OllamaClient(BaseModelClient):
    """
    Ollama client for generating intervention messages.
    See: https://github.com/ollama/ollama/blob/main/docs/api.md
    """

    def __init__(self, model: str = "llama:3.2:3b", temperature: float = 0.2):
        self.model = model
        self.temperature = temperature
        self.base_url = OLLAMA_URL
        self._client = httpx.Client(timeout=120)

    def complete(self, prompt: str, system_prompt: str = None) -> str:
        payload: Dict[str, Any] = {
            "model": self.model,
            "temperature": self.temperature,
            "prompt": prompt,
            "stream": False,
        }
        # Include system prompt if provided
        if system_prompt:
            payload["system"] = system_prompt

        url = f"{self.base_url}/api/generate"
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
