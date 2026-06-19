# Handoff Plan: 7B Coding LLM Improvement Lab

## Mission

Build a research-inspired local project that improves a lower-cost open-weight coding model for two targets:

1. **LeetCode-style algorithmic coding**: solve standalone programming problems with hidden tests, edge-case reasoning, and code repair after failures.
2. **SWE-bench-style repository repair**: read an issue, localize relevant files/functions, generate a minimal patch, run tests, and retry from failure logs.

The project should be implemented as a polished, reproducible ML/SWE portfolio project. It should not train a frontier model from scratch. It should improve a 7B-ish model through data quality, targeted LoRA/QLoRA fine-tuning, execution feedback, retrieval, and a simple patch-validation agent.

Primary model recommendation:

- `Qwen/Qwen2.5-Coder-7B-Instruct` for inference and agent testing.
- `Qwen/Qwen2.5-Coder-7B` or compatible instruct checkpoint for fine-tuning experiments.

Optional baseline:

- `deepseek-ai/deepseek-coder-6.7b-instruct`.

Local hardware assumption:

- 16GB Apple Silicon Mac for inference, dataset processing, small evals, and demo.
- Cloud GPU/Kaggle/Colab for LoRA/QLoRA training when needed.

Do not implement everything at once. Build this as a staged project with clean milestones, measurable results, and ablation studies.

---

## Research Inspirations To Encode In The Project

Use these papers as design inspiration in the README/report, but implement a practical smaller version.

1. **Qwen2.5-Coder Technical Report**
   - Key ideas: code-specific continued pretraining, heavy data cleaning, scalable synthetic data generation, balanced data mixing across coding/reasoning/math.
   - URL: https://arxiv.org/abs/2409.12186

2. **Magicoder / OSS-Instruct**
   - Key idea: generate synthetic instruction data grounded in real open-source code snippets instead of purely generic LLM-generated tasks.
   - URL: https://arxiv.org/abs/2312.02120

3. **CodeRL**
   - Key idea: use execution/unit-test feedback to improve program synthesis instead of only doing supervised learning from final answers.
   - URL: https://arxiv.org/abs/2207.01780

4. **SWE-bench**
   - Key idea: evaluate models on real GitHub issue resolution requiring repo understanding, multi-file edits, and execution environments.
   - URL: https://arxiv.org/abs/2310.06770

5. **Agentless**
   - Key idea: a simple localization → repair → patch validation pipeline can be competitive with complex autonomous agents.
   - URL: https://arxiv.org/abs/2407.01489

6. **BigCodeBench**
   - Key idea: practical coding evaluation should test library/API usage and complex instructions, not only short algorithm puzzles.
   - URL: https://arxiv.org/abs/2406.15877

The project thesis should be:

> A small coding LLM becomes much more useful when combined with curated coding data, execution-guided repair trajectories, retrieval-based repo localization, and patch validation. The goal is not only to improve the model weights, but also to improve the full coding system around the model.

---

## Expected Final Deliverables

The final repository should contain:

1. A reproducible evaluation harness for algorithmic coding tasks.
2. A mini SWE-bench-style repository repair benchmark.
3. A curated JSONL dataset format for algorithmic, debugging, and repo-repair examples.
4. Scripts to generate synthetic tasks and hidden tests.
5. LoRA/QLoRA fine-tuning scripts or documented training commands.
6. A local inference wrapper using Ollama, llama.cpp, or MLX.
7. A simple repair agent with retrieval, patch generation, test execution, and retry logic.
8. Baseline vs improved model evaluation results.
9. Ablation study reports.
10. A polished README and technical report.
11. Optional demo CLI or small web UI.

---

## Recommended Project Structure

Create the following structure:

