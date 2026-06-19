# Project Report: Small Coding LLM Lab
**Title**: Execution-Guided Evaluation and Repair Tooling for 7B Coding LLMs

> **Status (2026-06-19):** Measurement and tooling complete; fine-tuning not yet
> run. This report states **only measured results**. Sections describing
> training outcomes are explicitly marked *pending* — no improvement numbers are
> claimed until an adapter is trained and evaluated on held-out data.

## Abstract
Open-weight 7B coding models are strong on canonical algorithmic problems but
can fail on instruction-sensitive, adversarially-phrased variants. We built a
reproducible lab around `Qwen2.5-Coder-7B`: a sandboxed execution-feedback
evaluation harness, a synthetic data generator spanning real algorithmic problem
families, an Agentless-inspired repository repair loop, and a QLoRA training
pipeline. Measuring the base model with live inference, we find canonical
problems saturate (92.9% pass@1, 100% with retry) and even textbook-hard
problems score 100% — so neither discriminates model ability. A purpose-built
**adversarial** eval (problems that mimic a famous neighbour but change one
requirement) drops the base model to **54.2% pass@1 / 70.8% with retry**,
establishing real headroom. Fine-tuning to close that gap is implemented but
**not yet run**; no training results are reported here.

## Dataset Construction
Synthetic algorithmic problems are generated from genuine **problem families**
(two-sum, Kadane, sliding-window, binary search, coin-change, sieve, etc.), each
with a real reference solution that *computes* hidden-test outputs — so tests are
correct by construction (verified: 1050/1050 references pass their own tests).
SFT data combines structured solution examples with execution-feedback
trajectories, with train/eval leakage controlled by (entrypoint, hidden-test)
signature. All items use strict Pydantic schemas.

## Evaluation Setup
1. **Algorithmic evaluation** — runs model solutions in a sandboxed subprocess
   against hidden tests, with an optional execution-feedback retry loop.
2. **Mini-SWE benchmark** — 10 Python repositories with logical bugs and pytest
   configs (currently exercised in mock mode; see *pending* note below).

## Measured Results (base model, live inference)
| Eval tier | tasks | pass@1 | + retry |
|---|---|---|---|
| Standard canonical | 28 | 92.9% | 100.0% |
| Textbook-hard | 14 | 100.0% | 100.0% |
| **Adversarial (traps)** | 24 | **54.2%** | **70.8%** |

See `reports/error_analysis.md` for the per-family breakdown and documented
failure modes (e.g. solving `climb_no_double2` as plain Fibonacci even after
retries).

## Pending (not yet run)
- **Fine-tuning results.** `notebooks/train_qlora.ipynb` trains a LoRA adapter
  and evaluates it against the adversarial set, but has not been run. No
  base-vs-fine-tuned numbers are claimed until then.
- **Real repository-repair results.** The repair loop has only been exercised in
  `EVAL_MODE=mock`. No real resolve-rate is claimed.
- **Practical / BigCodeBench-style results.** Mock only so far.

## Conclusion and Future Work
The measurement foundation is sound and honest: a real, diverse dataset; a
harness that no longer fabricates data on timeout; and a discriminating eval
with documented failure modes. The natural next step is running the QLoRA
notebook and the solutions-only vs +execution-feedback ablation, then extending
the adversarial set and the real (non-mock) repository-repair evaluation.
