"""Decision extraction and TaskState-facing delegation scorer regressions."""

import asyncio
import sys
from pathlib import Path

import pytest
from inspect_ai import eval
from inspect_ai.model import ChatMessageAssistant, ModelName, ModelOutput, get_model
from inspect_ai.scorer import CORRECT, INCORRECT, Target
from inspect_ai.solver import TaskState
from inspect_ai.tool import ToolCall

sys.path.insert(0, str(Path(__file__).parent))

import delegation_eval
from delegation_eval import CASES, delegation_scorer, extract_decision, judge_decision


def _msg_with_tool_call(function: str):
    tc = ToolCall(id="call-1", function=function, arguments={"subtask": "x"}, type="function")
    return ChatMessageAssistant(content="delegating", tool_calls=[tc])


def _msg_text(text: str):
    return ChatMessageAssistant(content=text)


def _state(output="Finished the task myself.", *, should_delegate=False, messages=None):
    return TaskState(
        model=ModelName("mockllm/model"),
        sample_id="test-decision",
        epoch=1,
        input="Handle this task.",
        messages=messages or [_msg_text(output)],
        output=ModelOutput.from_content("mockllm/model", output),
        metadata={"should_delegate": should_delegate},
        completed=True,
    )


def _score(state, *, live=True):
    return asyncio.run(delegation_scorer(live=live)(state, Target("SOLO")))


def test_decision_line_delegate():
    assert extract_decision([_msg_text("DECISION: DELEGATE")], "DECISION: DELEGATE") is True


def test_decision_line_solo():
    assert extract_decision([_msg_text("x")], "DECISION: SOLO") is False


def test_mock_unparseable_returns_none():
    assert extract_decision([_msg_text("did stuff")], "did stuff") is None


def test_mock_requires_declaration_even_when_completed():
    assert extract_decision([], "Ordinary summary", completed=True) is None


def test_mock_requires_declaration_even_with_tool_call():
    assert extract_decision([_msg_with_tool_call("spawn_subagent")], "summary") is None


def test_live_tool_call_means_delegated():
    msgs = [_msg_with_tool_call("spawn_subagent")]
    assert extract_decision(msgs, "DECISION: SOLO", live=True, completed=True) is True


def test_live_other_tool_call_means_solo():
    msgs = [_msg_with_tool_call("read_file")]
    assert extract_decision(msgs, "DECISION: DELEGATE", live=True, completed=True) is False


def test_live_completed_without_tool_call_means_solo():
    assert extract_decision([], "Finished the fix.", live=True, completed=True) is False


def test_live_incomplete_without_tool_call_is_unknown():
    assert extract_decision([], "DECISION: SOLO", live=True) is None


def test_live_incomplete_with_tool_call_is_unknown():
    msgs = [_msg_with_tool_call("spawn_subagent")]
    assert extract_decision(msgs, "DECISION: DELEGATE", live=True) is None


def test_task_state_completed_live_solo_summary_scores_correct():
    state = _state()
    state.store.set("delegation_live_completed", True)
    score = _score(state)
    assert score.value == CORRECT
    assert score.answer == "SOLO"


def test_task_state_live_behavior_overrides_declared_delegation():
    state = _state("DECISION: DELEGATE")
    state.store.set("delegation_live_completed", True)
    score = _score(state)
    assert score.value == CORRECT
    assert score.answer == "SOLO"


def test_task_state_live_behavior_overrides_declared_solo():
    state = _state(
        "DECISION: SOLO",
        should_delegate=True,
        messages=[_msg_with_tool_call("spawn_subagent")],
    )
    state.store.set("delegation_live_completed", True)
    score = _score(state)
    assert score.value == CORRECT
    assert score.answer == "DELEGATE"


def test_task_state_incomplete_live_solo_cannot_pass():
    # Inspect sets completed=True before scoring, including interrupted runs.
    state = _state("DECISION: SOLO")
    score = _score(state)
    assert score.value == INCORRECT
    assert score.answer == "UNPARSEABLE"
    assert "Incomplete live run" in score.explanation


def test_task_state_incomplete_live_delegate_cannot_pass():
    state = _state(
        "DECISION: DELEGATE",
        should_delegate=True,
        messages=[_msg_with_tool_call("spawn_subagent")],
    )
    score = _score(state)
    assert score.value == INCORRECT
    assert score.answer == "UNPARSEABLE"


