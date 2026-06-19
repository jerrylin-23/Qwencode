# Qualitative Error Analysis

This report documents representative wins and common failure modes identified during evaluation runs.

## Representative Wins
1. **Division by Zero in Calculator**: The agent successfully localized the `divide` function in `src/calculator.py`, generated a clean unified diff adding a check `if b == 0: raise ValueError(...)`, applied the patch, and verified that pytest passed.
2. **String Reversal Logic**: The model correctly updated `reverse_string(s)` to `return s[::-1]`, replacing the dummy return statement and passing all unit tests.

## Common Failure Modes

### 1. Unified Diff Application Failures
- **Symptom**: The model occasionally generates patches with extra context lines or incorrect line offsets that do not match the local file contents exactly.
- **Remedy**: Improved patch application robustness using sliding-window search that ignores whitespace/indentation.

### 2. Multi-File Bug Dependency
- **Symptom**: When a bug requires modifying multiple files simultaneously (e.g., updating an import in `main.py` and renaming a function in `utils.py`), the model client struggles to generate a single unified diff encompassing both changes.
- **Remedy**: Break down multi-file repairs into sequential single-file edit steps.

### 3. Non-deterministic Outputs
- **Symptom**: Running the model with temperature > 0 can produce different structured formats (e.g., writing python code blocks without language tags or extra prose text).
- **Remedy**: Fix temperature = 0.0 and add strict system prompt guidelines.
