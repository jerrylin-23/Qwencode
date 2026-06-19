from code_model_lab.data.schemas import AlgorithmicProblem

def test_algorithmic_problem_schema():
    task_data = {
        "id": "algo_test_01",
        "task_type": "algorithmic_problem",
        "source": "unit_test",
        "license": "MIT",
        "difficulty": "easy",
        "tags": ["testing"],
        "language": "python",
        "problem": "Return 1",
        "constraints": "none",
        "starter_code": "def solve(): pass",
        "examples": [{"input": "()", "output": "1", "explanation": "Always 1"}],
        "hidden_tests": [{"input": "()", "expected_output": "1"}],
        "reference_solution": "def solve(): return 1",
        "explanation": "Simple return",
        "complexity": {"time": "O(1)", "space": "O(1)"}
    }
    
    # Validation should succeed
    problem = AlgorithmicProblem.model_validate(task_data)
    assert problem.id == "algo_test_01"
    assert problem.complexity.time == "O(1)"
