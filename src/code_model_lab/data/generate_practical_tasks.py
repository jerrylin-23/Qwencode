import json
from pathlib import Path
from code_model_lab.data.schemas import AlgorithmicProblem, Example, HiddenTest, Complexity

def generate_practical_tasks(output_path: Path):
    tasks = []
    
    # Generate 50 tasks
    for idx in range(1, 51):
        task_id = f"prac_{idx:06d}"
        
        if idx <= 15:
            # 1. Pandas transformations
            limit = 20 + idx
            problem = f"Write a function `filter_dataframe(df)` that takes a pandas DataFrame and returns a new DataFrame containing only rows where the column 'age' is strictly greater than {limit}."
            starter_code = "import pandas as pd\n\ndef filter_dataframe(df):\n    pass"
            
            
            hidden_tests = [
                {
                    "input": f"(pd.DataFrame({{'name': ['A', 'B'], 'age': [{limit + 5}, {limit - 5}]}}),)",
                    "expected_output": f"pd.DataFrame({{'name': ['A'], 'age': [{limit + 5}]}}).reset_index(drop=True)"
                },
                {
                    "input": f"(pd.DataFrame({{'name': ['X'], 'age': [{limit}]}}),)",
                    "expected_output": "pd.DataFrame(columns=['name', 'age']).astype({'age': 'int64'}).reset_index(drop=True)"
                }
            ]
            
            ref_sol = f"import pandas as pd\n\ndef filter_dataframe(df):\n    return df[df['age'] > {limit}].reset_index(drop=True)"
            
            complexity = Complexity(time="O(N)", space="O(N)")
            tags = ["pandas", "dataframe"]
            
        elif idx <= 30:
            # 2. JSON/Dictionary parsing
            key = f"key_{idx}"
            problem = f"Write a function `extract_json_key(json_str)` that parses a JSON string and returns the value corresponding to '{key}'. If the key does not exist, return None."
            starter_code = "import json\n\ndef extract_json_key(json_str):\n    pass"
            
            hidden_tests = [
                {"input": f"('{{\"{key}\": \"val_{idx}\"}}',)", "expected_output": f"'val_{idx}'"},
                {"input": "('{\"other\": \"val\"}',)", "expected_output": "None"},
                {"input": "('{}',)", "expected_output": "None"}
            ]
            
            ref_sol = f"import json\n\ndef extract_json_key(json_str):\n    try:\n        data = json.loads(json_str)\n        return data.get('{key}')\n    except Exception:\n        return None"
            
            complexity = Complexity(time="O(N)", space="O(N)")
            tags = ["json", "dictionary"]
            
        else:
            # 3. Text cleaning/Regex/API response formatting
            pattern = f"id_{idx}"
            problem = f"Write a function `clean_text_pattern(text)` that replaces all occurrences of '{pattern}' in the string with 'REDACTED'."
            starter_code = "import re\n\ndef clean_text_pattern(text):\n    pass"
            
            hidden_tests = [
                {"input": f"('User {pattern} logged in',)", "expected_output": "'User REDACTED logged in'"},
                {"input": "('No matches here',)", "expected_output": "'No matches here'"},
                {"input": f"('{pattern} and {pattern}',)", "expected_output": "'REDACTED and REDACTED'"}
            ]
            
            ref_sol = f"import re\n\ndef clean_text_pattern(text):\n    return text.replace('{pattern}', 'REDACTED')"
            
            complexity = Complexity(time="O(N)", space="O(1)")
            tags = ["regex", "text-cleaning"]

        task = AlgorithmicProblem(
            id=task_id,
            task_type="algorithmic_problem",
            source="synthetic_practical_gen",
            license="MIT",
            difficulty="medium",
            tags=tags,
            language="python",
            problem=problem,
            constraints="Input string/dataframe within memory limits.",
            starter_code=starter_code,
            examples=[Example(input="Input data", output="Output data", explanation="Example explanation")],
            hidden_tests=[HiddenTest(input=t["input"], expected_output=t["expected_output"]) for t in hidden_tests],
            reference_solution=ref_sol,
            explanation="Use standard library/third-party APIs to achieve the goal.",
            complexity=complexity
        )
        tasks.append(task.model_dump())
        
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for t in tasks:
            f.write(json.dumps(t) + "\n")
            
    print(f"Generated {len(tasks)} practical tasks in {output_path}.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=str, default="data/processed/sample_practical.jsonl")
    args = parser.parse_args()
    generate_practical_tasks(Path(args.output))
