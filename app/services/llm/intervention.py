from app.utils.prompt_templates import PRAGMATIC_PROMPT_TEMPLATE, CONTINGENT_PROMPT_TEMPLATE
from app.services.llm.llm_client import ModelFactory


def get_rephrased_error_message(code_snippet: str, error_msg: str, intervention_type: str) -> str:
    """
    Generate a rephrased error message based on the intervention type.
    """
    if intervention_type == "pragmatic":
        prompt = PRAGMATIC_PROMPT_TEMPLATE.format(code=code_snippet, error=error_msg)
    elif intervention_type == "contingent":
        prompt = CONTINGENT_PROMPT_TEMPLATE.format(code=code_snippet, error=error_msg)
    else:
        raise ValueError("Invalid intervention type. Must be 'pragmatic' or 'contingent'.")

    # Get the LLM client
    llm_client = ModelFactory.create_client("llama3.2:3b")

    # Call the LLM to get the rephrased error message
    response = llm_client.complete(prompt)

    return response
