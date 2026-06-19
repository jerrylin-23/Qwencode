import json
import argparse
from pathlib import Path

def augment_hidden_tests(task: dict) -> dict:
    # Look at the starter code / problem and generate edge case test cases
    hidden_tests = task.get("hidden_tests", [])
    
    # Check if we already have 10-30 hidden tests, otherwise add some
    if len(hidden_tests) < 10:
        # Check function name or prompt to infer context
        problem_text = task.get("problem", "").lower()
        if "sum" in problem_text:
            # Add some additional list test cases
            additional_inputs = [
                "([-100, -200, -300],)",
                "([0, 0, 0, 0],)",
                "([1, 2, 3, 4, 5, 6, 7, 8, 9, 10],)"
            ]
            for inp in additional_inputs:
                # Calculate expected output using reference solution
                ref_sol = task["reference_solution"]
                # Evaluate reference solution code locally in a safe namespace to get expected output
                local_ns = {}
                exec(ref_sol, {}, local_ns)
                # Find the function name
                func_name = list(local_ns.keys())[0]
                func = local_ns[func_name]
                try:
                    args = eval(inp)
                    result = func(*args)
                    hidden_tests.append({
                        "input": inp,
                        "expected_output": str(result)
                    })
                except Exception:
                    pass
        else:
            # Generic fallback tests
            hidden_tests.append({"input": "([],)", "expected_output": "0"})
            
    task["hidden_tests"] = hidden_tests
    return task

def main():
    parser = argparse.ArgumentParser(description="Augment hidden tests for tasks.")
    parser.add_argument("input", type=str, help="Input JSONL file.")
    parser.add_argument("output", type=str, help="Output JSONL file.")
    args = parser.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with open(in_path, "r") as fin, open(out_path, "w") as fout:
        for line in fin:
            if not line.strip():
                continue
            task = json.loads(line)
            augmented = augment_hidden_tests(task)
            fout.write(json.dumps(augmented) + "\n")
            count += 1

    print(f"Processed {count} tasks. Saved to {out_path}.")

if __name__ == "__main__":
    main()
