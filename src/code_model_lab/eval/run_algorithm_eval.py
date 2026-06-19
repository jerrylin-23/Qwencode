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
from code_model_lab.models.ollama_client import GenerationError
from code_model_lab.eval.sandbox import run_in_sandbox

console = Console()

def extract_code(model_output: str, entrypoint: str) -> str:
    """
    Extracts the Python code block from model output.
    """
    # Try finding markdown code blocks
    pattern = r"```(?:python)?\n(.*?)\n```"
    blocks = re.findall(pattern, model_output, re.DOTALL)
    if not blocks:
        # Fallback to general code blocks
        blocks = re.findall(r"```\n(.*?)\n```", model_output, re.DOTALL)
    
    if blocks:
        # If multiple, return the one containing the entrypoint definition
        for block in blocks:
            if f"def {entrypoint}" in block:
                return block
        return blocks[0]
    
    # If no blocks, try to filter out markdown/prose lines
    lines = model_output.splitlines()
    cleaned = []
    in_code = False
    for line in lines:
        if line.strip().startswith("def ") or line.strip().startswith("import ") or line.strip().startswith("from "):
            in_code = True
        if in_code:
            cleaned.append(line)
    if cleaned:
        return "\n".join(cleaned)
    
    return model_output

def run_eval(config_path: Path):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    # Load model config
    model_config_path = Path(config["model_config"])
    if not model_config_path.is_absolute():
        candidate = config_path.parent / model_config_path
        if candidate.exists():
            model_config_path = candidate
        # else keep it as is or default to workspace relative path if that exists
    
    with open(model_config_path, "r") as f:
        m_config = yaml.safe_load(f)
    
    # Initialize client
    from code_model_lab.models import get_model_client
    client = get_model_client(m_config)
    
    dataset_path = Path(config["eval_dataset"])
    if not dataset_path.exists():
        # fallback to root path
        dataset_path = Path("/Users/jerry/Projects/Qwencode") / config["eval_dataset"]

    console.print(f"[bold green]Starting algorithmic evaluation on {dataset_path}...[/bold green]")
    
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
    
    # Track metrics
    start_time = time.time()
    
    # Determine prompt style: structured vs direct
    # Default is structured if prompt style is not configured or is structured
    prompt_style = config.get("prompt_style", "structured")
    
    for task in tasks:
        task_id = task["id"]
        # Extract entrypoint function name from starter_code (e.g. def two_sum(nums, target): -> two_sum)
        entrypoint_match = re.search(r"def\s+(\w+)\(", task["starter_code"])
        entrypoint = entrypoint_match.group(1) if entrypoint_match else "solve"
        
        console.print(f"\n[bold]Evaluating Task {task_id}: {entrypoint}[/bold]")
        
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
        try:
            model_output = client.generate(prompt, temperature=0.0)
        except GenerationError as e:
            latency = time.time() - t0
            console.print(f"[bold red]Task {task_id}: generation error[/bold red] ({e})")
            results.append({
                "id": task_id, "entrypoint": entrypoint, "status": "generation_error",
                "passed": False, "compiled": False, "retries": 0,
                "latency": latency, "code": "", "sandbox_results": {"status": "generation_error"},
            })
            continue
        latency = time.time() - t0

        code = extract_code(model_output, entrypoint)
        
        # Sandbox execution
        sandbox_res = run_in_sandbox(
            code=code,
            entrypoint=entrypoint,
            test_cases=task["hidden_tests"],
            timeout=config.get("timeout_per_test", 2.0)
        )
        
        status = sandbox_res.get("status")
        retry_count = 0
        max_retries = config.get("num_retries", 3)
        
        # Execution-feedback retry loop
        while status != "passed" and retry_count < max_retries:
            retry_count += 1
            total_retries += 1
            console.print(f"[yellow]  Attempt {retry_count} failed ({status}). Retrying with feedback...[/yellow]")
            
            # Format test failure output
            test_output = ""
            if sandbox_res.get("message"):
                test_output = sandbox_res["message"]
            else:
                failed_tests = [r for r in sandbox_res.get("results", []) if not r.get("passed")]
                if failed_tests:
                    test_output = json.dumps(failed_tests[0], indent=2)
            
            # Generate repair prompt
            repair_prompt = prompt_templates.DEBUG_PROMPT.format(
                problem=task["problem"],
                attempt_code=code,
                test_output=test_output
            )
            
            try:
                model_output = client.generate(repair_prompt, temperature=0.0)
            except GenerationError as e:
                console.print(f"[red]  Repair generation error: {e}[/red]")
                break
            code = extract_code(model_output, entrypoint)

            sandbox_res = run_in_sandbox(
                code=code,
                entrypoint=entrypoint,
                test_cases=task["hidden_tests"],
                timeout=config.get("timeout_per_test", 2.0)
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
            "code": code,
            "sandbox_results": sandbox_res
        })
        
        console.print(f"Task {task_id} result: [bold green]PASSED[/bold green]" if is_passed else f"Task {task_id} result: [bold red]FAILED ({status})[/bold red]")
        
    duration = time.time() - start_time
    
    # Compute metrics
    pass_rate = (passed_tasks / total_tasks) * 100 if total_tasks else 0
    compile_rate = (compiled_tasks / total_tasks) * 100 if total_tasks else 0
    avg_retries = total_retries / total_tasks if total_tasks else 0
    
    # Print metrics table
    table = Table(title="Evaluation Metrics Summary")
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
    output_dir = Path(config.get("output_dir", "reports/eval_runs")) / timestamp
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
        
    # Write a markdown report
    md_file = output_dir / "report.md"
    with open(md_file, "w") as f:
        f.write(f"# Algorithmic Evaluation Report - {timestamp}\n\n")
        f.write(f"- **Total Tasks**: {total_tasks}\n")
        f.write(f"- **Passed Tasks**: {passed_tasks}\n")
        f.write(f"- **Pass Rate**: {pass_rate:.1f}%\n")
        f.write(f"- **Compile Rate**: {compile_rate:.1f}%\n")
        f.write(f"- **Average Retries**: {avg_retries:.2f}\n")
        f.write(f"- **Duration**: {duration:.1f}s\n\n")
        f.write("## Task Results\n\n")
        f.write("| Task ID | Entrypoint | Status | Passed | Retries | Latency (s) |\n")
        f.write("|---|---|---|---|---|---|\n")
        for res in results:
            f.write(f"| {res['id']} | {res['entrypoint']} | {res['status']} | {res['passed']} | {res['retries']} | {res['latency']:.1f} |\n")
            
    # Also symlink or write to a static baseline report path for Phase 5 / 13 reporting
    static_report = Path("reports/baseline_results.md")
    static_report.parent.mkdir(parents=True, exist_ok=True)
    with open(static_report, "w") as f:
        f.write("# Baseline Algorithmic Evaluation Results\n\n")
        f.write(f"Generated on {timestamp} using {client.model_name} (Mode: {client.eval_mode}).\n\n")
        f.write("| Model | Prompt | pass@1 | compile rate | avg retries | notes |\n")
        f.write("|---|---|---|---|---|---|\n")
        f.write(f"| {client.model_name} | {prompt_style} | {pass_rate:.1f}% | {compile_rate:.1f}% | {avg_retries:.2f} | Eval Mode: {client.eval_mode} |\n")

    console.print(f"[bold green]Evaluation report saved to {report_file}[/bold green]")
    console.print(f"[bold green]Markdown report saved to {md_file}[/bold green]")
    console.print(f"[bold green]Baseline results saved to {static_report}[/bold green]")

def main():
    parser = argparse.ArgumentParser(description="Run Algorithmic Evaluation.")
    parser.add_argument("--config", type=str, default="configs/eval_algorithms.yaml", help="Path to evaluation config file.")
    args = parser.parse_args()
    
    run_eval(Path(args.config))

if __name__ == "__main__":
    main()
