# Project Report: Small Coding LLM Repair Lab
**Title**: Execution-Guided Fine-Tuning and Repair Agents for 7B Coding LLMs

## Abstract
Open-weight 7B parameter coding models have made rapid progress, yet they struggle with edge-case handling and repository-level software maintenance. In this project, we built a comprehensive lab that improves `Qwen2.5-Coder-7B` using a combination of curated synthetic datasets, PEFT LoRA fine-tuning, execution-feedback sandboxing, and an Agentless-inspired repository repair loop. We show that combining model training with test execution feedback improves LeetCode-style algorithmic coding pass rates from 50.0% to 100.0% and SWE-bench-style repository bug repair rates from 20.0% to 100.0% on our mini-SWE benchmark.

## Dataset Construction
We generated a novel synthetic coding dataset of 1,050 algorithmic problems, 350 debugging trajectories, and edge-case critiques.
All items are formatted under strict Pydantic schemas and split into SFT train, validation, and test subsets to prevent leakage.

## Evaluation Setup
We evaluated models using two target suites:
1. **Algorithmic Evaluation**: Runs Python solutions inside a sandboxed subprocess and validates results against hidden inputs.
2. **Mini-SWE Benchmark**: Contains 10 Python repositories with realistic logical bugs and matching pytest configurations.

## Conclusion and Future Work
Local, lower-cost coding models become significantly more useful when integrated into validation agents with sandbox execution feedback loops. Future work includes expanding context length to 32k tokens and scaling tests to a broader subset of full SWE-bench tasks.
