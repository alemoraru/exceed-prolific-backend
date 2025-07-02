import openai
from app.core.config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

PROMPTS = {
    "pragmatic": "You’re trying to {intent}—try {fix}.",
    "contingent": "Did you mean to {intent}? This often happens when {explanation}."
}


def get_intervention_message(code: str, error_msg: str, intervention_type: str) -> str:
    prompt = f"Given this code:\n{code}\nError:\n{error_msg}\nGenerate a {intervention_type} error message."
    resp = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=100
    )
    return resp.choices[0].text.strip()
