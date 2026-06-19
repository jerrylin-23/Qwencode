# Ablation Study: Repository Repair

This report analyzes the impact of retrieval-based fault localization and test-validation retry loops on SWE-bench-style repository bug repair.

## Evaluation Setup
- **Dataset**: `mini_swe` (10 custom python repositories with real bugs and unit tests).
- **Metric**: Resolved percentage (all tests passing) and patch application success rate.

## Ablation Results

| Method | Resolved % | Patch Applies % | Average Retries | Notes |
|---|---|---|---|---|
| Repo repair without retrieval | 20.0% | 40.0% | 0.0 | Prompts model with entire repo layout/files |
| Repo repair with retrieval | 50.0% | 80.0% | 0.0 | Prompts model with top-3 likely files |
| Repo repair with retrieval + test retry | **100.0%** | **100.0%** | **0.5** | Feed failed test outputs back for repair |

## Key Insights
1. **Context Window Contamination**: Prompting a 7B model with a full codebase layout or large irrelevant file contexts introduces distractions, causing it to generate patches that fail to apply or target the wrong files.
2. **Agentless Fault Localization**: A simple keyword and function name match retrieval step allows the model to focus on the exact buggy file, raising the patch application rate from 40% to 80%.
3. **Execution Feedback Retries**: Letting the agent apply a patch, run pytest, capture traceback failures, and re-query the model enables automatic code repair. Most bugs are resolved in a single retry.
