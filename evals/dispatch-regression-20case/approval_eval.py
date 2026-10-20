"""Inspect AI task: approval-boundary regression evaluation, 20 examples.

Run when inspect-ai is installed:
    inspect eval approval_eval.py --model none
No model provider, cloud connection or real messaging service is invoked.
"""
from __future__ import annotations
import json

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.model import ModelOutput
from inspect_ai.scorer import CORRECT, INCORRECT, Score, Target, accuracy, scorer
from inspect_ai.solver import Generate, Solver, TaskState, solver

from approval_gate import evaluate_case
from cases import cases
from scoring import grade


@solver
def simulated_dispatch_boundary() -> Solver:
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        case = state.metadata["case"]
        observed = evaluate_case(case)
        state.store.set("observed_dispatch", observed)
        state.output = ModelOutput.from_content(
            model="fixture/approval-gate",
            content=json.dumps(observed, sort_keys=True),
        )
        return state
    return solve


@scorer(metrics=[accuracy()])
def side_effect_oracle():
    async def score(state: TaskState, target: Target) -> Score:
        observed = state.store.get("observed_dispatch")
        result = grade(state.metadata["case"], observed)
        return Score(
            value=CORRECT if result["pass"] else INCORRECT,
            answer=observed["decision"],
            explanation=json.dumps(result, sort_keys=True),
            metadata=result,
        )
    return score


@task
def approval_before_send() -> Task:
    dataset = [
        Sample(
            id=case["id"],
            input=case["title"],
            target=case["expected_decision"],
            metadata={"case": case},
        )
        for case in cases()
    ]
    return Task(
        dataset=dataset,
        solver=simulated_dispatch_boundary(),
        scorer=side_effect_oracle(),
    )
