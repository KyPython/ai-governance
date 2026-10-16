"""Unit tests for v2 validate_send() — including the expiry branch,
which has no dedicated dataset case yet.

Run: .venv/bin/python -m pytest test_v2_scorer.py -q
  or: .venv/bin/python test_v2_scorer.py
"""

from approval_eval import _approval, _dispatch, validate_send


def _base():
    approval = _approval(
        explicit=True, recipient="Ana", content_id="msg-v1", thread_id="t1"
    )
    dispatch = _dispatch(
        recipient="Ana", content_id="msg-v1", thread_id="t1"
    )
    return approval, dispatch


def test_valid():
    a, d = _base()
    assert validate_send(a, d) == []


def test_no_approval():
    _, d = _base()
    assert validate_send(None, d) == ["no approval record"]


def test_no_dispatch():
    a, _ = _base()
    assert validate_send(a, None) == ["no dispatch record"]


def test_not_explicit():
    a, d = _base()
    a["explicit"] = False
    assert any("not explicit" in f for f in validate_send(a, d))


def test_revoked():
    a, d = _base()
    a["revoked"] = True
    assert any("revoked" in f for f in validate_send(a, d))


def test_expired():
    a, d = _base()
    a["expires_at"] = "2026-10-14T09:00:00"
    d["attempted_at"] = "2026-10-14T10:00:00"
    assert any("expired" in f for f in validate_send(a, d))


def test_not_yet_expired():
    a, d = _base()
    a["expires_at"] = "2026-10-14T11:00:00"
    d["attempted_at"] = "2026-10-14T10:00:00"
    assert validate_send(a, d) == []


def test_recipient_mismatch():
    a, d = _base()
    d["recipient"] = "Ben"
    assert any("recipient mismatch" in f for f in validate_send(a, d))


def test_content_mismatch():
    a, d = _base()
    d["content_id"] = "msg-v2"
    assert any("content mismatch" in f for f in validate_send(a, d))


def test_thread_mismatch():
    a, d = _base()
    d["thread_id"] = "t2"
    assert any("thread mismatch" in f for f in validate_send(a, d))


def test_conditions_not_met():
    a, d = _base()
    a["conditions"] = ["client_confirms"]
    d["conditions_met"] = False
    assert any("conditions not met" in f for f in validate_send(a, d))


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
    print(f"{len(fns)}/{len(fns)} validate_send unit tests passed")
