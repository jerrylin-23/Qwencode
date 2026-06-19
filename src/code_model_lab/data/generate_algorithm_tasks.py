import json
import argparse
import random
from pathlib import Path
from code_model_lab.data.schemas import AlgorithmicProblem, Example, HiddenTest, Complexity, CommonFailure

CATEGORIES = [
    "arrays", "hash maps", "two pointers", "sliding window", "binary search",
    "linked lists", "stacks/queues", "trees", "graphs", "heaps", "greedy",
    "dynamic programming", "backtracking", "intervals", "strings", "math/combinatorics"
]

DIFFICULTIES = ["easy", "medium", "hard"]

def generate_task(task_id: int) -> dict:
    # Programmatic variations of algorithmic problems
    category = random.choice(CATEGORIES)
    difficulty = random.choice(DIFFICULTIES)
    
    # Let's generate a list summation task variation
    num_limit = random.randint(10, 1000)
    func_name = f"sum_elements_under_{num_limit}"
    
    problem_desc = f"Given an array of integers `nums`, return the sum of all elements that are strictly less than {num_limit}."
    starter_code = f"def {func_name}(nums):\n    pass"
    
    examples = [
        Example(
            input=f"nums = [1, {num_limit + 5}, 3]",
            output="4",
            explanation=f"Only 1 and 3 are strictly less than {num_limit}. 1 + 3 = 4."
        )
    ]
    
    hidden_tests = [
        HiddenTest(input=f"([1, {num_limit + 10}, 3],)", expected_output="4"),
        HiddenTest(input="([],)", expected_output="0"),
        HiddenTest(input=f"([{num_limit - 1}, {num_limit}, {num_limit + 1}],)", expected_output=str(num_limit - 1)),
        HiddenTest(input=f"([i for i in range({min(10, num_limit)})],)", expected_output=str(sum(range(min(10, num_limit)))))
    ]
    
    ref_sol = f"def {func_name}(nums):\n    return sum(x for x in nums if x < {num_limit})"
    
    common_failures = [
        CommonFailure(
            wrong_solution=f"def {func_name}(nums):\n    return sum(x for x in nums if x <= {num_limit})",
            failure_reason="Includes element equal to the threshold (strictly less is required).",
            failing_test=f"([{num_limit - 1}, {num_limit}, {num_limit + 1}],)"
        )
    ]
    
    task = AlgorithmicProblem(
        id=f"algo_{task_id:06d}",
        task_type="algorithmic_problem",
        source="synthetic_generator",
        license="MIT",
        difficulty=difficulty,
        tags=[category, "arrays"],
        language="python",
        problem=problem_desc,
        constraints=f"nums.length <= 1000\n-10^9 <= nums[i] <= 10^9\nlimit = {num_limit}",
        starter_code=starter_code,
        examples=examples,
        hidden_tests=hidden_tests,
        reference_solution=ref_sol,
        explanation=f"Filter list using list comprehension or generator checking x < {num_limit}, then sum it.",
        complexity=Complexity(time="O(N)", space="O(1)"),
        common_failures=common_failures
    )
    
    return task.model_dump()

def main():
    parser = argparse.ArgumentParser(description="Generate synthetic algorithmic problems.")
    parser.add_argument("--count", type=int, default=1000, help="Number of tasks to generate.")
    parser.add_argument("--output", type=str, default="data/synthetic/algorithmic_tasks.jsonl", help="Output JSONL path.")
    args = parser.parse_args()

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    count_written = 0
    with open(out_path, "w", encoding="utf-8") as f:
        for i in range(1, args.count + 1):
            task = generate_task(i)
            f.write(json.dumps(task) + "\n")
            count_written += 1

    print(f"Generated {count_written} synthetic algorithmic tasks saved to {out_path}.")

if __name__ == "__main__":
    main()
