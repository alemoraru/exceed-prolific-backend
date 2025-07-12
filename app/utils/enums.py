from enum import Enum


class InterventionType(Enum):
    """Enum for intervention types."""

    PRAGMATIC = "pragmatic"
    CONTINGENT = "contingent"


class ModelType(Enum):
    """Enum for model names."""

    OPENAI_GPT_4O = "gpt-4o"
    OLLAMA_LLAMA3_2_3B = "llama3.2:3b"
    OLLAMA_LLAMA3_1_8B = "llama3.1:8b"
    OLLAMA_CODELLAMA_7B = "codellama:7b"
    OLLAMA_CODELLAMA_13B = "codellama:13b"
    OLLAMA_MISTRAL_7B = "mistral:7b"
    OLLAMA_CODESTRAL_22B = "codestral:22b"
    OLLAMA_DEEPSEEK_R1_14B = "deepseek-r1:14b"
    OLLAMA_QWEN3_14B = "qwen3:14b"
    OLLAMA_QWEN2_5_CODER_3_B = "qwen2.5-coder:3b"
    OLLAMA_QWEN2_5_CODER_7_B = "qwen2.5-coder:7b"
    OLLAMA_QWEN2_5_CODER_14_B = "qwen2.5-coder:14b"
