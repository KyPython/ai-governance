# Verification — 20-case dispatch suite

## Current source verification (2026-10-16)

The unchanged benchmark contains 20 fixtures: 2 ALLOW and 18 BLOCK. Supplemental
regressions live in `tests/test_gate.py`; they are not extra benchmark examples.

- `PYTHONPATH=. python -m unittest discover -s tests -v`: **12/12 passed**.
- `python run_offline.py --output offline_results.json`: **20/20 passed**, with
  2 authorized simulated dispatches and 0 dispatches across the 18 blocked cases.
- `bash /absolute/path/to/ai-governance/evals/dispatch-regression-20case/run_native.sh
  --log-dir /tmp/ai-governance-227-dispatch-logs`, invoked from `/tmp` with
  `inspect-ai` **0.3.280**: **20/20 passed**, accuracy **1.000**, status success.
  No model calls, API keys, or network dispatches were used. The native receipt
  was inspected locally; generated `.eval` logs are not included in this bundle.

`CHECKSUMS.json` lists all **12 tracked suite files other than the manifest
itself**, including this note and `tests/test_gate.py`. Paths are relative to
this directory; there is no suite-local `.gitignore`. The current manifest was
regenerated after the code, documentation, and offline receipt changed.

To verify the manifest from this directory:

```bash
python - <<'PYTHON'
import hashlib
import json
from pathlib import Path

manifest = json.loads(Path("CHECKSUMS.json").read_text())
for name, expected in manifest.items():
    actual = hashlib.sha256(Path(name).read_bytes()).hexdigest()
    assert actual == expected, name
print(f"Verified {len(manifest)} files")
PYTHON
```

## Historical recorded receipts (2026-10-14)

The original import was recorded as originating in
`inspect_approval_trial_fixed__1.zip`, plus a byte-identical standalone
`cases.py`. Neither that archive nor its external execution logs are included
here, so those original provenance claims are historical records rather than
newly reproduced evidence.

The imported notes recorded an offline result of 20/20, an independent native
Inspect 0.3.280 result of 20/20, and 5/5 unit tests. A separate initial trial
report said native Inspect was unavailable in its environment. These describe
different historical runs. Their results and original hashes do not certify
the revised source; the current checks and regenerated receipt above do.

## Scope

These checks exercise a local reference approval gate and inert simulated
transport, with no deployed agent or model. Sequential calls sharing trusted
state consume the approval and idempotency key after a successful simulated
dispatch. Atomic consumption under concurrency and real transport failure
recovery require production infrastructure and are not established here.

This suite remains separate from `../approval-gate/`; no cases were
merged between suites.
