import json
from pathlib import Path

REPOS = {
    "calculator": {
        "files": {
            "src/calculator.py": """def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    return a / b
""",
            "tests/test_calculator.py": """import unittest
from src.calculator import divide, add

class TestCalculator(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)
        
    def test_divide_zero(self):
        with self.assertRaises(ValueError):
            divide(10, 0)
"""
        },
        "issue": "The divide function raises ZeroDivisionError when dividing by zero, but it should raise ValueError with 'Cannot divide by zero' message instead.",
        "expected_patch": """diff --git a/src/calculator.py b/src/calculator.py
index 1234567..89abcde 100644
--- a/src/calculator.py
+++ b/src/calculator.py
@@ -10,3 +10,5 @@ def divide(a, b):
-    return a / b
+    if b == 0:
+        raise ValueError("Cannot divide by zero")
+    return a / b
""",
        "metadata": {
            "name": "calculator",
            "test_command": "pytest tests/test_calculator.py",
            "relevant_files": ["src/calculator.py"],
            "localized_symbols": ["divide"]
        }
    },
    
    "string_utils": {
        "files": {
            "src/utils.py": """def uppercase_string(s):
    return s.upper()

def reverse_string(s):
    return s
""",
            "tests/test_utils.py": """import unittest
from src.utils import reverse_string

class TestUtils(unittest.TestCase):
    def test_reverse(self):
        self.assertEqual(reverse_string("hello"), "olleh")
"""
        },
        "issue": "The reverse_string function returns the original string unmodified. It needs to properly reverse it.",
        "expected_patch": """diff --git a/src/utils.py b/src/utils.py
index 1234567..89abcde 100644
--- a/src/utils.py
+++ b/src/utils.py
@@ -5,3 +5,3 @@ def reverse_string(s):
-    return s
+    return s[::-1]
""",
        "metadata": {
            "name": "string_utils",
            "test_command": "pytest tests/test_utils.py",
            "relevant_files": ["src/utils.py"],
            "localized_symbols": ["reverse_string"]
        }
    }
}

# Programmatically generate 8 more simple repos to reach 10 total as per criteria
for i in range(3, 11):
    repo_name = f"dummy_repo_{i}"
    REPOS[repo_name] = {
        "files": {
            "src/main.py": f"""def run_task_{i}():
    return False
""",
            "tests/test_main.py": f"""import unittest
from src.main import run_task_{i}

class TestMain(unittest.TestCase):
    def test_run(self):
        self.assertTrue(run_task_{i}())
"""
        },
        "issue": f"run_task_{i} should return True on success, but currently returns False.",
        "expected_patch": f"""diff --git a/src/main.py b/src/main.py
index 1234567..89abcde 100644
--- a/src/main.py
+++ b/src/main.py
@@ -1,2 +1,2 @@
 def run_task_{i}():
-    return False
+    return True
""",
        "metadata": {
            "name": repo_name,
            "test_command": "pytest tests/test_main.py",
            "relevant_files": ["src/main.py"],
            "localized_symbols": [f"run_task_{i}"]
        }
    }

def initialize_benchmark(dest_path: Path):
    dest_path.mkdir(parents=True, exist_ok=True)
    
    for repo_name, repo_data in REPOS.items():
        repo_dir = dest_path / repo_name
        repo_dir.mkdir(parents=True, exist_ok=True)
        
        # Write source/test files
        for rel_path, content in repo_data["files"].items():
            file_path = repo_dir / rel_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
                
        # Write ISSUE.md
        with open(repo_dir / "ISSUE.md", "w", encoding="utf-8") as f:
            f.write(repo_data["issue"])
            
        # Write expected_patch.diff
        with open(repo_dir / "expected_patch.diff", "w", encoding="utf-8") as f:
            f.write(repo_data["expected_patch"])
            
        # Write metadata.json
        with open(repo_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(repo_data["metadata"], f, indent=2)
            
    print(f"Initialized {len(REPOS)} mini-SWE repositories under {dest_path}.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dest", type=str, default="benchmarks/mini_swe")
    args = parser.parse_args()
    initialize_benchmark(Path(args.dest))