```text
.
├── README.md
├── pyproject.toml
├── .env.example
├── .gitignore
├── data/
│   ├── raw/
│   ├── processed/
│   ├── synthetic/
│   ├── eval/
│   └── dataset_card.md
├── configs/
│   ├── model.yaml
│   ├── training_lora.yaml
│   ├── eval_algorithms.yaml
│   └── eval_repo_repair.yaml
├── src/
│   └── code_model_lab/
│       ├── __init__.py
│       ├── models/
│       │   ├── ollama_client.py
│       │   ├── hf_client.py
│       │   └── prompt_templates.py
│       ├── data/
│       │   ├── schemas.py
│       │   ├── clean_dataset.py
│       │   ├── validate_jsonl.py
│       │   ├── generate_algorithm_tasks.py
│       │   ├── generate_hidden_tests.py
│       │   └── generate_debug_trajectories.py
│       ├── eval/
│       │   ├── run_algorithm_eval.py
│       │   ├── run_mbpp_eval.py
│       │   ├── run_humaneval_eval.py
│       │   ├── run_bigcodebench_subset.py
│       │   ├── metrics.py
│       │   └── sandbox.py
│       ├── repo_repair/
│       │   ├── index_repo.py
│       │   ├── retrieve_context.py
│       │   ├── localize_issue.py
│       │   ├── generate_patch.py
│       │   ├── apply_patch.py
│       │   ├── run_tests.py
│       │   └── repair_loop.py
│       ├── training/
│       │   ├── prepare_sft_dataset.py
│       │   ├── train_lora.py
│       │   ├── merge_adapter.py
│       │   └── export_gguf.md
│       └── reporting/
│           ├── make_tables.py
│           └── make_ablation_report.py
├── benchmarks/
│   ├── algorithmic_private/
│   ├── mini_swe/
│   └── README.md
├── scripts/
│   ├── setup.sh
│   ├── run_baseline.sh
│   ├── run_algorithm_eval.sh
│   ├── run_repo_repair_eval.sh
│   └── train_lora.sh
├── reports/
│   ├── baseline_results.md
│   ├── sft_results.md
│   ├── execution_feedback_results.md
│   ├── repo_repair_results.md
│   └── final_report.md
└── notebooks/
    ├── error_analysis.ipynb
    └── result_charts.ipynb
```

Use Python as the main implementation language. Keep scripts modular and small.

---

## Phase 1: Project Setup

### Goal

Create a clean Python project that can run local inference and automated code evaluation.

### Tasks

1. Initialize package structure.
2. Add `pyproject.toml` with dependencies.
3. Add `.env.example` for optional model endpoints.
4. Add `.gitignore` excluding model weights, datasets, caches, virtualenvs, and generated outputs.
5. Add README skeleton.
6. Add config files under `configs/`.

### Recommended dependencies

Use only what is needed at first:

```text
python>=3.10
pydantic
pyyaml
rich
tqdm
pandas
numpy
pytest
ruff
black
requests
GitPython
sentence-transformers or fastembed
faiss-cpu or sqlite-vss optional
transformers
peft
trl optional
accelerate
bitsandbytes only for Linux/cloud GPU, not Mac
mlx-lm optional for Apple Silicon experiments
```

### Local model options

Support at least one of these:

1. **Ollama** for simplest local inference:
   - `qwen2.5-coder:7b`
   - `deepseek-coder:6.7b`

2. **Hugging Face transformers** for training/eval on GPU.

3. **MLX-LM** optional for Apple Silicon inference/fine-tuning experiments.

### Acceptance criteria

- `python -m code_model_lab` or an equivalent CLI entrypoint works.
- `scripts/run_baseline.sh` can call the local model and print one generated solution.
- README documents setup for Mac and cloud GPU.

---

## Phase 2: Data Schemas

### Goal

Define strict schemas for all dataset examples so later training/eval does not become messy.

### Algorithmic problem schema

Create a Pydantic model equivalent to this JSONL shape:

```json
{
  "id": "algo_000001",
  "task_type": "algorithmic_problem",
  "source": "synthetic_or_open_dataset",
  "license": "permissive_or_internal",
  "difficulty": "medium",
  "tags": ["binary_search", "arrays"],
  "language": "python",
  "problem": "...",
  "constraints": "...",
  "starter_code": "...",
  "examples": [
    {
      "input": "...",
      "output": "...",
      "explanation": "..."
    }
  ],
  "hidden_tests": [
    {
      "input": "...",
      "expected_output": "..."
    }
  ],
  "reference_solution": "...",
  "explanation": "...",
  "complexity": {
    "time": "O(n log n)",
    "space": "O(n)"
  },
  "common_failures": [
    {
      "wrong_solution": "...",
      "failure_reason": "Fails on duplicates",
      "failing_test": "..."
    }
  ]
}
```

