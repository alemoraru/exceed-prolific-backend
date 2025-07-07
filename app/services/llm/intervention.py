from app.utils.enums import ModelType
from app.utils.prompt_templates import PRAGMATIC_PROMPT, CONTINGENT_PROMPT
from app.services.llm.llm_client import ModelFactory


def get_rephrased_error_message(code_snippet: str, error_msg: str, intervention_type: str) -> str:
    """
    Generate a rephrased error message based on the intervention type.
    """
    if intervention_type == "pragmatic":
        prompt = PRAGMATIC_PROMPT["template"].format(code=code_snippet, error=error_msg)
        system_prompt = PRAGMATIC_PROMPT["system_prompt"]
    elif intervention_type == "contingent":
        prompt = CONTINGENT_PROMPT["template"].format(code=code_snippet, error=error_msg)
        system_prompt = CONTINGENT_PROMPT["system_prompt"]
    else:
        raise ValueError("Invalid intervention type. Must be 'pragmatic' or 'contingent'.")

    # Get the LLM client
    llm_client = ModelFactory.create_client(ModelType.OLLAMA_QWEN2_5_CODER_3_B.value)

    # Call the LLM to get the rephrased error message
    response = llm_client.complete(prompt, system_prompt=system_prompt)

    return response