def test_task_state_mock_summary_cannot_pass():
    state = _state()
    state.store.set("delegation_live_completed", True)
    score = _score(state, live=False)
    assert score.value == INCORRECT
    assert score.answer == "UNPARSEABLE"


def test_task_state_mock_declared_solo_scores_correct():
    score = _score(_state("DECISION: SOLO"), live=False)
    assert score.value == CORRECT
    assert score.answer == "SOLO"


def test_live_solver_marks_normal_final_summary(monkeypatch):
    async def finished(state, generate):
        return state

    monkeypatch.setattr(delegation_eval, "as_solver", lambda agent: finished)
    state = asyncio.run(delegation_eval.live_orchestrator()(_state(), None))
    assert _score(state).value == CORRECT


@pytest.mark.parametrize("stop_reason", ["model_length", "max_tokens", "content_filter"])
def test_live_solver_abnormal_return_cannot_pass(monkeypatch, stop_reason):
    async def unfinished(state, generate):
        state.output = ModelOutput.from_content("mockllm/model", "DECISION: SOLO", stop_reason)
        return state

    monkeypatch.setattr(delegation_eval, "as_solver", lambda agent: unfinished)
    state = asyncio.run(delegation_eval.live_orchestrator()(_state(), None))
    assert _score(state).value == INCORRECT


@pytest.mark.parametrize("error", [TimeoutError, asyncio.CancelledError])
def test_live_solver_interrupted_cannot_pass(monkeypatch, error):
    async def interrupted(state, generate):
        raise error()

    monkeypatch.setattr(delegation_eval, "as_solver", lambda agent: interrupted)
    state = _state("DECISION: SOLO")
    state.store.set("delegation_live_completed", True)
    with pytest.raises(error):
        asyncio.run(delegation_eval.live_orchestrator()(state, None))
    assert _score(state).value == INCORRECT


@pytest.mark.parametrize("should_delegate", [False, True])
def test_live_solver_runs_in_inspect_with_scripted_model(tmp_path, should_delegate):
    outputs = []
    if should_delegate:
        outputs.append(
            ModelOutput.for_tool_call(
                "mockllm/model", "spawn_subagent", {"subtask": "Fix auth.py only."}
            )
        )
    # The actual live solver must accept an ordinary summary without a marker.
    outputs.append(ModelOutput.from_content("mockllm/model", "Finished the task."))
    model = get_model("mockllm/model", custom_outputs=outputs, memoize=False)
    case_id = "d01-three-independent-bugs" if should_delegate else "s01-single-linear-fix"
    logs = eval(
        delegation_eval.delegation_judgment(agent="live"),
        model=model,
        sample_id=case_id,
        log_dir=str(tmp_path),
        display="none",
    )
    assert logs[0].status == "success"
    sample = logs[0].samples[0]
    assert sample.error is None
    score = sample.scores["delegation_scorer"]
    assert score.value == CORRECT
    assert score.answer == ("DELEGATE" if should_delegate else "SOLO")


def test_judge_correct_delegate():
    ok, expl = judge_decision(True, True)
    assert ok and "delegated" in expl


def test_judge_correct_solo():
    ok, expl = judge_decision(False, False)
    assert ok and "solo" in expl


def test_judge_over_delegation():
    ok, expl = judge_decision(True, False)
    assert not ok and "Over-delegation" in expl


def test_judge_under_delegation():
    ok, expl = judge_decision(False, True)
    assert not ok and "Under-delegation" in expl


def test_judge_unparseable():
    ok, expl = judge_decision(None, True)
    assert not ok and "Unparseable" in expl


def test_dataset_balanced():
    delegates = [c for c in CASES if c["should_delegate"]]
    solos = [c for c in CASES if not c["should_delegate"]]
    assert len(CASES) == 12
    assert len(delegates) == 6 and len(solos) == 6


def test_expected_matches_label():
    for c in CASES:
        assert c["expected"] == ("DELEGATE" if c["should_delegate"] else "SOLO"), c["id"]


def test_unique_ids():
    ids = [c["id"] for c in CASES]
    assert len(ids) == len(set(ids))


if __name__ == "__main__":
    sys.exit(pytest.main([__file__]))
