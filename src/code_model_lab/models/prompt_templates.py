# Prompt templates for different tasks and model variants

ALGORITHMIC_DIRECT = """You are an expert software engineer. Solve the following programming problem in Python.
Respond ONLY with a single valid Python code block enclosed in ```python and ```. Do not write any explanations.

Problem:
{problem}

Starter Code:
{starter_code}
"""

ALGORITHMIC_STRUCTURED = """You are an expert software engineer. Solve the following programming problem in Python.
You must follow this exact output structure:

Approach:
<Write a brief explanation of your algorithmic approach here>

Edge cases:
<List edge cases you are handling>

Code:
```python
<Write your Python code here>
```

Complexity:
Time: <Time complexity, e.g. O(N)>
Space: <Space complexity, e.g. O(1)>

Problem:
{problem}

Constraints:
{constraints}

Starter Code:
{starter_code}
"""

DEBUG_PROMPT = """You are an expert software engineer. We have a Python solution that fails tests.
Please diagnose the issue and provide a corrected solution.

Problem:
{problem}

Attempted Code:
{attempt_code}

Test Failure/Output:
{test_output}

You must follow this exact output structure:

Diagnosis:
<Briefly explain why the code failed>

Fix:
<Briefly explain how you are fixing it>

Corrected code:
```python
<Write your corrected Python code here>
```
"""

REPO_REPAIR_LOCALIZE = """You are an expert software engineer. You are investigating a bug report for a codebase.
Analyze the issue description and repository layout, then rank the most likely files and classes/functions that contain the bug.

Issue:
{issue}

Files in Repo:
{file_list}

Respond with a JSON object in the following format:
{{
  "likely_files": [
    {{
      "path": "path/to/file.py",
      "reason": "Explain why this file is likely to contain the bug"
    }}
  ],
  "likely_symbols": ["function_or_class_name"]
}}
"""

REPO_REPAIR_PATCH = """You are an expert software engineer. Generate a minimal unified diff patch to fix the issue.
Only edit the files necessary. Do not rewrite large chunks of code.

Issue:
{issue}

Relevant Context:
{context}

Respond ONLY with a unified diff patch enclosed in ```diff and ```.
"""
