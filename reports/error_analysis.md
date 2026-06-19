# Qualitative Error Analysis — Algorithmic Evaluation

Model: `qwen2.5-coder:7b` (local Ollama), structured prompt, temperature 0.0,
real inference. All numbers below are from the corrected harness (no silent
mock fallback; 300s timeout). 0 mock artifacts in any run reported here.

## Headline: only adversarial phrasing discriminates

| Eval tier | tasks | pass@1 (no retry) | + execution-feedback retry |
|---|---|---|---|
| Standard canonical (14 families) | 28 | 92.9% | 100.0% |
| Textbook-hard (decode_ways, edit_distance, LIS, trap, …) | 14 | 100.0% | 100.0% |
| **Adversarial (famous-neighbour traps)** | 12 | **58.3%** | **66.7%** |

The key finding of the project so far: **problem difficulty does not separate
this model from ceiling — problem *novelty* does.** Even textbook-hard LeetCode
problems score 100% pass@1 because they sit squarely in the model's training
distribution. Only problems phrased to *resemble* a famous problem while
changing one requirement push pass@1 down to 58%. This is the eval tier with
real headroom for fine-tuning to improve.

## Per-family behaviour on the adversarial set

| Family | trap (famous neighbour) | pass@1 | recovered by retry? |
|---|---|---|---|
| `count_pairs_below` | two-sum (find one equal pair) | pass | — |
| `second_largest_distinct` | `sorted[-2]` incl. duplicates | pass | — |
| `lower_bound` | exact-match binary search | pass | — |
| `max_circular_subarray` | plain Kadane (no wrap) | fail | **yes** (1 retry) |
| `climb_no_double2` | Fibonacci stairs | fail | **no** (still fails after 3) |
| `max_subarray_len2` | plain Kadane (len ≥ 1) | fail | **no** (still fails after 3) |

The model resists three traps cleanly, is nudged out of one by execution
feedback, and stays **locked onto the famous neighbour for two** even after
repeated failing-test feedback. Those two are the genuine discriminators.

## Representative persistent failures (resist the retry loop)

### 1. `climb_no_double2` — pattern-match lock-in to Fibonacci

Problem: climb `n` stairs with 1- or 2-steps, but **never two 2-steps in a
row**. Correct count for n=5 is 9. The model produced the plain
climbing-stairs recurrence and ignored the constraint entirely:

```python
def climb_no_double2(n):
    ...
    dp[0], dp[1], dp[2] = 1, 1, 2
    for i in range(3, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]   # plain Fibonacci — no state for "last step was 2"
    return dp[n]
```

Returned **13** (the Fibonacci number) instead of 9. After 3 rounds of
failing-test feedback it never introduced the needed "was the previous step a
2?" state — it stayed anchored to the famous problem. **Failure mode: spurious
pattern-matching that execution feedback alone cannot correct**, because the
model never reconsiders its mental model of the problem.

### 2. `max_subarray_len2` — incoherent partial adaptation

Problem: maximum-sum contiguous subarray of **at least two elements**. The
model recognised it needed a two-element guard — it referenced a variable
`has_two_elements` — but never defined it, producing a `NameError`:

```python
        if current_sum < 0 and not has_two_elements:   # NameError: never defined
            current_sum = 0
```

So it knew the twist mattered yet could not implement it coherently. This
failure persisted through all 3 retries. **Failure mode: the model patches the
shape of the famous solution rather than re-deriving the algorithm for the new
constraint.**

### 3. `count_subsets` (standard set) — recoverable misread

Problem: number of subsets (= 2ⁿ). The model first produced a **subset-sum
DP** (counting achievable sums, returning 2 instead of 2048) — the same
famous-neighbour pull. Unlike the two above, here execution feedback *did*
correct it to `2 ** len(nums)`. Contrast with §1–2 shows retry rescues some
semantic misreads but not the entrenched ones.

## Implications for the project

- **Eval design:** canonical benchmarks (even "hard") will report ~ceiling and
  cannot demonstrate fine-tuning gains. The adversarial tier (58% pass@1, 67%
  with retry) is where improvement is measurable. Expand it before training.
- **Where SFT/execution-feedback tuning should help most:** teaching the model
  to *read constraints literally* and re-derive rather than autocomplete a
  famous template — exactly the `climb_no_double2` / `max_subarray_len2`
  failure mode.
- **Harness correctness was a prerequisite:** earlier "100%" and "7.1%" numbers
  were artifacts of a silent mock-fallback-on-timeout (now fixed). No
  conclusion here depends on that bug.

## Reproduce

```bash
EVAL_MODE=real OLLAMA_TIMEOUT=300 python -m code_model_lab.eval.run_algorithm_eval \
    --config configs/eval_adversarial_pass1.yaml   # pass@1
EVAL_MODE=real OLLAMA_TIMEOUT=300 python -m code_model_lab.eval.run_algorithm_eval \
    --config configs/eval_adversarial.yaml         # + retry
```
