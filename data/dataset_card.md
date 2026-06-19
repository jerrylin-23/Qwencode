# Dataset Card: 7B Coding LLM Improvement Lab Dataset

## Dataset Summary
This dataset contains high-quality Python programming problems, debug trajectories, and repository repair examples designed for training and evaluating local 7B-parameter coding models. The focus is on programmatic generation to prevent copyright contamination and ensure high test coverage.

## Dataset Structure
The dataset splits are organized as:
- **Train Split (`data/processed/sft_train.jsonl`)**: 1,203 samples.
- **Validation Split (`data/processed/sft_valid.jsonl`)**: 150 samples.
- **Held-out Test Split (`data/processed/sft_test_heldout.jsonl`)**: 151 samples.

Each sample contains a clear `instruction` / `prompt` asking the model to solve or correct a code snippet, alongside a structured `response` explaining the approach, handling edge cases, and providing clean code blocks.

## Content Mixtures
- **Algorithmic Solutions**: 45% of the primary mixture. Focuses on core structures (two pointers, arrays, sliding windows).
- **Debugging Trajectories**: 20% of the primary mixture. Synthesizes a failed test, diagnosis of the logical bug, and a corrected code patch.
- **Edge-case Explanations**: 15% of the mixture. Focuses on identifying and documenting input limits, empty arrays, null pointer safety, and overflow cases.
- **Wrong-solution Critique**: 10% of the mixture. Identifies logic flaws in common buggy implementations.
- **Practical library/API tasks**: 10% of the mixture. Includes tasks using common python libraries (e.g. pandas data aggregation).

## Contamination and Leakage Controls
To ensure credible results:
1. No LeetCode problems or standard benchmarks (HumanEval, MBPP) were included in the synthetic generator templates.
2. Deduplication is performed based on problem descriptions prior to training/validation splits.
3. Problem IDs are tracked to guarantee that no variants of a problem present in the validation or held-out test splits appear in the training dataset.

## Licensing
This dataset is published under the permissive **MIT License**. All generated tasks are synthetic.
