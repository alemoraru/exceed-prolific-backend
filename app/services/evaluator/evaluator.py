import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile
from types import ModuleType
from typing import Optional, Tuple

from app.services.llm.intervention import get_rephrased_error_message


def evaluate_code(
    code: str, snippet_id: str, intervention_type: str
) -> Tuple[str, str, Optional[int], Optional[int]]:
    """
    Evaluate user code against a predefined snippet and its test suite.
    This function performs the following steps:

    1) Syntax‐check the code.
    2) Copy user code and test suite to temp dir.
    3) Run only the relevant unittest class for the snippet.
    4) If errors are encountered, rephrase the error message using an LLM.
    5) Return the evaluation status, rephrased error message, and test results.

    :param code: The user code to evaluate.
    :param snippet_id: The ID of the snippet to evaluate against.
    :param intervention_type: The type of intervention to apply for error rephrasing.
    :return: A tuple containing:
        - status: "success", "syntax_error", "test_failure", or "runtime_error"
        - rephrased error message (if applicable)
        - number of tests passed (if applicable)
        - total number of tests (if applicable)
    """
    snippet_map = {
        "0": ("snippetA/snippetA.py", "snippetA/test_snippetA.py", "TestSnippetA"),
        "1": ("snippetB/snippetB.py", "snippetB/test_snippetB.py", "TestSnippetB"),
        "2": ("snippetC/snippetC.py", "snippetC/test_snippetC.py", "TestSnippetC"),
        "3": ("snippetD/snippetD.py", "snippetD/test_snippetD.py", "TestSnippetD"),
    }
    if snippet_id not in snippet_map:
        return "not_found", f"No test suite defined for {snippet_id}", None, None
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
            return "syntax_error", llm_msg, None, None

        # Run only the relevant test class in the relevant test file
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "unittest",
                    f"{os.path.splitext(os.path.basename(test_file))[0]}.{test_class}",
                    "-v",
                ],
                cwd=td,
                capture_output=True,
                text=True,
                timeout=10,
            )
        except Exception:
            orig_code, orig_error = _load_original_code_and_error(
                code_dir, snippet_file
            )
            llm_msg = get_rephrased_error_message(
                orig_code, orig_error, intervention_type
            )
            return "runtime_error", llm_msg, None, None
        if result.returncode == 0:
            # Parse output for test count
            passed, total = _parse_unittest_output(result.stdout)
            return "success", "", passed, total
        else:
            passed, total = _parse_unittest_output(result.stdout)
            orig_code, orig_error = _load_original_code_and_error(
                code_dir, snippet_file
            )
            llm_msg = get_rephrased_error_message(
                orig_code, orig_error, intervention_type
            )
            return "test_failure", llm_msg, passed, total


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


def _parse_unittest_output(output: str) -> Tuple[Optional[int], Optional[int]]:
    """
    Parse unittest output to extract number of passed and total tests.
    :param output: The output string from unittest.
    :return: A tuple containing the number of passed tests and total tests.
    """

    # Look for lines like: 'Ran 3 tests in 0.001s'
    m = re.search(r"Ran (\d+) tests?", output)
    total = int(m.group(1)) if m else None
    # Look for 'OK' or 'FAILED (failures=1)' etc.
    if "OK" in output:
        passed = total
    else:
        # Try to count failures/errors
        fail_match = re.search(r"FAILED \((.*?)\)", output)
        failed = 0
        if fail_match:
            fail_str = fail_match.group(1)
            # e.g. 'failures=1, errors=1'
            for part in fail_str.split(","):
                if "=" in part:
                    failed += int(part.split("=")[1])
        passed = total - failed if total is not None else None
    return passed, total
