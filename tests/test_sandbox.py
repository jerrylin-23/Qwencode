from code_model_lab.eval.sandbox import run_in_sandbox

def test_sandbox_passing():
    code = "def add_one(x):\n    return x + 1"
    tests = [
        {"input": "(2,)", "expected_output": "3"},
        {"input": "(0,)", "expected_output": "1"}
    ]
    res = run_in_sandbox(code, "add_one", tests)
    assert res["status"] == "passed"
    assert len(res["results"]) == 2
    assert all(r["passed"] for r in res["results"])

def test_sandbox_compile_error():
    # Syntax error code
    code = "def add_one(x):\n    return x +"
    tests = [{"input": "(2,)", "expected_output": "3"}]
    res = run_in_sandbox(code, "add_one", tests)
    assert res["status"] == "compile_error"

def test_sandbox_failing_test():
    code = "def add_one(x):\n    return x"
    tests = [{"input": "(2,)", "expected_output": "3"}]
    res = run_in_sandbox(code, "add_one", tests)
    assert res["status"] == "failed"
    assert not res["results"][0]["passed"]