### Debug trajectory schema

```json
{
  "id": "debug_000001",
  "task_type": "debug_trajectory",
  "problem_id": "algo_000001",
  "language": "python",
  "problem": "...",
  "attempt_code": "...",
  "test_output": "...",
  "diagnosis": "...",
  "corrected_code": "...",
  "final_result": "pass"
}
```

### Repo repair schema

```json
{
  "id": "repo_000001",
  "task_type": "repo_repair",
  "repo_name": "mini_parser_bug",
  "language": "python",
  "issue": "...",
  "relevant_files": ["src/parser.py", "tests/test_parser.py"],
  "localized_symbols": ["parse_config"],
  "failing_test_output": "...",
  "patch_diff": "...",
  "test_command": "pytest",
  "final_test_result": "pass"
}
```

### Acceptance criteria

- JSONL validation script catches missing fields and malformed examples.
- Dataset card explains sources, licenses, contamination controls, and held-out splits.

---

## Phase 3: Algorithmic Evaluation Harness

### Goal

Measure baseline coding ability before any fine-tuning.

### Required features

1. Load tasks from JSONL.
2. Prompt the model using a consistent format.
3. Extract code from model output.
4. Run generated code in a sandboxed subprocess.
5. Apply visible and hidden tests.
6. Record compile/runtime/test failures.
7. Save per-task outputs to `reports/eval_runs/<timestamp>/`.
8. Compute metrics.

### Metrics

Track:

```text
pass@1
pass@3
compile rate
runtime error rate
hidden test pass rate
average retries
average latency
edge-case failure rate
```

### Safety and sandboxing

Implement conservative subprocess controls:

- Timeout per test.
- Temporary directory per run.
- No network access.
- Restricted imports when possible.
- Kill runaway processes.
- Capture stdout/stderr.

### Baseline eval targets

Start with:

1. 50 custom easy tasks.
2. 50 custom medium tasks.
3. 20 custom hard tasks.
4. HumanEval or HumanEval-style open benchmark if available.
5. MBPP or MBPP-style open benchmark if available.

Do not train on the evaluation split.

### Acceptance criteria

- `scripts/run_algorithm_eval.sh` generates a markdown report.
- Each failed task stores the model answer, traceback/test output, and expected result.

---

## Phase 4: Synthetic Algorithmic Dataset Generation

### Goal

Generate high-quality LeetCode-style data without scraping paid/copyrighted problem statements.

### Categories

Generate tasks across:

```text
arrays
hash maps
two pointers
sliding window
binary search
linked lists
stacks/queues
trees
graphs
heaps
greedy
dynamic programming
backtracking
intervals
strings
math/combinatorics
```

### Generation process

For each problem:

1. Generate a novel problem statement.
2. Generate constraints.
3. Generate examples.
4. Generate a reference solution.
5. Generate 10-30 hidden tests.
6. Run the reference solution against all tests.
7. Generate 1-3 plausible wrong solutions.
8. Run wrong solutions and keep only examples with real failing tests.
9. Store explanation and complexity.
10. Validate against schema.

### Quality filters

Reject tasks if:

- Reference solution does not pass tests.
- Hidden tests are too weak.
- Problem is a near-copy of a known benchmark item.
- Statement is ambiguous.
- Constraints are inconsistent.
- Expected output cannot be deterministically checked.

### Acceptance criteria

- At least 1,000 validated synthetic algorithmic tasks.
- At least 300 debugging trajectories.
- At least 100 held-out private eval tasks.
- Dataset card documents generation and filtering.

---

## Phase 5: Baseline Model Evaluation

### Goal

Measure the starting point for Qwen and optionally DeepSeek.

### Models to compare

1. `qwen2.5-coder:7b` via Ollama.
2. `deepseek-coder:6.7b` via Ollama if available.
3. Optional: `qwen2.5-coder:14b` if local memory allows or cloud inference is available.

### Prompting variants

Run each model under:

1. Direct answer prompt.
2. Structured prompt: approach → edge cases → code → complexity.
3. Debug-aware prompt with hidden-test retry loop.

### Output table

Create a report table like:

