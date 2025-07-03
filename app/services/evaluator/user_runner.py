import sys
import json
import traceback

if len(sys.argv) != 5:
    print(json.dumps({"error": "Invalid arguments"}))
    sys.exit(1)

user_code_path = sys.argv[1]
function_name = sys.argv[2]
test_cases_json = sys.argv[3]
output_path = sys.argv[4]

try:
    import importlib.util

    spec = importlib.util.spec_from_file_location("user_module", user_code_path)
    user_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(user_module)
    func = getattr(user_module, function_name)
except Exception as e:
    with open(output_path, "w") as f:
        f.write(json.dumps({"error": f"ImportError: {e}"}))
    sys.exit(0)

try:
    test_cases = json.loads(test_cases_json)
except Exception as e:
    with open(output_path, "w") as f:
        f.write(json.dumps({"error": f"TestCaseParseError: {e}"}))
    sys.exit(0)

results = []
for case in test_cases:
    inp = case[0]
    expected = case[1]
    try:
        if isinstance(inp, list):
            result = func(*inp) if isinstance(inp, tuple) else func(inp)
        else:
            result = func(inp)
        passed = result == expected
        results.append({"input": inp, "expected": expected, "result": result, "passed": passed})
    except Exception as e:
        tb = traceback.TracebackException(type(e), e, e.__traceback__)
        user_frames = []
        for frame in tb.stack:
            if user_code_path in frame.filename:
                user_frames.append(f'  File "main.py", line {frame.lineno}, in {frame.name}\n    {frame.line}')
        error_message = f"{type(e).__name__}: {e}"
        if user_frames:
            tb_filtered = "Traceback (most recent call last):\n" + "\n".join(user_frames) + f"\n{error_message}"
        else:
            tb_filtered = error_message
        results.append({"input": inp, "expected": expected, "error": tb_filtered, "passed": False})

with open(output_path, "w") as f:
    f.write(json.dumps({"results": results}))
