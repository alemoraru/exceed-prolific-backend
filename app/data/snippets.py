import os
from typing import Dict, Tuple

SNIPPET_FILES = {
    "A": ("snippetA/snippetA.py", "snippetA/snippetA_error.txt"),
    "B": ("snippetB/snippetB.py", "snippetB/snippetB_error.txt"),
    "C": ("snippetC/snippetC.py", "snippetC/snippetC_error.txt"),
    "D": ("snippetD/snippetD.py", "snippetD/snippetD_error.txt"),
}


def read_snippet(filename: Tuple[str, str]) -> str:
    """
    Read a code snippet from a file.
    :param filename: A tuple containing the directory and filename of the snippet.
    :return: The content of the code snippet as a string.
    :raises FileNotFoundError: If the snippet file does not exist.
    :raises ValueError: If the filename is invalid.
    """
    path = os.path.join(os.path.dirname(__file__), "code", filename[0])
    with open(path, "r") as f:
        return f.read()


def read_error(snippet_key: str) -> str:
    """
    Read the error message from a file for a given snippet.
    :param snippet_key: The key identifying the snippet (e.g., "A", "B", etc.).
    :return: The content of the error message as a string.
    :raises FileNotFoundError: If the error file does not exist.
    :raises ValueError: If the snippet key is invalid.
    """
    code_file, error_file = SNIPPET_FILES[snippet_key]
    error_path = os.path.join(os.path.dirname(__file__), "code", error_file)
    with open(error_path, "r") as f:
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
