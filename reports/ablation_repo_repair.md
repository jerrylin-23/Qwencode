# Ablation Study: Repository Repair

Planned analysis of retrieval-based fault localization and test-validation retry
loops on SWE-bench-style repository bug repair using `mini_swe`.

> **Status: NOT YET RUN with a live model.** The repair loop has so far only
> been exercised in `EVAL_MODE=mock`, where the mock client returns canned
> patches — those numbers measure the *harness*, not the model, and are not
> reported here as results. The table below is the experiment design; all cells
> are pending a real run (`EVAL_MODE=real`).

## Evaluation Setup
- **Dataset:** `benchmarks/mini_swe` (10 Python repositories with logical bugs
  and pytest configs).
- **Metric:** resolved % (all tests pass after patch) and patch-apply %.

## Planned ablation (pending real run)
| Method | Resolved % | Patch Applies % | Notes |
|---|---|---|---|
| Repair without retrieval | _pending_ | _pending_ | Full repo layout in context |
| Repair with retrieval (top-3 files) | _pending_ | _pending_ | Agentless-style localization |
| Retrieval + test-feedback retry | _pending_ | _pending_ | Apply → run pytest → re-query |

## Hypotheses to test (not yet validated)
1. **Context contamination:** prompting a 7B model with a full codebase layout
   may produce patches that fail to apply or target the wrong file.
2. **Agentless localization:** keyword/function-name retrieval should let the
   model focus on the buggy file and raise patch-apply rate.
3. **Execution-feedback retries:** apply-test-re-query may resolve bugs that a
   single shot misses.

These are stated as hypotheses, not findings. Run the loop in real mode and
fill the table before drawing conclusions.
