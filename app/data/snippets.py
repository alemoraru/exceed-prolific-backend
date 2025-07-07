import os
from typing import Dict

SNIPPET_FILES = {
    "0": "snippetA.py",
    "1": "snippetB.py",
    "2": "snippetC.py",
    "3": "snippetD.py",
}


def read_snippet(filename: str) -> str:
    """Read a code snippet from a file."""
    path = os.path.join(os.path.dirname(__file__), "code", filename)
    with open(path, "r") as f:
        return f.read()


def read_error(snippet_key: str) -> str:
    error_file = f"{SNIPPET_FILES[snippet_key].replace('.py', '_error.txt')}"
    error_path = os.path.join(os.path.dirname(__file__), 'code', error_file)
    with open(error_path, 'r') as f:
        return f.read()


SNIPPETS: Dict[str, dict] = {
    key: {
        "code": read_snippet(filename),
        "error": read_error(key),
        "filename": filename,
    }
    for key, filename in SNIPPET_FILES.items()
}


def get_snippet(snippet_id: str) -> dict | None:
    """
    Retrieve a code snippet by its associated ID.
    :param snippet_id: The ID of the snippet to retrieve.
    :return: A dictionary containing the code, error message, and filename, or None if not found.
    """
    return SNIPPETS.get(snippet_id)
