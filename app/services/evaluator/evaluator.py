import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile
import ast
from types import ModuleType
from typing import Optional, Tuple


def evaluate_code(
    code: str, snippet_id: str
) -> Tuple[str, str, Optional[int], Optional[int]]:
    """
    Evaluate user code against a predefined snippet and its test suite.
    This function performs the following steps:

    1) Syntax‐check the code.
    2) Copy user code and test suite to temp dir.
    3) Run the user code to check for runtime errors.
    4) Run only the relevant unittest class for the snippet.
    5) If errors are encountered, rephrase the error message using an LLM.
    6) Return the evaluation status, rephrased error message, and test results.

    :param code: The user code to evaluate.
    :param snippet_id: The ID of the snippet to evaluate against.
    :return: A tuple containing:
        - status: "success", "syntax_error", "runtime_error", "test_failure", "not_found", or "high_risk_code"
        - produced error message (if applicable)
        - number of tests passed (if applicable)
        - total number of tests (if applicable)
    """
    snippet_map = {
        "A": ("snippetA/snippetA.py", "snippetA/test_snippetA.py", "TestSnippetA"),
        "B": ("snippetB/snippetB.py", "snippetB/test_snippetB.py", "TestSnippetB"),
        "C": ("snippetC/snippetC.py", "snippetC/test_snippetC.py", "TestSnippetC"),
        "D": ("snippetD/snippetD.py", "snippetD/test_snippetD.py", "TestSnippetD"),
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

        # Malicious code detection
        if detect_malicious_code(code):
            return "high_risk_code", "Malicious or high-risk code detected.", None, None

        # Syntax check user code
        try:
            subprocess.check_output(
                [sys.executable, "-m", "py_compile", user_code_path],
                stderr=subprocess.STDOUT,
            )
        except subprocess.CalledProcessError as e:
            # Syntax error when compiling the file, return the error
            return "syntax_error", e.output.decode("utf-8"), None, None

        # Run the file itself
        try:
            run_result = subprocess.run(
                [sys.executable, user_code_path],
                cwd=td,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if run_result.returncode != 0:
                # Runtime error when running the file
                error_msg = run_result.stderr or run_result.stdout
                return "runtime_error", error_msg, None, None
        except Exception as e:
            return "runtime_error", str(e), None, None

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
        except Exception as e:
            # If there is an error running the unittest command
            return "runtime_error", str(e), None, None
        if result.returncode == 0:
            # Parse output for test count
            passed, total = _parse_unittest_output(result.stdout, result.stderr)
            return "success", "", passed, total
        else:
            passed, total = _parse_unittest_output(result.stdout, result.stderr)
            # Return the number of tests passed and total tests
            return "test_failure", "", passed, total


def detect_malicious_code(code: str) -> bool:
    """
    Scan code using AST to detect potentially malicious usage.
    Only blocks os.system calls, allows other os usages (including os.path.exists).
    :param code: The user code to scan.
    :return: True if high-risk code is detected, else False.
    """
    try:
        tree = ast.parse(code)
    except Exception:
        return False

    risky_names = {
        "sys",
        "subprocess",
        "shutil",
        "socket",
        "threading",
        "multiprocessing",
        "ctypes",
        "pickle",
        "eval",
        "exec",
        "compile",
        "open",
        "__import__",
    }

    for node in ast.walk(tree):
        # Detect risky imports (allow os completely)
        if isinstance(node, ast.Import):
            for alias in node.names:
                modname = alias.name.split(".")[0]
                if modname != "os" and modname in risky_names:
                    return True
        if isinstance(node, ast.ImportFrom):
            if node.module:
                modname = node.module.split(".")[0]
                if modname != "os" and modname in risky_names:
                    return True

        # Detect risky calls
        if isinstance(node, ast.Call):
            # Allow os.path.exists only
            if isinstance(node.func, ast.Attribute):
                # Allow: os.path.exists(...)
                if (
                    isinstance(node.func.value, ast.Attribute)
                    and isinstance(node.func.value.value, ast.Name)
                    and node.func.value.value.id == "os"
                    and node.func.value.attr == "path"
                    and node.func.attr == "exists"
                ):
                    continue

                # Block: os.system(...)
                if isinstance(node.func.value, ast.Name) and node.func.value.id == "os":
                    if node.func.attr == "system":
                        return True

                # Block other risky attributes (e.g., subprocess.call)
                full_name = f"{getattr(node.func.value, 'id', '')}.{node.func.attr}"
                if node.func.attr in risky_names or full_name in risky_names:
                    return True

            if isinstance(node.func, ast.Name) and node.func.id in risky_names:
                return True

    return False


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


def _parse_unittest_output(
    output: str, stderr: str = None
) -> Tuple[Optional[int], Optional[int]]:
    """
    Parse unittest output (stdout and optionally stderr) to extract number of passed and total tests.
    :param output: The output string from unittest stdout.
    :param stderr: The output string from unittest stderr (optional).
    :return: A tuple containing the number of passed tests and total tests.
    """
    # Combine stdout and stderr for parsing
    combined = output
    if stderr:
        combined += "\n" + stderr

    # Look for lines like: 'Ran 3 tests in 0.001s'
    m = re.search(r"Ran (\d+) tests?", combined)
    total = int(m.group(1)) if m else None
    # Look for 'OK' or 'FAILED (failures=1)' etc.
    if "OK" in combined:
        passed = total
    else:
        # Try to count failures/errors/skips
        fail_match = re.search(r"FAILED \((.*?)\)", combined)
        failed = 0
        if fail_match:
            fail_str = fail_match.group(1)
            # e.g. 'failures=1, errors=1, skipped=1'
            for part in fail_str.split(","):
                if "=" in part:
                    failed += int(part.split("=")[1])
        passed = total - failed if total is not None else None
    return passed, total