```text
Model | Prompt | pass@1 | pass@3 | compile rate | hidden test pass | avg retries | notes
```

### Acceptance criteria

- `reports/baseline_results.md` exists.
- It includes clear numbers and 5-10 qualitative failure examples.

---

## Phase 6: Supervised Fine-Tuning Dataset

### Goal

Prepare SFT data to make the model more reliable on algorithmic and debugging tasks.

### Training mixture v1

Use this starting mix:

```text
45% algorithmic final solutions
20% debugging trajectories
15% edge-case explanations
10% wrong-solution critique
10% practical library/API tasks
```

### Prompt/completion format

Use a chat format compatible with the base model. Keep output style consistent:

```text
Approach:
...

Edge cases:
...

Code:
```python
...
```

Complexity:
...
```

For debugging:

```text
Diagnosis:
...

Fix:
...

Corrected code:
```python
...
```
```

### Important training principle

Do not train the model to produce huge chain-of-thought. Use concise explanations and actionable reasoning. The output should be useful to a developer, not a long hidden reasoning trace.

### Acceptance criteria

- `data/processed/sft_train.jsonl`
- `data/processed/sft_valid.jsonl`
- `data/processed/sft_test_heldout.jsonl`
- Validation script confirms no schema errors.
- Splits prevent task leakage.

---

## Phase 7: LoRA/QLoRA Training

### Goal

Fine-tune the 7B coding model efficiently.

### Training approach

Preferred:

- LoRA/QLoRA with PEFT.
- Train on cloud GPU if local Mac is insufficient.
- Keep training reproducible with config files.

### Suggested initial hyperparameters

These are starting points, not guaranteed optimal:

```text
lora_r: 16 or 32
lora_alpha: 32 or 64
lora_dropout: 0.05
learning_rate: 2e-5 to 1e-4
epochs: 1-3
batch_size: hardware dependent
gradient_accumulation_steps: hardware dependent
max_seq_length: 4096 initially
optimizer: paged_adamw_8bit if supported
```

### Training checkpoints

Save:

```text
outputs/checkpoints/sft_v1/
outputs/adapters/sft_v1/
outputs/logs/sft_v1/
```

### Acceptance criteria

- Training script can run from config.
- Adapter is saved.
- Training loss curve is logged.
- Inference with adapter works on 5 sample prompts.

---

## Phase 8: Execution-Feedback Fine-Tuning

### Goal

Teach the model to repair failed code using real failure logs.

### Data creation process

1. Use baseline or SFT model to generate attempted solutions.
2. Run hidden tests.
3. Collect failures.
4. Create training examples:
   - problem
   - attempt
   - failing output
   - diagnosis
   - corrected solution
5. Keep only corrected solutions that pass tests.

### Example trajectory format

```text
Problem:
...

Attempt:
...

Test failure:
AssertionError on input ...
Expected ..., got ...

Diagnosis:
The code misses the duplicate-value edge case.

Corrected code:
...
```

### Acceptance criteria

- At least 500 real execution-feedback examples.
- Second adapter `execution_feedback_v1` trained or dataset prepared for training.
- Evaluation shows whether retry/debug performance improved.

---

## Phase 9: Mini SWE-Bench-Style Benchmark

### Goal

Create a smaller controlled benchmark for repository-level software repair.

### Benchmark design

Create 10-30 small Python repositories under `benchmarks/mini_swe/`. Each should include:

```text
repo/
├── pyproject.toml or requirements.txt
├── src/
├── tests/
├── ISSUE.md
├── expected_patch.diff
└── metadata.json
```

### Bug categories

Include:

```text
off-by-one errors
bad type conversion
missing None handling
wrong config parsing
incorrect path handling
bad API response parsing
broken validation logic
wrong exception type
incorrect date/time handling
regression from renamed function
multi-file import mismatch
```

### Each benchmark instance should include

- Issue description.
- Failing test command.
- Expected patch.
- Relevant files.
- Hidden tests if possible.
- Difficulty label.

### Acceptance criteria

- At least 10 benchmark repos initially.
- Each repo has a failing test before patch and passing tests after expected patch.
- `scripts/run_repo_repair_eval.sh` can run the benchmark.

---

## Phase 10: Repository Retrieval and Localization

### Goal

