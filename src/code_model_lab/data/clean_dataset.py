"""Build SFT datasets from the verified problem families.

Two record types, both grounded in real reference solutions:

1. **Solution** examples: problem -> structured solution (Approach / Edge cases
   / Code / Complexity).
2. **Execution-feedback** trajectories (CodeRL-style): problem + a *wrong*
   attempt that pattern-matches a famous neighbour + the failing test ->
   diagnosis + corrected code. These target the failure mode found in
   evaluation (e.g. solving `climb_no_double2` as plain Fibonacci).

Leakage control: any generated instance whose (entrypoint, hidden-tests)
signature appears in an eval file is dropped, so train and eval never share
the exact same inputs. Train/eval still share *families* — results must be
read as in-family generalization to new inputs, which is exactly the claim we
want to test.
"""
import re
import json
import random
import argparse
from pathlib import Path

from code_model_lab.data.generate_algorithm_tasks import (
    FAMILIES, HARD_FAMILIES, ADVERSARIAL_FAMILIES, generate_task,
)

ALL_FAMILIES = FAMILIES + HARD_FAMILIES + ADVERSARIAL_FAMILIES


def _entrypoint(starter_code: str) -> str:
    m = re.search(r"def\s+(\w+)\(", starter_code)
    return m.group(1) if m else "solve"


def _signature(task: dict) -> str:
    """Identity of a task instance: entrypoint + its hidden-test inputs."""
    ep = _entrypoint(task["starter_code"])
    inputs = tuple(ht["input"] for ht in task["hidden_tests"])
    return f"{ep}::{inputs}"


def _edge_cases(task: dict) -> str:
    cf = task.get("common_failures") or []
    if cf:
        return f"- {cf[0]['failure_reason']}"
    return "- Empty or single-element input.\n- Boundary values at the constraint limits."


def solution_record(task: dict) -> dict:
    instruction = (
        f"Problem:\n{task['problem']}\n\n"
        f"Constraints:\n{task.get('constraints', '')}\n\n"
        f"Starter Code:\n{task['starter_code']}"
    )
    cx = task.get("complexity", {})
    response = (
        f"Approach:\n{task.get('explanation', '')}\n\n"
        f"Edge cases:\n{_edge_cases(task)}\n\n"
        f"Code:\n```python\n{task['reference_solution']}\n```\n\n"
        f"Complexity:\nTime: {cx.get('time', 'O(N)')}\nSpace: {cx.get('space', 'O(1)')}"
    )
    return {"instruction": instruction, "response": response, "kind": "solution",
            "family": _entrypoint(task["starter_code"])}


def feedback_record(task: dict) -> dict | None:
    """Build an execution-feedback trajectory from the family's known wrong
    solution, running it against a hidden test to get a real failure message."""
    cf = (task.get("common_failures") or [])
    if not cf:
        return None
    wrong = cf[0]["wrong_solution"]
    reason = cf[0]["failure_reason"]
    ep = _entrypoint(task["starter_code"])

    # Produce a concrete failing test line (expected vs got) from the wrong code.
    failure_line = cf[0].get("failing_test", "")
    try:
        wns, rns = {}, {}
        exec(wrong, wns)
        exec(task["reference_solution"], rns)
        wfn, rfn = wns[ep], rns[ep]
        for ht in task["hidden_tests"]:
            args = eval(ht["input"])
            got, exp = wfn(*args), rfn(*args)
            if got != exp:
                failure_line = f"Input {ht['input']}: expected {exp!r}, got {got!r}"
                break
    except Exception:
        pass

    instruction = (
        f"Problem:\n{task['problem']}\n\n"
        f"Attempted Code:\n```python\n{wrong}\n```\n\n"
        f"Test Failure:\n{failure_line}"
    )
    response = (
        f"Diagnosis:\n{reason}\n\n"
        f"Fix:\nRe-read the requirement literally and implement it directly "
        f"rather than reusing a similar well-known solution.\n\n"
        f"Corrected code:\n```python\n{task['reference_solution']}\n```"
    )
    return {"instruction": instruction, "response": response, "kind": "feedback",
            "family": ep}


def load_eval_signatures(paths) -> set:
    sigs = set()
    for p in paths:
        p = Path(p)
        if not p.exists():
            continue
        for line in p.open():
            if line.strip():
                sigs.add(_signature(json.loads(line)))
    return sigs


def main():
    ap = argparse.ArgumentParser(description="Build grounded SFT datasets.")
    ap.add_argument("--per_family", type=int, default=60,
                    help="Instances to generate per family before dedup/leakage filtering.")
    ap.add_argument("--output_dir", type=str, default="data/processed")
    ap.add_argument("--seed", type=int, default=2024)
    ap.add_argument("--eval_files", nargs="*", default=[
        "data/processed/eval_baseline_30.jsonl",
        "data/processed/eval_hard.jsonl",
        "data/processed/eval_adversarial.jsonl",
    ])
    args = ap.parse_args()

    rng = random.Random(args.seed)
    eval_sigs = load_eval_signatures(args.eval_files)

    # Generate a fresh, varied pool per family (different seed space than eval).
    tid = 0
    records, kept_sigs = [], set()
    leaked = 0
    for fam in ALL_FAMILIES:
        made = 0
        for _ in range(args.per_family * 3):  # oversample; dedup below
            if made >= args.per_family:
                break
            tid += 1
            task = generate_task(tid, fam, rng)
            sig = _signature(task)
            if sig in eval_sigs:
                leaked += 1
                continue
            if sig in kept_sigs:
                continue
            kept_sigs.add(sig)
            made += 1
            records.append(solution_record(task))
            fb = feedback_record(task)
            if fb:
                records.append(fb)

    rng.shuffle(records)
    n = len(records)
    tr, va = int(n * 0.8), int(n * 0.9)
    splits = [("sft_train", records[:tr]), ("sft_valid", records[tr:va]),
              ("sft_test_heldout", records[va:])]

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    for name, split in splits:
        with (out / f"{name}.jsonl").open("w", encoding="utf-8") as f:
            for r in split:
                f.write(json.dumps({"instruction": r["instruction"],
                                    "response": r["response"]}) + "\n")
        print(f"Saved {len(split)} -> {out / (name + '.jsonl')}")

    from collections import Counter
    kinds = Counter(r["kind"] for r in records)
    fams = Counter(r["family"] for r in records)
    print(f"\nTotal records: {n}  (dropped {leaked} eval-leaking instances)")
    print(f"By kind: {dict(kinds)}")
    print(f"Families: {len(fams)}  (min/max per family: "
          f"{min(fams.values())}/{max(fams.values())})")


if __name__ == "__main__":
    main()
