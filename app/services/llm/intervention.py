from app.core.config import OLLAMA_MODEL
from app.services.llm.llm_client import ModelFactory
from app.utils.prompt_templates import CONTINGENT_PROMPT, PRAGMATIC_PROMPT


def prepend_line_numbers(code_snippet: str) -> str:
    """
    Prepend each line of the code snippet with its line number, starting from 1.
    """
    lines = code_snippet.splitlines()
    return "\n".join(f"{i+1} {line}" for i, line in enumerate(lines))


def get_rephrased_error_message(
    code_snippet: str, error_msg: str, intervention_type: str
) -> str:
    """
    Generate a rephrased error message based on the intervention type.
    :param code_snippet: The original code snippet that caused the error.
    :param error_msg: The original error message to be rephrased.
    :param intervention_type: The type of intervention, either "pragmatic" or "contingent".
    :return: The rephrased error message.
    :raises ValueError: If the intervention type is invalid.
    """
    if intervention_type == "pragmatic":
        code_snippet_numbered = prepend_line_numbers(code_snippet)
        prompt = PRAGMATIC_PROMPT["template"].format(
            code=code_snippet_numbered, error=error_msg
        )
        system_prompt = PRAGMATIC_PROMPT["system_prompt"]
    elif intervention_type == "contingent":
        code_snippet_numbered = prepend_line_numbers(code_snippet)
        prompt = CONTINGENT_PROMPT["template"].format(
            code=code_snippet_numbered, error=error_msg
        )
        system_prompt = CONTINGENT_PROMPT["system_prompt"]
    else:
        raise ValueError(
            "Invalid intervention type. Must be 'pragmatic' or 'contingent'."
        )

    # Get the LLM client
    llm_client = ModelFactory.create_client(OLLAMA_MODEL)

    # Call the LLM to get the rephrased error message
    llm_response = llm_client.complete(prompt, system_prompt=system_prompt)

    return llm_response
