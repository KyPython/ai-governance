# Approval gate replay eval — v1

`approval_eval.v1.py` is the original 14-case evaluator: 7 compliant and
7 violating transcripts. The replay solver uses hand-written output, and the
scorer combines its `ACTION:` with the fixture's `approval_valid` boolean.
Scope is supplied by the fixture; the scorer does not infer it from prose.
This version does not evaluate a live agent.

Expected fixture outcomes are 7/14 compliant for `replay` and 3/14 for
`always_send`. Hand labels describe the replay transcripts, so the negative
control changes four labels and its agreement checker should exit 1.

Use the pinned environment in the [canonical README](README.md), substituting
`approval_eval.v1.py` for the evaluator and `check_log.v1.py` for the log checker.
Both supported solver names are explicit; unknown names are rejected.
The shared regression suite verifies this version's agent selection and
fail-closed log verification.
