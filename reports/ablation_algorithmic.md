# Ablation Study: Algorithmic Coding Tasks

Effect of prompting style and the execution-feedback retry loop for
`Qwen2.5-Coder-7B` on algorithmic coding.

> **Status:** Base-model rows are **measured** (live inference, fixed harness,
> 0 mock artifacts). SFT rows are **pending** — no adapter has been trained yet,
> so those cells are left blank rather than filled with invented numbers.

## Evaluation Setup
- **Datasets:** standard canonical (28 tasks, 14 families), textbook-hard
  (14 tasks), and adversarial traps (24 tasks). See `error_analysis.md`.
- **Metric:** pass@1 (all hidden tests pass). Sandbox: subprocess, 2.0s timeout.
- **Retry:** execution-feedback loop, ≤3 retries, failing test fed back.

## Measured: base model, by eval tier
| Configuration | Standard pass@1 | Hard pass@1 | Adversarial pass@1 |
|---|---|---|---|
| Base, structured prompt (no retry) | 92.9% | 100.0% | 54.2% |
| Base, structured + execution-feedback retry | 100.0% | 100.0% | 70.8% |

**Reading:** canonical and textbook-hard problems saturate and do not
discriminate. Only the adversarial tier has headroom, and execution feedback
recovers part of it (54.2% → 70.8%) but not all — two families
(`climb_no_double2`, `max_subarray_len2`) resist repair entirely.

## Pending: SFT ablation (run via notebooks/train_qlora.ipynb)
| Configuration | Adversarial pass@1 |
|---|---|
| Base (no fine-tune) | 54.2% (measured) |
| SFT, solutions only | _pending_ |
| SFT + execution-feedback trajectories | _pending_ |

Comparing the last two rows is the experiment that would isolate
execution-feedback fine-tuning as a cause of improvement. Until it is run, no
SFT result is claimed.

## Qualitative Findings (measured)
1. **Structured prompting** (Approach / Edge cases before code) is the default;
   we have not yet run a controlled direct-vs-structured comparison, so no
   delta is claimed for it.
2. **Execution-feedback retries** help on the adversarial tier (+16.6 points)
   but cannot fix entrenched pattern-matching: `climb_no_double2` is solved as
   plain Fibonacci even after three rounds of failing-test feedback.
