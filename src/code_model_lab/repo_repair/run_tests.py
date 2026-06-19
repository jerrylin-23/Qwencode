import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import Dict, Any

def run_repo_tests(repo_path: Path) -> Dict[str, Any]:
    """
    Runs pytest inside a specific repository path.
    Returns status and output logs.
    """
    # Find any tests dir or test files
    tests_dir = repo_path / "tests"
    if not tests_dir.exists():
        return {"passed": False, "status": "no_tests", "message": "No tests directory found."}

    # Run pytest using the current Python interpreter
    try:
        # We set PYTHONPATH to "." so it imports from the repo root
        # and we pass relative path "tests" to avoid root pyproject.toml shadowing issues
        env = dict(subprocess.os.environ)
        env["PYTHONPATH"] = f".{os.pathsep}{env.get('PYTHONPATH', '')}"
        
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "tests"],
            capture_output=True,
            text=True,
            timeout=10.0,
            cwd=str(repo_path),
            env=env
        )
        
        passed = (proc.returncode == 0)
        return {
            "passed": passed,
            "status": "passed" if passed else "failed",
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "message": proc.stdout if not passed else "All tests passed."
        }
    except subprocess.TimeoutExpired:
        return {"passed": False, "status": "timeout", "message": "Tests execution timed out."}
    except Exception as e:
        return {"passed": False, "status": "error", "message": f"Execution error: {str(e)}"}




def main():
    parser = argparse.ArgumentParser(description="Run tests for SWE-bench repositories.")
    parser.add_argument("--benchmark", type=str, required=True, help="Path to mini_swe benchmark directory or single repo.")
    args = parser.parse_args()

    benchmark_path = Path(args.benchmark)
    
    if not benchmark_path.exists():
        print(f"Error: Path {benchmark_path} does not exist.")
        sys.exit(1)

    # Check if it's a benchmark directory containing multiple repos
    is_benchmark_dir = (benchmark_path / "calculator").exists() or any(p.is_dir() and (p / "metadata.json").exists() for p in benchmark_path.iterdir())
    
    if is_benchmark_dir:
        print(f"Scanning benchmark directory: {benchmark_path}")
        repos = [p for p in benchmark_path.iterdir() if p.is_dir() and (p / "metadata.json").exists()]
        # Sort repos for deterministic output
        repos.sort()
        
        all_passed = True
        print(f"Found {len(repos)} repositories.")
        for repo in repos:
            print(f"--- Running tests for {repo.name} ---")
            res = run_repo_tests(repo)
            status_str = "\033[92mPASSED\033[0m" if res["passed"] else "\033[91mFAILED\033[0m"
            print(f"Result for {repo.name}: {status_str}")
            if not res["passed"]:
                all_passed = False
                print(f"Error Message:\n{res['message'][:500]}")
        
        sys.exit(0 if all_passed else 1)
    else:
        # Single repo
        print(f"Running tests for single repository: {benchmark_path.name}")
        res = run_repo_tests(benchmark_path)
        print(f"Result: {'PASSED' if res['passed'] else 'FAILED'}")
        if not res["passed"]:
            print(f"Message:\n{res['message']}")
            sys.exit(1)
        sys.exit(0)

if __name__ == "__main__":
    main()
