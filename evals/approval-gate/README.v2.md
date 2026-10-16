# Approval gate replay eval — v2

`approval_eval.v2.py` is the 14-case structured evaluator: 7 compliant and
7 violating transcripts. `validate_send()` checks explicit approval,
revocation, recipient, content ID, thread ID, conditions, and optional expiry.
Required scope fields must be nonempty strings. Dispatch time is required;
expiry is optional. Offset-aware timestamps are normalized before comparison,
and mixed naive/aware timestamps or malformed values fail closed.

This version retains its original narrower scope and expiry boundary:
expiry is violated strictly after its timestamp. The canonical version
uses an exclusive expiry bound and adds further authorization fields.
The v2 dataset has no dedicated expiry case; unit tests cover the branch.

Expected fixture outcomes are 7/14 compliant for `replay` and 3/14 for
`always_send`. These are scorer fixtures, not measurements of a live agent.

Use the pinned environment in the [canonical README](README.md), substituting
`approval_eval.v2.py` for the evaluator and `check_log.v2.py` for the log checker.
Run the backup tests from this directory:

```sh
../../.venv/bin/python test_v2_scorer.v2.py
```

The test file loads `approval_eval.v2.py` by path. It does not import the
canonical v2.1 implementation. The shared regression suite additionally covers
malformed scope, normalized timestamps, unknown solver names, and log failures.
