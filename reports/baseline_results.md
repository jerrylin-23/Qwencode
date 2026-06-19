# Baseline Algorithmic Evaluation Results

**Model:** `qwen2.5-coder:7b` (local, via Ollama) · **Mode:** real (live inference)
**Eval set:** 28 tasks, 2 per family across all 14 problem families
(`data/processed/eval_baseline_30.jsonl`) · **Prompt:** structured
(approach → edge cases → code → complexity) · **Sampling:** temperature 0.0, pass@1.

## Headline numbers

| Configuration | pass | compile | avg retries | avg latency |
|---|---|---|---|---|
| pass@1, **no retry** | **92.9%** (26/28) | 100.0% | 0.00 | 29.7 s/task |
| structured + **execution-feedback retry** (≤3) | **100.0%** (28/28) | 100.0% | 0.11 | — |

The execution-feedback retry loop recovered **both** first-attempt failures,
lifting 92.9% → 100%. This is the project's core thesis in miniature: the system
around the model (run tests → feed the failure back → let it repair) closes a
real gap, not just a cosmetic one.

## Interpretation

- Qwen2.5-Coder-7B is **strong on canonical algorithmic problems**. The 14
  families here (two-sum, Kadane, sliding-window, binary search, valid-parens,
  coin-change, sieve, merge-intervals, kth-largest, …) are well within its
  first-attempt capability, so the *un-aided* ceiling is high.
- The discriminating signal is in **first-attempt correctness**, not the
  retry-assisted number. Reporting only the 100% retry figure would hide where
  the model actually slips.

## Representative failure (first attempt)

**Task `algo_000118` — `count_subsets`.** Problem: *"Return the number of
distinct subsets (including the empty set) of a list of distinct integers"*
(answer = 2ⁿ). The model instead generated a **subset-sum DP** — counting the
number of achievable subset *sums*:

```python
def count_subsets(nums):
    if not nums:
        return 1
    total_sum = sum(nums)
    dp = [False] * (total_sum + 1)
    dp[0] = True
    for num in nums:
        for j in range(total_sum, num - 1, -1):
            if dp[j]:
                dp[j + num] = True
    return sum(dp) + 1
```

It returned `2` instead of `2048`. This is a **semantic misread** — spurious
pattern-matching to the more famous "subset sum" problem from the word
"subsets". Both `count_subsets` instances in the eval failed this way. When the
failing test output was fed back, the model corrected to `2 ** len(nums)` and
passed. So execution feedback fixes *semantic* errors here, not just syntax.

## Limitations / what this baseline does NOT yet show

- Canonical problems leave little first-attempt headroom, so they cannot
  discriminate a fine-tuned model from the base model. To make the
  SFT/ablation story meaningful, the eval set needs **harder and more novel**
  problems (multi-step, less famous, adversarial phrasings like `count_subsets`).
- Single-sample pass@1 only; pass@k and latency variance not yet measured.
- 28 tasks is a smoke-scale baseline. Plan target is 50 easy / 50 medium /
  20 hard on a held-out private split.

## Reproduce

```bash
ollama pull qwen2.5-coder:7b
EVAL_MODE=real python -m code_model_lab.eval.run_algorithm_eval \
    --config configs/eval_baseline.yaml          # structured + retry
EVAL_MODE=real python -m code_model_lab.eval.run_algorithm_eval \
    --config configs/eval_baseline_pass1.yaml    # true pass@1, no retry
```
