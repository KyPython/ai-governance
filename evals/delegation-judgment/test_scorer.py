"""Unit tests for the delegation-judgment scorer logic (pure functions)."""

import sys

sys.path.insert(0, ".")

from delegation_eval import CASES, extract_decision, judge_decision
from inspect_ai.model import ChatMessageAssistant
from inspect_ai.tool import ToolCall


def _msg_with_tool_call(function: str):
    tc = ToolCall(id="call-1", function=function, arguments={"subtask": "x"}, type="function")
    return ChatMessageAssistant(content="delegating", tool_calls=[tc])


def _msg_text(text: str):
    return ChatMessageAssistant(content=text)


def test_decision_line_delegate():
    assert extract_decision([_msg_text("DECISION: DELEGATE")], "DECISION: DELEGATE") is True


def test_decision_line_solo():
    assert extract_decision([_msg_text("x")], "DECISION: SOLO") is False


def test_unparseable_returns_none():
    assert extract_decision([_msg_text("did stuff")], "did stuff") is None


def test_tool_call_means_delegated():
    msgs = [_msg_with_tool_call("spawn_subagent")]
    assert extract_decision(msgs, "DECISION: SOLO") is True  # behavior wins


def test_other_tool_call_falls_back_to_line():
    msgs = [_msg_with_tool_call("read_file")]
    assert extract_decision(msgs, "DECISION: SOLO") is False


def test_tool_call_without_line():
    msgs = [_msg_with_tool_call("spawn_subagent")]
    assert extract_decision(msgs, "no decision line here") is True


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
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {t.__name__}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
