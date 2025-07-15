import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
from types import ModuleType
from typing import Tuple

from app.services.llm.intervention import get_rephrased_error_message


def evaluate_code(
        code: str, snippet_id: str, intervention_type: str
) -> Tuple[str, str]:
    """
    1) Syntax‐check the code.
    2) Copy user code and test suite to temp dir.
    3) Run only the relevant unittest class for the snippet.
    4) If errors are encountered, rephrase the error message using an LLM.
    5) Return ("success", "") or ("syntax_error"/"test_failure", details).
    """
    snippet_map = {
        "0": ("snippetA/snippetA.py", "snippetA/test_snippetA.py", "TestSnippetA"),
        "1": ("snippetB/snippetB.py", "snippetB/test_snippetB.py", "TestSnippetB"),
        "2": ("snippetC/snippetC.py", "snippetC/test_snippetC.py", "TestSnippetC"),
        "3": ("snippetD/snippetD.py", "snippetD/test_snippetD.py", "TestSnippetD"),
    }
    if snippet_id not in snippet_map:
        return "no_tests", f"No test suite defined for {snippet_id}"
    snippet_file, test_file, test_class = snippet_map[snippet_id]
    code_dir = os.path.join(os.path.dirname(__file__), "../../data/code")

    with tempfile.TemporaryDirectory() as td:
        # Write user code to temp dir (overwriting the reference snippet file)
        user_code_path = os.path.join(td, os.path.basename(snippet_file))
        with open(user_code_path, "w") as f:
            f.write(code)
        # Copy all other snippet files (from their folders)
        for folder in ["snippetA", "snippetB", "snippetC", "snippetD"]:
            src = os.path.join(code_dir, folder, f"{folder}.py")
            dst = os.path.join(td, f"{folder}.py")
            if src != os.path.join(code_dir, snippet_file):
                shutil.copyfile(src, dst)

        # Copy only the relevant test file from its snippet folder
        test_src = os.path.join(code_dir, test_file)
        test_dst = os.path.join(td, os.path.basename(test_file))
        shutil.copyfile(test_src, test_dst)

        # Syntax check user code
        try:
            subprocess.check_output(
                [sys.executable, "-m", "py_compile", user_code_path],
                stderr=subprocess.STDOUT,
            )
        except subprocess.CalledProcessError as e:
            orig_code, orig_error = _load_original_code_and_error(
                code_dir, snippet_file
            )
            llm_msg = get_rephrased_error_message(
                orig_code, orig_error, intervention_type
            )
            return "syntax_error", llm_msg

        # Run only the relevant test class in the relevant test file
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "unittest",
                    f"{os.path.splitext(os.path.basename(test_file))[0]}.{test_class}",
                ],
                cwd=td,
                capture_output=True,
                text=True,
                timeout=10,
            )
        except Exception as e:
            orig_code, orig_error = _load_original_code_and_error(
                code_dir, snippet_file
            )
            llm_msg = get_rephrased_error_message(
                orig_code, orig_error, intervention_type
            )
            return "runtime_error", llm_msg
        if result.returncode == 0:
            return "success", ""
        else:
            orig_code, orig_error = _load_original_code_and_error(
                code_dir, snippet_file
            )
            llm_msg = get_rephrased_error_message(
                orig_code, orig_error, intervention_type
            )
            return "test_failure", llm_msg


def _load_module(path: str, module_name: str) -> ModuleType:
    """Dynamically load a Python file as a module."""
    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)  # type: ignore
    return mod


def _load_original_code_and_error(code_dir, snippet_file) -> Tuple[str, str]:
    """
    Load the original code and error message for a given snippet file.
    :param code_dir: the directory containing the code snippets.
    :param snippet_file: the relative path to the snippet file.
    :return: Tuple containing the original code and error message.
    """
    orig_code_path = os.path.join(code_dir, snippet_file)
    orig_error_path = os.path.join(
        code_dir,
        os.path.dirname(snippet_file),
        f"{os.path.splitext(os.path.basename(snippet_file))[0]}_error.txt",
    )
    with open(orig_code_path, "r") as f:
        orig_code = f.read()
    with open(orig_error_path, "r") as f:
        orig_error = f.read()
    return orig_code, orig_error
