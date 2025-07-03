import subprocess
import tempfile
import os
import sys
import importlib.util
import json
from types import ModuleType
from typing import Tuple

from app.services.llm.intervention import get_rephrased_error_message

# Each entry: snippet_id -> (function_name, list of (args, expected) tuples)
TEST_SUITES = {
    "snippetA": (
        "build_list",
        [
            (0, []),
            (1, [0]),
            (3, [0, 1, 2]),
            (5, list(range(5))),
        ],
    ),
    "snippetB": (
        "top_three",
        [
            ([1, 2], [2, 1]),
            ([5, 1, 3, 4, 2], [5, 4, 3]),
            ([10, 9, 8, 7], [10, 9, 8]),
        ],
    ),
    "snippetC": (
        "get_third_element",
        [
            ([1, 2, 3], 3),
            (["a", "b", "c", "d"], "c"),
        ],
    ),
    "snippetD": (
        "parse_numbers",
        [
            ("1,2,3", [1, 2, 3]),
            ("10", [10]),
            ("", []),
        ],
    ),
}


def _load_module(path: str, module_name: str) -> ModuleType:
    """Dynamically load a Python file as a module."""
    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)  # type: ignore
    return mod


def evaluate_code(code: str, snippet_id: str, intervention_type: str) -> Tuple[str, str]:
    """
    1) Syntax‐check the code.
    2) Load module.
    3) Dispatch to the right test suite
    4) If errors are encountered, rephrase the error message using an LLM.
    5) Return (\"success\", \"\") or (\"syntax_error\"/\"test_failure\", details).
    """
    # 1. Write to temp file
    with tempfile.TemporaryDirectory() as td:
        filename = f"snippet_{snippet_id}.py"
        path = os.path.join(td, filename)
        with open(path, "w") as f:
            f.write(code)

        # 2. Syntax check
        try:
            subprocess.check_output(
                ["python", "-m", "py_compile", path],
                stderr=subprocess.STDOUT
            )
        except subprocess.CalledProcessError as e:
            return "syntax_error", e.output.decode()

        # 3. Prepare test runner
        if snippet_id not in TEST_SUITES:
            return "no_tests", f"No test suite defined for {snippet_id}"
        func_name, cases = TEST_SUITES[snippet_id]
        test_cases_json = json.dumps(cases)
        output_path = os.path.join(td, "results.json")
        runner_path = os.path.join(os.path.dirname(__file__), "user_runner.py")

        # 4. Run test runner as subprocess
        try:
            subprocess.check_output([
                sys.executable, runner_path, path, func_name, test_cases_json, output_path
            ], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            error_msg = e.output.decode()
            llm_msg = get_rephrased_error_message(code, error_msg, intervention_type)
            return "runtime_error", llm_msg

        # 5. Parse results
        if not os.path.exists(output_path):
            llm_msg = get_rephrased_error_message(code, "No output from test runner.", intervention_type)
            return "runtime_error", llm_msg
        with open(output_path) as f:
            result_data = json.load(f)
        if "error" in result_data:
            llm_msg = get_rephrased_error_message(code, result_data["error"], intervention_type)
            return "runtime_error", llm_msg
        results = result_data.get("results", [])
        for r in results:
            if not r.get("passed", False):
                if "error" in r:
                    llm_msg = get_rephrased_error_message(code, r["error"], intervention_type)
                    return "runtime_error", llm_msg
                else:
                    llm_msg = get_rephrased_error_message(
                        code,
                        f"For input {r['input']!r}, expected {r['expected']!r}, got {r['result']!r}",
                        intervention_type
                    )
                    return "test_failure", llm_msg
        return "success", ""
