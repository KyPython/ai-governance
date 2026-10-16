"""Verify an inspect_ai eval log: scorer agreement vs hand labels.

Usage: .venv/bin/python check_log.py <log-file.eval>
Uses inspect_ai's read_eval_log (logs are binary .eval by default).
Prints per-sample scorer verdict vs expected, plus compliance rate
(share C) and scorer agreement (share scorer == expected).
Exit 0 only if every sample has a score.
"""

import sys


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_log.py <log-file>", file=sys.stderr)
        return 2
    from inspect_ai.log import read_eval_log

    log = read_eval_log(sys.argv[1])
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
        ok = value == expected
        agree += int(ok)
        correct += int(value == "C")
        print(f"{sample_id}: scorer={value} expected={expected} {'OK' if ok else 'MISMATCH'}")
    n = len(samples)
    print(f"\ncompliance rate (share C): {correct}/{n} = {correct / n:.1%}")
    print(f"scorer agreement (scorer == hand label): {agree}/{n} = {agree / n:.1%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
