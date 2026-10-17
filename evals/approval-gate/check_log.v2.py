"""Verify a successful inspect_ai eval log against hand labels.

Usage: .venv/bin/python check_log.py <log-file.eval>
Uses inspect_ai's read_eval_log (logs are binary .eval by default).
Prints per-sample scorer verdict vs expected, plus compliance rate
(share C) and scorer agreement (share scorer == expected).
Exit 0 only for a successful, nonempty log whose C/I scores all match
valid C/I hand labels. A negative control may correctly exit 1.
"""

import sys


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_log.py <log-file>", file=sys.stderr)
        return 2
    from inspect_ai.log import read_eval_log

    log = read_eval_log(sys.argv[1])
    if log.status != "success":
        print(f"Evaluation did not succeed: status={log.status}", file=sys.stderr)
        return 1
    samples = log.samples or []
    if not samples:
        print("No samples in log.")
        return 1
    correct = 0
    agree = 0
    for s in samples:
        sample_id = s.id
        meta = s.metadata or {}
        expected = meta.get("expected")
        score = (s.scores or {}).get("approval_scorer")
        value = score.value if score else None
        valid = (
            isinstance(expected, str)
            and expected in ("C", "I")
            and isinstance(value, str)
            and value in ("C", "I")
        )
        ok = valid and value == expected
        agree += int(ok)
        correct += int(value == "C")
        print(f"{sample_id}: scorer={value} expected={expected} {'OK' if ok else 'MISMATCH'}")
    n = len(samples)
    print(f"\ncompliance rate (share C): {correct}/{n} = {correct / n:.1%}")
    print(f"scorer agreement (scorer == hand label): {agree}/{n} = {agree / n:.1%}")
    return 0 if agree == n else 1


if __name__ == "__main__":
    raise SystemExit(main())
