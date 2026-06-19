import sys
import json
import argparse
from pathlib import Path
from rich.console import Console

from code_model_lab.data.schemas import AlgorithmicProblem, DebugTrajectory, RepoRepair

console = Console()

def validate_file(filepath: Path) -> bool:
    if not filepath.exists():
        console.print(f"[red]Error: File {filepath} does not exist.[/red]")
        return False

    console.print(f"[bold blue]Validating {filepath}...[/bold blue]")
    
    valid_count = 0
    errors = 0

    with open(filepath, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                data = json.loads(line)
            except json.JSONDecodeError as e:
                console.print(f"[red]Line {line_num}: Invalid JSON - {e}[/red]")
                errors += 1
                continue

            task_type = data.get("task_type")
            try:
                if task_type == "algorithmic_problem":
                    AlgorithmicProblem.model_validate(data)
                elif task_type == "debug_trajectory":
                    DebugTrajectory.model_validate(data)
                elif task_type == "repo_repair":
                    RepoRepair.model_validate(data)
                elif not task_type:
                    console.print(f"[yellow]Line {line_num}: Missing 'task_type'. Attempting to infer schema.[/yellow]")
                    # Infer:
                    if "problem" in data and "hidden_tests" in data:
                        AlgorithmicProblem.model_validate(data)
                    elif "attempt_code" in data:
                        DebugTrajectory.model_validate(data)
                    elif "patch_diff" in data:
                        RepoRepair.model_validate(data)
                    else:
                        raise ValueError("Could not infer task type from fields.")
                else:
                    console.print(f"[red]Line {line_num}: Unknown task_type '{task_type}'[/red]")
                    errors += 1
                    continue
                
                valid_count += 1
            except Exception as e:
                console.print(f"[red]Line {line_num} validation failed: {e}[/red]")
                errors += 1

    if errors > 0:
        console.print(f"[bold red]Validation failed with {errors} errors (validated {valid_count} successfully).[/bold red]")
        return False
    else:
        console.print(f"[bold green]Success: All {valid_count} lines validated successfully.[/bold green]")
        return True

def main():
    parser = argparse.ArgumentParser(description="Validate JSONL datasets against schemas.")
    parser.add_argument("file", type=str, help="Path to JSONL file to validate.")
    args = parser.parse_args()

    success = validate_file(Path(args.file))
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
