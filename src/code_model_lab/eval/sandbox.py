import sys
import tempfile
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, List

def run_in_sandbox(code: str, entrypoint: str, test_cases: List[Dict[str, str]], timeout: float = 2.0) -> Dict[str, Any]:
    """
    Runs code against test cases in a temporary file using a subprocess.
    Returns a dict with test results.
    """
    # Create the test runner script content
    runner_template = """
import sys
import json

{code}

# Test runner
test_cases = {test_cases}
entrypoint_name = "{entrypoint}"

if entrypoint_name not in globals():
    print(json.dumps({{"status": "compile_error", "message": f"Entrypoint '{{entrypoint_name}}' not found in code."}}))
    sys.exit(0)

func = globals()[entrypoint_name]
results = []
all_passed = True

for idx, tc in enumerate(test_cases):
    inp_str = tc["input"]
    exp_str = tc["expected_output"]
    try:
        # Evaluate inputs as args
        args = eval(inp_str)
        if not isinstance(args, tuple):
            args = (args,)
        
        # Evaluate expected output
        expected = eval(exp_str)
        
        # Call the function
        actual = func(*args)
        
        # Check correctness using a safe helper to handle pandas structures
        def safe_equals(a, b):
            try:
                import pandas as pd
                if isinstance(a, pd.DataFrame) and isinstance(b, pd.DataFrame):
                    try:
                        pd.testing.assert_frame_equal(
                            a.reset_index(drop=True),
                            b.reset_index(drop=True),
                            check_dtype=False,
                            check_column_type=False,
                            check_index_type=False
                        )
                        return True
                    except AssertionError:
                        return False
                if isinstance(a, pd.Series) and isinstance(b, pd.Series):
                    try:
                        pd.testing.assert_series_equal(
                            a.reset_index(drop=True),
                            b.reset_index(drop=True),
                            check_dtype=False,
                            check_index_type=False
                        )
                        return True
                    except AssertionError:
                        return False
            except ImportError:
                pass
            return a == b

        if safe_equals(actual, expected):
            results.append({{"test_index": idx, "passed": True}})
        else:
            results.append({{
                "test_index": idx, 
                "passed": False, 
                "expected": exp_str, 
                "actual": str(actual),
                "error": f"Expected {{expected}} (type {{type(expected).__name__}}), got {{actual}} (type {{type(actual).__name__}})"
            }})
            all_passed = False
    except Exception as e:
        results.append({{
            "test_index": idx,
            "passed": False,
            "error": f"Runtime error: {{type(e).__name__}}: {{str(e)}}"
        }})
        all_passed = False

status = "passed" if all_passed else "failed"
print(json.dumps({{"status": status, "results": results}}))
"""

    formatted_runner = runner_template.format(
        code=code,
        entrypoint=entrypoint,
        test_cases=repr(test_cases)
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_file = Path(tmpdir) / "test_run.py"
        with open(tmp_file, "w", encoding="utf-8") as f:
            f.write(formatted_runner)

        # Run subprocess.
        # To prevent network access or restricted imports, we can run with standard sandbox precautions.
        # For a local lab, running as subprocess with timeout is the primary tool.
        try:
            # We use sys.executable to ensure we run under the same Python interpreter (and environment)
            proc = subprocess.run(
                [sys.executable, str(tmp_file)],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if proc.returncode != 0:
                # Compile or syntax/runtime error in global execution scope
                return {
                    "status": "compile_error",
                    "message": f"Process exited with non-zero code {proc.returncode}.\nStderr: {proc.stderr}\nStdout: {proc.stdout}",
                    "results": []
                }
            
            stdout_clean = proc.stdout.strip()
            # Find the last line that matches JSON if there are prints
            json_line = None
            for line in stdout_clean.splitlines():
                if line.startswith("{") and line.endswith("}"):
                    json_line = line
            
            if json_line:
                return json.loads(json_line)
            else:
                return {
                    "status": "runtime_error",
                    "message": f"Could not parse test results from stdout:\n{proc.stdout}\nStderr: {proc.stderr}",
                    "results": []
                }
                
        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "message": f"Execution timed out after {timeout} seconds.",
                "results": []
            }
        except Exception as e:
            return {
                "status": "sandbox_error",
                "message": str(e),
                "results": []
            }
