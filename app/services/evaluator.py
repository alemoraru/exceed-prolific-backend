import subprocess, tempfile, os


def evaluate_code(code: str, snippet_id: str) -> tuple[str, str]:
    # Write code to temp file
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, f"snippet_{snippet_id}.py")
        with open(path, "w") as f:
            f.write(code)
        # Syntax check
        try:
            subprocess.check_output(["python", "-m", "py_compile", path], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            return "syntax_error", e.output.decode()
        # Here you could run tests, e.g., pytest
        # For now assume success
        return "success", ""
