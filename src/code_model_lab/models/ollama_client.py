import os
import re
import json
import requests


class GenerationError(RuntimeError):
    """Raised when a real-mode generation request fails.

    We deliberately do NOT silently fall back to mock output in real mode: a
    mock response masquerading as a model answer fabricates evaluation data
    (fake passes or fake failures). Callers should record an explicit error.
    """


class OllamaClient:
    def __init__(self, model_name: str = "qwen2.5-coder:7b",
                 api_base: str = "http://localhost:11434/api",
                 eval_mode: str = "mock", timeout: float = 300.0,
                 keep_alive: str = "10m"):
        self.model_name = model_name
        self.api_base = api_base
        self.eval_mode = os.getenv("EVAL_MODE", eval_mode)
        self.timeout = float(os.getenv("OLLAMA_TIMEOUT", timeout))
        self.keep_alive = keep_alive
        # Opt-in only: never silently fabricate data in a real eval.
        self.allow_mock_fallback = os.getenv("ALLOW_MOCK_FALLBACK", "0") == "1"

    def generate(self, prompt: str, temperature: float = 0.0, max_tokens: int = 2048) -> str:
        if self.eval_mode == "mock":
            return self._mock_generate(prompt)

        # Check if we are using an OpenAI-compatible cloud provider or local Ollama
        is_openai = "openai" in self.api_base or "deepinfra" in self.api_base or "together" in self.api_base or "openrouter" in self.api_base
        
        headers = {}
        token = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY")
        if token:
            headers["Authorization"] = f"Bearer {token}"

        if is_openai:
            url = f"{self.api_base.rstrip('/')}/chat/completions"
            payload = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        else:
            url = f"{self.api_base.rstrip('/')}/generate"
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "keep_alive": self.keep_alive,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            res_json = response.json()
            if is_openai:
                return res_json.get("choices", [{}])[0].get("message", {}).get("content", "")
            else:
                return res_json.get("response", "")
        except Exception as e:
            if self.allow_mock_fallback:
                print(f"Ollama request failed ({e}). ALLOW_MOCK_FALLBACK=1 -> mock response.")
                return self._mock_generate(prompt)
            # Do not fabricate eval data: surface the failure to the caller.
            raise GenerationError(f"Ollama request to {url} failed: {e}") from e

    def _mock_generate(self, prompt: str) -> str:
        # Mock logic to return valid responses for the evaluation and repair tasks
        prompt_lower = prompt.lower()
        
        # 1. Repo Repair Localization
        if "likely_files" in prompt_lower or "json object in the following format" in prompt_lower:
            # Check which benchmark repo is likely
            if "calculator" in prompt_lower:
                return json.dumps({
                    "likely_files": [{"path": "src/calculator.py", "reason": "Issue mentions division by zero bug."}],
                    "likely_symbols": ["divide"]
                })
            elif "string_utils" in prompt_lower or "reverse" in prompt_lower:
                return json.dumps({
                    "likely_files": [{"path": "src/utils.py", "reason": "Issue mentions string reversal bug."}],
                    "likely_symbols": ["reverse_string"]
                })
            else:
                return json.dumps({
                    "likely_files": [{"path": "src/main.py", "reason": "Default file search fallback."}],
                    "likely_symbols": ["main"]
                })

        # 2. Repo Repair Patch Generation
        if "unified diff patch" in prompt_lower or "diff --git" in prompt:
            if "calculator" in prompt_lower:
                return """```diff
diff --git a/src/calculator.py b/src/calculator.py
index 1234567..89abcde 100644
--- a/src/calculator.py
+++ b/src/calculator.py
@@ -10,3 +10,5 @@ def divide(a, b):
-    return a / b
+    if b == 0:
+        raise ValueError("Cannot divide by zero")
+    return a / b
```"""
            elif "string_utils" in prompt_lower or "reverse" in prompt_lower:
                return """```diff
diff --git a/src/utils.py b/src/utils.py
index 1234567..89abcde 100644
--- a/src/utils.py
+++ b/src/utils.py
@@ -5,3 +5,3 @@ def reverse_string(s):
-    return s
+    return s[::-1]
```"""
            else:
                match = re.search(r"run_task_(\d+)", prompt)
                if match:
                    idx = match.group(1)
                    return f"""```diff
diff --git a/src/main.py b/src/main.py
index 1234567..89abcde 100644
--- a/src/main.py
+++ b/src/main.py
@@ -1,3 +1,3 @@
 def run_task_{idx}():
-    return False
+    return True
```"""
                return """```diff
diff --git a/src/main.py b/src/main.py
index 1234567..89abcde 100644
--- a/src/main.py
+++ b/src/main.py
@@ -1,2 +1,2 @@
 def main():
-    pass
+    return True
```"""

        # 3. Algorithmic Problem - Two Sum (Structured/Direct)
        if "two_sum" in prompt or "nums" in prompt:
            # Is it structured or direct?
            if "Approach:" in prompt or "Edge cases:" in prompt:
                # Return structured format
                return """Approach:
Use a hash map to map the value to its index. Check for complement in map.

Edge cases:
Checking for target - num being the same number (avoid using same element twice).

Code:
```python
def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        comp = target - num
        if comp in seen:
            return [seen[comp], i]
        seen[num] = i
    return []
```

Complexity:
Time: O(N)
Space: O(N)"""
            else:
                # Direct format
                return """```python
def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        comp = target - num
        if comp in seen:
            return [seen[comp], i]
        seen[num] = i
    return []
```"""

        # 4. Palindrome Checking
        if "palindrome" in prompt or "is_palindrome" in prompt:
            if "Approach:" in prompt or "Edge cases:" in prompt:
                return """Approach:
Clean the string of non-alphanumeric, and compare with reverse.

Edge cases:
Empty string, single character, non-alphanumeric punctuation.

Code:
```python
def is_palindrome(s):
    clean = [c.lower() for c in s if c.isalnum()]
    return clean == clean[::-1]
```

Complexity:
Time: O(N)
Space: O(N)"""
            else:
                return """```python
def is_palindrome(s):
    clean = [c.lower() for c in s if c.isalnum()]
    return clean == clean[::-1]
```"""

        # 5. Debugging / Corrected code
        if "attempted code" in prompt_lower or "corrected code" in prompt_lower:
            if "two_sum" in prompt or "nums" in prompt:
                return """Diagnosis:
The code was reusing the same element.

Fix:
Add the current element to the hash map only after checking for complement, or do it sequentially properly.

Corrected code:
```python
def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        comp = target - num
        if comp in seen:
            return [seen[comp], i]
        seen[num] = i
    return []
```"""
            elif "palindrome" in prompt:
                return """Diagnosis:
The code failed to strip non-alphanumeric characters.

Fix:
Lower and filter by isalnum first.

Corrected code:
```python
def is_palindrome(s):
    clean = [c.lower() for c in s if c.isalnum()]
    return clean == clean[::-1]
```"""

        # Generic fallback
        return """```python
def solve(*args, **kwargs):
    return True
```"""