Implement an Agentless-inspired pipeline: localization → repair → validation.

### Retrieval process

1. Read issue text.
2. Index repository files.
3. Chunk source files by function/class where possible.
4. Embed chunks or use lexical search.
5. Retrieve top-k files/functions.
6. Ask model to rank likely fault locations.
7. Pass only relevant context into patch-generation prompt.

### Keep it simple initially

Start with lexical BM25 or simple keyword matching. Add embeddings later if needed.

### Output format

Localization output should be structured:

```json
{
  "likely_files": [
    {
      "path": "src/parser.py",
      "reason": "Issue mentions config parsing and this file contains parse_config."
    }
  ],
  "likely_symbols": ["parse_config"]
}
```

### Acceptance criteria

- Localization report saved per issue.
- Top-3 file recall measured against expected relevant files.
- Failure examples included in report.

---

## Phase 11: Patch Generation and Validation Loop

### Goal

Generate minimal patches and validate them by running tests.

### Repair loop

Implement this flow:

```text
Input issue
→ retrieve context
→ localize likely files/functions
→ ask model for unified diff
→ apply patch to temp copy
→ run tests
→ if fail, summarize failure and retry up to N times
→ save final patch and result
```

### Patch constraints

Prompt the model to:

- Produce a unified diff only.
- Edit the fewest files necessary.
- Avoid broad rewrites.
- Preserve public interfaces unless the issue requires changing them.
- Do not change tests unless explicitly allowed for a benchmark mode.

### Metrics

Track:

```text
resolved percentage
patch applies percentage
test pass percentage
files edited per patch
average retries
localization top-1/top-3 accuracy
unnecessary edit rate
```

### Acceptance criteria

- Repair loop runs on mini-SWE benchmark.
- Report compares no-retrieval vs retrieval vs retrieval+retry.
- At least a few benchmark issues are solved end-to-end.

---

## Phase 12: BigCodeBench-Style Practical Coding Subset

### Goal

Avoid making the project only about toy algorithms.

### Task types

Add tasks requiring:

```text
pandas transformations
JSON parsing
CSV processing
regex/text cleaning
filesystem manipulation
API response normalization
basic plotting/data aggregation
```

### Evaluation

Use unit tests that check real outputs. Avoid network calls. Mock data should be local.

### Acceptance criteria

- At least 50 practical library/API tasks.
- Results reported separately from pure algorithms.

---

## Phase 13: Ablation Studies

### Goal

Make the final project look research-driven and credible.

Run these comparisons:

```text
Base model, direct prompt
Base model, structured prompt
Base model, structured prompt + retry loop
SFT model, no retry
SFT model + retry loop
SFT model + execution-feedback adapter
Repo repair without retrieval
Repo repair with retrieval
Repo repair with retrieval + test retry loop
```

### Reports

Create:

```text
reports/ablation_algorithmic.md
reports/ablation_repo_repair.md
reports/error_analysis.md
```

Each report should include:

- Metrics table.
- 5 representative wins.
- 5 representative failures.
- Interpretation of what helped and what did not.

### Acceptance criteria

- The final report does not just claim improvement; it shows which component caused the improvement.

---

## Phase 14: Final README and Report

### README should include

1. Project overview.
2. Research motivation.
3. Model choices.
4. Dataset design.
5. Training approach.
6. Evaluation approach.
7. Results table.
8. Demo instructions.
9. Limitations.
10. Future work.

### Final report outline

```text
1. Abstract
2. Motivation
3. Related Work
4. Base Models
5. Dataset Construction
6. Training Method
7. Execution-Guided Repair
8. Repository Repair Agent
9. Evaluation Setup
10. Results
11. Ablations
12. Error Analysis
13. Limitations
14. Future Work
```

### Resume-friendly final project title

Use one of:

```text
Execution-Guided Fine-Tuning of a 7B Coding LLM
Small Coding LLM Repair Lab
LeetCode + SWE-Bench Inspired Coding Model Improvement
Qwen2.5-Coder Fine-Tuning and Repository Repair Agent
```

---

## Phase 15: Resume Bullets To Support

The implementation should generate enough evidence to honestly support bullets like:

