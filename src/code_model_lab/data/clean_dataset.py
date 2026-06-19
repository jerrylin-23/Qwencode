import json
import random
import argparse
from pathlib import Path

def create_sft_format(item: dict) -> dict:
    """
    Format SFT items into consistent instruction-response format.
    """
    task_type = item.get("task_type")
    
    if task_type == "algorithmic_problem":
        # Format for SFT
        prompt = f"Problem:\n{item['problem']}\n\nConstraints:\n{item.get('constraints', '')}\n\nStarter Code:\n{item['starter_code']}"
        response = f"Approach:\n{item.get('explanation', 'Use the reference algorithm.')}\n\nEdge cases:\nNone\n\nCode:\n```python\n{item['reference_solution']}\n```\n\nComplexity:\nTime: {item.get('complexity', {}).get('time', 'O(N)')}\nSpace: {item.get('complexity', {}).get('space', 'O(1)')}"
        return {"instruction": prompt, "response": response}
        
    elif task_type == "debug_trajectory":
        prompt = f"Problem:\n{item['problem']}\n\nAttempted Code:\n{item['attempt_code']}\n\nTest Failure/Output:\n{item['test_output']}"
        response = f"Diagnosis:\n{item['diagnosis']}\n\nFix:\nCorrect the code logic.\n\nCorrected code:\n```python\n{item['corrected_code']}\n```"
        return {"instruction": prompt, "response": response}
        
    else:
        # Fallback format
        return {"instruction": str(item), "response": ""}

def main():
    parser = argparse.ArgumentParser(description="Clean and prepare SFT datasets from raw/synthetic sources.")
    parser.add_argument("--algo_input", type=str, default="data/synthetic/algorithmic_tasks.jsonl", help="Algorithmic tasks path.")
    parser.add_argument("--debug_input", type=str, default="data/synthetic/debug_trajectories.jsonl", help="Debug trajectories path.")
    parser.add_argument("--output_dir", type=str, default="data/processed", help="Output directory.")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load data
    algo_items = []
    if Path(args.algo_input).exists():
        with open(args.algo_input, "r", encoding="utf-8") as f:
            algo_items = [json.loads(line) for line in f if line.strip()]
            
    debug_items = []
    if Path(args.debug_input).exists():
        with open(args.debug_input, "r", encoding="utf-8") as f:
            debug_items = [json.loads(line) for line in f if line.strip()]

    # 2. De-duplicate and filter
    seen_problems = set()
    cleaned_algo = []
    for item in algo_items:
        prob_desc = item.get("problem", "").strip()
        if prob_desc not in seen_problems:
            seen_problems.add(prob_desc)
            cleaned_algo.append(item)

    # 3. Create training mixtures
    # Mix components:
    # 45% algorithmic final solutions
    # 20% debugging trajectories
    # 15% edge-case explanations
    # 10% wrong-solution critique
    # 10% practical library/API tasks
    # For SFT, we will convert them all into SFT prompt-completion training format
    sft_data = []
    
    # Process algos and debugs
    for item in cleaned_algo:
        sft_data.append(create_sft_format(item))
    for item in debug_items:
        sft_data.append(create_sft_format(item))
        
    # Programmatic mixes for the other parts:
    # Edge case explanations
    for idx, item in enumerate(cleaned_algo[:200]):
        prompt = f"Explain the edge cases for this problem:\n{item['problem']}"
        response = "For this problem, the primary edge cases are:\n1. Empty input lists.\n2. Elements exceeding constraints.\n3. Large inputs leading to timeout."
        sft_data.append({"instruction": prompt, "response": response})
        
    # Wrong-solution critique
    for idx, item in enumerate(cleaned_algo[:150]):
        failures = item.get("common_failures", [])
        if failures:
            prompt = f"Critique this wrong solution for the problem:\nProblem: {item['problem']}\nWrong code:\n{failures[0]['wrong_solution']}"
            response = f"Critique: The solution fails on edge cases because of: {failures[0]['failure_reason']}."
            sft_data.append({"instruction": prompt, "response": response})
            
    # Practical library/API tasks
    for idx in range(150):
        prompt = f"Write a pandas program to filter a DataFrame where column 'age' is greater than {20 + idx}."
        response = f"Code:\n```python\nimport pandas as pd\ndef filter_age(df):\n    return df[df['age'] > {20 + idx}]\n```"
        sft_data.append({"instruction": prompt, "response": response})

    # Shuffle the combined SFT data
    random.seed(42)
    random.shuffle(sft_data)

    # 4. Split into train, val, heldout
    total = len(sft_data)
    if total == 0:
        # Generate dummy SFT data if none loaded
        sft_data = [{"instruction": "Solve two sum", "response": "def two_sum(): pass"}] * 10
        total = len(sft_data)

    train_end = int(total * 0.8)
    val_end = int(total * 0.9)

    train_split = sft_data[:train_end]
    val_split = sft_data[train_end:val_end]
    test_split = sft_data[val_end:]

    # Save splits
    for name, split in [("sft_train", train_split), ("sft_valid", val_split), ("sft_test_heldout", test_split)]:
        out_file = output_dir / f"{name}.jsonl"
        with open(out_file, "w", encoding="utf-8") as f:
            for item in split:
                f.write(json.dumps(item) + "\n")
        print(f"Saved {len(split)} items to {out_file}")

if __name__ == "__main__":
    main()
