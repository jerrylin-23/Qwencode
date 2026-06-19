from typing import List, Optional
from pydantic import BaseModel

class Example(BaseModel):
    input: str
    output: str
    explanation: Optional[str] = None

class HiddenTest(BaseModel):
    input: str
    expected_output: str

class CommonFailure(BaseModel):
    wrong_solution: str
    failure_reason: str
    failing_test: str

class Complexity(BaseModel):
    time: str
    space: str

class AlgorithmicProblem(BaseModel):
    id: str
    task_type: str = "algorithmic_problem"
    source: str
    license: str
    difficulty: str
    tags: List[str]
    language: str = "python"
    problem: str
    constraints: str
    starter_code: str
    examples: List[Example]
    hidden_tests: List[HiddenTest]
    reference_solution: str
    explanation: str
    complexity: Complexity
    common_failures: Optional[List[CommonFailure]] = None

class DebugTrajectory(BaseModel):
    id: str
    task_type: str = "debug_trajectory"
    problem_id: str
    language: str = "python"
    problem: str
    attempt_code: str
    test_output: str
    diagnosis: str
    corrected_code: str
    final_result: str = "pass"

class RepoRepair(BaseModel):
    id: str
    task_type: str = "repo_repair"
    repo_name: str
    language: str = "python"
    issue: str
    relevant_files: List[str]
    localized_symbols: List[str]
    failing_test_output: str
    patch_diff: str
    test_command: str = "pytest"
    final_test_result: str = "pass"