```text
Fine-tuned a 7B open-source coding LLM with LoRA/QLoRA on curated algorithmic, debugging, and repository-repair datasets, improving pass@1 on a held-out LeetCode-style benchmark versus the base model.
```

```text
Built an execution-guided evaluation harness that generated code, ran hidden unit tests, captured compiler/runtime failures, and fed structured feedback into a self-repair loop.
```

```text
Designed a SWE-bench-inspired repair agent with retrieval-based fault localization, patch generation, test execution, and retry logic for multi-file Python repositories.
```

```text
Ran ablation studies comparing baseline prompting, supervised fine-tuning, execution-feedback tuning, and agentic test-repair loops across algorithmic and repository-level coding tasks.
```

Only include numeric improvements on the resume after real evaluation is complete.

---

## Implementation Order For Local Codex Agent

Follow this order strictly:

1. Create project skeleton and README.
2. Add configs and dataset schemas.
3. Implement JSONL validation.
4. Implement Ollama model client.
5. Implement one algorithmic eval runner.
6. Add 10 sample algorithmic tasks manually or synthetically.
7. Run baseline eval and save report.
8. Implement hidden-test generation utilities.
9. Generate a larger synthetic algorithmic dataset.
10. Implement debug trajectory generation.
11. Prepare SFT JSONL.
12. Add LoRA training scripts, but do not require local training to pass setup.
13. Build mini-SWE benchmark with 3 repos first.
14. Implement retrieval/localization.
15. Implement patch generation and patch application.
16. Implement test-validation retry loop.
17. Expand mini-SWE to 10+ repos.
18. Add ablation scripts.
19. Add report generation.
20. Polish README and final report.

At every step, keep the project runnable. Do not leave the repo in a broken state.

---

## Verification Commands

Add these commands to README and ensure they work:

```bash
python -m pip install -e .
python -m code_model_lab.data.validate_jsonl data/processed/sample_algorithmic.jsonl
python -m code_model_lab.eval.run_algorithm_eval --config configs/eval_algorithms.yaml
python -m code_model_lab.repo_repair.run_tests --benchmark benchmarks/mini_swe
python -m code_model_lab.repo_repair.repair_loop --config configs/eval_repo_repair.yaml
pytest
ruff check .
```

Optional training command:

```bash
python -m code_model_lab.training.train_lora --config configs/training_lora.yaml
```

---

## Edge Cases To Handle

### Algorithmic eval

- Model outputs prose but no code block.
- Model outputs multiple code blocks.
- Code times out.
- Code reads stdin when harness expects function call.
- Code prints when harness expects return value.
- Runtime exception.
- Non-deterministic output.
- Floating point tolerance.
- Multiple valid outputs.

### Dataset generation

- Duplicate tasks.
- Broken tests.
- Reference solution fails hidden tests.
- Wrong solution accidentally passes.
- Problem statement inconsistent with tests.
- Training/eval leakage.

### Repo repair

- Patch does not apply.
- Patch edits tests instead of source.
- Patch modifies too many files.
- Test command fails due environment setup.
- Model hallucinates nonexistent files.
- Retrieved context misses the real file.
- Retry loop repeats same failed patch.

---

## Non-Goals

Do not attempt these in the first version:

- Full pretraining.
- Training a model from scratch.
- Massive SWE-bench full evaluation before mini benchmark works.
- Complex autonomous browsing agent.
- Unbounded shell access agent.
- Production deployment.
- Claims of improvement without held-out evaluation.

---

## Definition Of Done

The project is complete when:

1. A user can run local inference with a 7B model.
2. A baseline algorithmic evaluation report exists.
3. A curated dataset and dataset card exist.
4. At least one fine-tuning-ready JSONL dataset exists.
5. A LoRA training script/config exists, even if training is run on cloud.
6. A mini-SWE benchmark exists with multiple reproducible bugs.
7. The repair loop can generate, apply, test, and retry patches.
8. Final reports show baseline vs improved/agentic results.
9. README explains setup, methods, results, and limitations.

---

## Suggested First Commit

The first commit should only include:

- Project skeleton.
- README with mission and research inspirations.
- Dataset schemas.
- Config stubs.
- Basic Ollama client.
- A tiny 5-task algorithmic eval sample.
- Validation command instructions.

Do not start with training. Start with measurement.
