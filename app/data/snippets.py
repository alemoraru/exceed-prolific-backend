import os
from typing import Dict

SNIPPET_FILES = {
    "0": "snippetA.py",
    "1": "snippetB.py",
    "2": "snippetC.py",
    "3": "snippetD.py",
}

ERRORS = {
    "0": '''Traceback (most recent call last):\n  File "main.py", line 17, in <module>\n    build_list(10)\n  File "main.py", line 11, in build_list\n    result = result.append(i)\n             ^^^^^^^^^^^^^\nAttributeError: 'NoneType' object has no attribute 'append\'''',
    "1": '''Traceback (most recent call last):\n  File "main.py", line 6, in top_three\n    return sorted_items[:3]\nTypeError: 'NoneType' object is not subscriptable''',
    "2": '''Traceback (most recent call last):\n  File "main.py", line 5, in get_third_element\n    return lst[2]\nIndexError: list index out of range''',
    "3": '''Traceback (most recent call last):\n  File "main.py", line 6, in parse_numbers\n    return [int(x) for x in data.split(',')]\nAttributeError: 'list' object has no attribute 'split''',
}


def read_snippet(filename: str) -> str:
    """Read a code snippet from a file."""
    path = os.path.join(os.path.dirname(__file__), "code", filename)
    with open(path, "r") as f:
        return f.read()


SNIPPETS: Dict[str, dict] = {
    key: {
        "code": read_snippet(filename),
        "error": ERRORS[key],
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
