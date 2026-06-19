# Baseline Algorithmic Evaluation Results

Base `qwen2.5-coder:7b`, live inference (`EVAL_MODE=real`), structured prompt,
temperature 0.0. Canonical-tier baseline (28 tasks, 14 families).

| Model | Prompt | pass@1 | + retry | compile rate | notes |
|---|---|---|---|---|---|
| qwen2.5-coder:7b | structured | 92.9% | 100.0% | 100.0% | canonical tier, 28 tasks |

> Note: this file is auto-overwritten by `run_algorithm_eval` and will show the
> numbers of whichever config was last run. The canonical-tier baseline is
> 92.9% pass@1 (`configs/eval_baseline_pass1.yaml`). For the hard and adversarial
> tiers and full analysis, see [`error_analysis.md`](error_analysis.md).
