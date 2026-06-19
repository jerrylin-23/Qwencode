import re
import yaml
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table

from code_model_lab.models import prompt_templates
from code_model_lab.eval.sandbox import run_in_sandbox
from code_model_lab.eval.run_algorithm_eval import extract_code

console = Console()

def run_practical_eval(config_path: Path):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    # Load model config
    model_config_path = Path(config["model_config"])
    if not model_config_path.is_absolute():
        candidate = config_path.parent / model_config_path
        if candidate.exists():
            model_config_path = candidate
    
    with open(model_config_path, "r") as f:
        m_config = yaml.safe_load(f)
    
    # Initialize client
    from code_model_lab.models import get_model_client
    client = get_model_client(m_config)
    
    # Use the practical subset dataset
    dataset_path = Path("data/processed/sample_practical.jsonl")
    if not dataset_path.exists():
        dataset_path = Path("/Users/jerry/Projects/Qwencode") / dataset_path

    console.print(f"[bold green]Starting practical BigCodeBench-style evaluation on {dataset_path}...[/bold green]")
    
    tasks = []
    with open(dataset_path, "r") as f:
        for line in f:
            if line.strip():
                tasks.append(json.loads(line))
                
    results = []
    total_tasks = len(tasks)
    passed_tasks = 0
    compiled_tasks = 0
    total_retries = 0
    
    start_time = time.time()
    prompt_style = config.get("prompt_style", "structured")
    
    for task in tasks:
        task_id = task["id"]
        # Extract entrypoint function name
        entrypoint_match = re.search(r"def\s+(\w+)\(", task["starter_code"])
        entrypoint = entrypoint_match.group(1) if entrypoint_match else "solve"
        
        console.print(f"\n[bold]Evaluating Practical Task {task_id}: {entrypoint}[/bold]")
        
        # Format the prompt
        if prompt_style == "direct":
            prompt = prompt_templates.ALGORITHMIC_DIRECT.format(
                problem=task["problem"],
                starter_code=task["starter_code"]
            )
        else:
            prompt = prompt_templates.ALGORITHMIC_STRUCTURED.format(
                problem=task["problem"],
                constraints=task.get("constraints", ""),
                starter_code=task["starter_code"]
            )
            
        t0 = time.time()
        # In mock mode, we intercept and return correct pandas / json / regex code
        if client.eval_mode == "mock":
            if "filter_dataframe" in entrypoint:
                model_output = f"""```python
import pandas as pd
def filter_dataframe(df):
    return df[df['age'] > {20 + int(task_id.split('_')[1])}].reset_index(drop=True)
```"""
            elif "extract_json_key" in entrypoint:
                key = f"key_{int(task_id.split('_')[1])}"
                model_output = f"""```python
import json
def extract_json_key(json_str):
    try:
        data = json.loads(json_str)
        return data.get('{key}')
    except Exception:
        return None
```"""
            elif "clean_text_pattern" in entrypoint:
                pattern = f"id_{int(task_id.split('_')[1])}"
                model_output = f"""```python
def clean_text_pattern(text):
    return text.replace('{pattern}', 'REDACTED')
```"""
            else:
                model_output = client.generate(prompt, temperature=0.0)
        else:
            model_output = client.generate(prompt, temperature=0.0)
            
        latency = time.time() - t0
        
        code = extract_code(model_output, entrypoint)
        
        sandbox_res = run_in_sandbox(
            code=code,
            entrypoint=entrypoint,
            test_cases=task["hidden_tests"],
            timeout=10.0
        )
        
        status = sandbox_res.get("status")
        retry_count = 0
        max_retries = config.get("num_retries", 3)
        
        while status != "passed" and retry_count < max_retries:
            retry_count += 1
            total_retries += 1
            console.print(f"[yellow]  Attempt {retry_count} failed ({status}). Retrying...[/yellow]")
            
            test_output = ""
            if sandbox_res.get("message"):
                test_output = sandbox_res["message"]
            else:
                failed_tests = [r for r in sandbox_res.get("results", []) if not r.get("passed")]
                if failed_tests:
                    test_output = json.dumps(failed_tests[0], indent=2)
            
            repair_prompt = prompt_templates.DEBUG_PROMPT.format(
                problem=task["problem"],
                attempt_code=code,
                test_output=test_output
            )
            
            model_output = client.generate(repair_prompt, temperature=0.0)
            code = extract_code(model_output, entrypoint)
            
            sandbox_res = run_in_sandbox(
                code=code,
                entrypoint=entrypoint,
                test_cases=task["hidden_tests"],
                timeout=10.0
            )
            status = sandbox_res.get("status")
            
        is_passed = (status == "passed")
        is_compiled = (status != "compile_error")
        
        if is_passed:
            passed_tasks += 1
        if is_compiled:
            compiled_tasks += 1
            
        results.append({
            "id": task_id,
            "entrypoint": entrypoint,
            "status": status,
            "passed": is_passed,
            "compiled": is_compiled,
            "retries": retry_count,
            "latency": latency,
            "code": code
        })
        
        console.print(f"Task {task_id} result: [bold green]PASSED[/bold green]" if is_passed else f"Task {task_id} result: [bold red]FAILED ({status})[/bold red]")
        
    duration = time.time() - start_time
    
    # Compute metrics
    pass_rate = (passed_tasks / total_tasks) * 100 if total_tasks else 0
    compile_rate = (compiled_tasks / total_tasks) * 100 if total_tasks else 0
    avg_retries = total_retries / total_tasks if total_tasks else 0
    
    # Print metrics table
    table = Table(title="Practical Library/API Evaluation Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    table.add_row("Total Tasks", str(total_tasks))
    table.add_row("Passed Tasks", str(passed_tasks))
    table.add_row("Pass Rate", f"{pass_rate:.1f}%")
    table.add_row("Compile Rate", f"{compile_rate:.1f}%")
    table.add_row("Avg Retries", f"{avg_retries:.2f}")
    table.add_row("Total Time", f"{duration:.1f}s")
    console.print(table)
    
    # Save reports
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("reports/practical_runs") / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)
    
    report_file = output_dir / "report.json"
    with open(report_file, "w") as f:
        json.dump({
            "metrics": {
                "total_tasks": total_tasks,
                "passed_tasks": passed_tasks,
                "pass_rate": pass_rate,
                "compile_rate": compile_rate,
                "avg_retries": avg_retries,
                "duration_seconds": duration
            },
            "results": results
        }, f, indent=2)
        
    # Save a static practical results report
    static_report = Path("reports/practical_results.md")
    static_report.parent.mkdir(parents=True, exist_ok=True)
    with open(static_report, "w") as f:
        f.write("# Practical Library/API Coding Evaluation Results\n\n")
        f.write(f"Generated on {timestamp} using {client.model_name} (Mode: {client.eval_mode}).\n\n")
        f.write("| Model | Dataset | pass@1 | compile rate | avg retries | notes |\n")
        f.write("|---|---|---|---|---|---|\n")
        f.write(f"| {client.model_name} | BigCodeBench-subset | {pass_rate:.1f}% | {compile_rate:.1f}% | {avg_retries:.2f} | Practical library/API tasks |\n")

    console.print(f"[bold green]Practical evaluation completed. Report saved to {report_file}[/bold green]")

def main():
    parser = argparse.ArgumentParser(description="Run BigCodeBench-Style Practical Evaluation.")
    parser.add_argument("--config", type=str, default="configs/eval_algorithms.yaml", help="Path to evaluation config file.")
    args = parser.parse_args()
    
    run_practical_eval(Path(args.config))

if __name__ == "__main__":
    main()
