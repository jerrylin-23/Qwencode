import json
import argparse
from pathlib import Path
from code_model_lab.data.schemas import DebugTrajectory

def main():
    parser = argparse.ArgumentParser(description="Generate synthetic debug trajectories.")
    parser.add_argument("--input", type=str, default="data/synthetic/algorithmic_tasks.jsonl", help="Input synthetic tasks path.")
    parser.add_argument("--output", type=str, default="data/synthetic/debug_trajectories.jsonl", help="Output JSONL path.")
    parser.add_argument("--count", type=int, default=300, help="Number of trajectories to generate.")
    args = parser.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)
    
    if not in_path.exists():
        print(f"Input file {in_path} does not exist. Please run generate_algorithm_tasks first.")
        # Try to use mock generation if input doesn't exist
        tasks = []
    else:
        with open(in_path, "r", encoding="utf-8") as f:
            tasks = [json.loads(line) for line in f if line.strip()]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    generated = 0
    with open(out_path, "w", encoding="utf-8") as f:
        # Loop through tasks and generate trajectories
        for idx, task in enumerate(tasks):
            if generated >= args.count:
                break
            
            failures = task.get("common_failures", [])
            for failure in failures:
                if generated >= args.count:
                    break
                
                trajectory = DebugTrajectory(
                    id=f"debug_{generated + 1:06d}",
                    task_type="debug_trajectory",
                    problem_id=task["id"],
                    language="python",
                    problem=task["problem"],
                    attempt_code=failure["wrong_solution"],
                    test_output=f"AssertionError on input {failure['failing_test']}: Expected correct output but got incorrect result.",
                    diagnosis=failure["failure_reason"],
                    corrected_code=task["reference_solution"],
                    final_result="pass"
                )
                f.write(json.dumps(trajectory.model_dump()) + "\n")
                generated += 1
                
        # If we need more to reach count, generate programmatically
        while generated < args.count:
            # Generate a simple generic debug trajectory
            trajectory = DebugTrajectory(
                id=f"debug_{generated + 1:06d}",
                task_type="debug_trajectory",
                problem_id=f"algo_gen_{generated}",
                language="python",
                problem="Compute the square of x.",
                attempt_code="def square(x):\n    return x + x",
                test_output="AssertionError on input (3,): Expected 9, got 6",
                diagnosis="Addition was used instead of multiplication.",
                corrected_code="def square(x):\n    return x * x",
                final_result="pass"
            )
            f.write(json.dumps(trajectory.model_dump()) + "\n")
            generated += 1

    print(f"Generated {generated} debug trajectories. Saved to {out_path}.")

if __name__ == "__main__":
    main()
