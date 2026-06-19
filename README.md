# Small Coding LLM Improvement Lab

A ML/SWE portfolio project focused on improving 7B-parameter open-weight coding models (e.g., `Qwen2.5-Coder-7B`) on algorithmic problem solving (LeetCode-style) and repository-level software repair (SWE-bench-style).

## Key Features

1. **Self-contained execution sandbox**: Safely runs generated code against unit tests, catching exceptions and compile errors in subprocesses.
2. **Synthetic Data Generation**: Algorithmic dataset generator built from genuine problem families (14 standard + 7 hard + 6 adversarial), each with a real reference solution that computes hidden-test outputs, plus execution-feedback failure trajectories.
3. **Agentless Repair Loop**: Simple context localization, patch generation, applying patch, running test, and automatic retry from failing logs.
4. **Fine-Tuning Utilities**: Scripts and configurations for training PEFT LoRA adapters.

## Installation & Setup

We recommend setting up a virtual environment in macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -e .
```

Ensure you have a `.env` file configured. Copy the template:
```bash
cp .env.example .env
```

To run without a live Ollama connection, you can set `EVAL_MODE=mock` in `.env` to execute tests and verify agent repair flow offline.

## Verification Commands
Use these commands to verify that all modules are working:

```bash
# 1. Install package in editable mode
python -m pip install -e .

# 2. Validate dataset format
python -m code_model_lab.data.validate_jsonl data/processed/sample_algorithmic.jsonl

# 3. Run algorithmic evaluation harness
python -m code_model_lab.eval.run_algorithm_eval --config configs/eval_algorithms.yaml

# 4. Run BigCodeBench-style practical library evaluation
python -m code_model_lab.eval.run_bigcodebench_subset --config configs/eval_algorithms.yaml

# 5. Run test suites on benchmarks/mini_swe repos
python -m code_model_lab.repo_repair.run_tests --benchmark benchmarks/mini_swe

# 6. Run the repository repair agent repair loop
python -m code_model_lab.repo_repair.repair_loop --config configs/eval_repo_repair.yaml

# 7. Run unit test suite
pytest

# 8. Lint and style checks
ruff check .
```

For LoRA fine-tuning training, run:
```bash
python -m code_model_lab.training.train_lora --config configs/training_lora.yaml
```

## Results Summary

Measured on the **base** `Qwen2.5-Coder-7B` with **live** local inference
(`EVAL_MODE=real`), structured prompt, temperature 0.0. Full breakdown and
documented failure modes in [`reports/error_analysis.md`](reports/error_analysis.md).

| Eval tier | tasks | pass@1 | + execution-feedback retry |
|---|---|---|---|
| Standard canonical (14 families) | 28 | 92.9% | 100.0% |
| Textbook-hard | 14 | 100.0% | 100.0% |
| **Adversarial (famous-neighbour traps)** | 24 | **54.2%** | **70.8%** |

**Takeaway:** canonical and even textbook-hard problems saturate; only
adversarially-phrased problems discriminate. That 54.2% is the headroom a
fine-tuned model would need to improve.

**Not yet run (no numbers claimed):** LoRA fine-tuning (pipeline in
[`notebooks/train_qlora.ipynb`](notebooks/train_qlora.ipynb)), real
(non-mock) repository repair, and practical/BigCodeBench evaluation. See the
*pending* sections in `reports/`.

## Project Structure

```text
.
├── pyproject.toml
├── README.md
├── .env
├── configs/
│   ├── model.yaml
│   ├── training_lora.yaml
│   ├── eval_algorithms.yaml
│   └── eval_repo_repair.yaml
├── data/
│   ├── processed/
│   │   ├── sample_algorithmic.jsonl
│   │   ├── sft_train.jsonl
│   │   ├── sft_valid.jsonl
│   │   └── sft_test_heldout.jsonl
│   └── dataset_card.md
├── src/
│   └── code_model_lab/
│       ├── data/
│       │   ├── schemas.py
│       │   ├── clean_dataset.py
│       │   ├── validate_jsonl.py
│       │   ├── generate_algorithm_tasks.py
│       │   ├── generate_hidden_tests.py
│       │   └── generate_debug_trajectories.py
│       ├── eval/
│       │   ├── run_algorithm_eval.py
│       │   └── sandbox.py
│       ├── repo_repair/
│       │   ├── index_repo.py
│       │   ├── retrieve_context.py
│       │   ├── localize_issue.py
│       │   ├── generate_patch.py
│       │   ├── apply_patch.py
│       │   ├── run_tests.py
│       │   └── repair_loop.py
│       └── training/
│           └── train_lora.py
└── benchmarks/
    └── mini_swe/
```

## Research Inspirations
- **Agentless**: Simplified localization, repair, and patch validation.
- **CodeRL**: Utilizing unit-test execution feedback to guide retry logic.
- **Magicoder**: Synthetic instructions grounded in real code semantics.

## License
MIT License
