# Eight-dimension CI evidence

This contract adds scoped acceptance and evidence accounting to existing project
checks. A passing pipeline establishes that the declared commands succeeded and
their evidence validated. It does not certify whole-system readiness, authorize
a merge/deploy, or replace the project's existing governance.

## Acceptance requirements

1. Every definition names the system, intended use, environment and governing
   requirements. Requirement file hashes must match before any check runs.
2. All eight dimensions must have acceptance criteria, a check mapping, explicit
   gaps and a next verification: correctness, security, reliability,
   data_integrity, observability, delivery, operations and outcome_evidence.
3. Declared commands run with argv, a finite timeout and their scoped input file
   hashes. Failed, missing or timed-out commands produce retained failure
   evidence and a nonzero result. Every declared check must be accounted for.
4. Evidence binds definition/requirement content, source revision, environment,
   command identity and current scoped input bytes. Missing, changed, expired,
   future-dated, cross-context or malformed evidence fails closed. Paths cannot
   escape the selected project or access Git internals.
5. CI-generated dimensions remain Partial when exercised and Not Evaluated when
   unexercised. Passing tests cannot silently erase gaps, claim independent
   outcomes or promote dimensions to Demonstrated. Readiness requests decline
   CI-only bundles. Independent operational/outcome qualification remains work
   for the project's existing governance and intended-use acceptance process.
6. Reruns can replace only tool-owned evidence directories. Check output remains
   in normal CI logs; receipts do not dump environments or embed credentials.
   Timed-out process groups are stopped. This tool is intended for reviewed
   development checks, not production operations, migrations or provider writes.

## Project definition

See this repository's `.quality/system.json` as a working example. The format is
version1 and uses only Python's standard library (Python3.11 or newer on macOS
or Linux). `requirements` contains project-relative `path` and `sha256` pairs.
`checks` maps stable IDs to `command` argv, `timeout_seconds` (1..3600), nonempty
file/glob `inputs`, `scope`, and an optional relative `cwd`. Each input pattern
must match real files. A literal `{python}` argv element resolves to the runner's
Python executable. The runner performs no shell interpolation; an explicitly
declared shell command is still code that the project owner must review.

Each dimension defines `acceptance_criteria`, `check_ids`, `gaps` and
`next_check`. Do not map one generic test to unrelated dimensions just to fill
the matrix. Keep real restore, live outcomes, provider authorization and operator
ownership unverified until their own acceptance evidence exists.

## Running locally and in CI

```sh
python3 scripts/system_quality.py run --root . \
  --definition .quality/system.json --output-dir .quality-results
python3 scripts/system_quality.py validate --root . \
  --assessment .quality-results/assessment.json --max-age-seconds 86400 --mode ci
```

Consumers can use `.github/actions/system-quality` from this repository at a
reviewed full commit SHA. Set `definition` and `output-directory` as needed.
Install the project's frozen dependencies first and retain existing lint/build,
security, network-confinement and negative-control checks. The action runs the
maintained tool bundled at that action revision against the caller workspace.
Upload the dedicated evidence directory with `if: always()`, bounded retention
and `if-no-files-found: error`. Require the containing existing CI job to pass.

The shared governance workflow also accepts `system-quality-definition`. An
opted-in caller must keep `run-quality: true`; otherwise its verdict fails.
Its helper action is pinned independently of the caller's source. Projects with
specialized native/OCI jobs can instead run the pinned composite action inside
their existing required jobs, keeping distinct subsystem environments separate.

`--mode readiness` returns nonzero for these CI-generated bundles. Its failure
is intentional: this tool does not authenticate independent manual/operational
proof. All eight real questions remain applicable, with readiness evidence
reviewed through the existing project-specific authority.

## Evidence limits

Receipts record execution and validate integrity/context within the selected CI
trust boundary. Hashes are not signatures or independent authorization, and a
project-controlled command can report a misleading outcome. Pinned workflow
review, meaningful oracles, isolated execution and independent checks remain
necessary. This is not an endpoint security assessment, a full dependency audit,
a recoverable backup, a load test or a customer-outcome benchmark.

## External required-job binding

An external validation job must run the actual stack checks and this composite
action. A caller can then use the authoritative reusable governance workflow
with **needs: validate**, **if: always()**, **run-quality: false**, and
**prerequisite-result** set to the actual needs.validate.result expression.
The verdict requires exact success; failure, cancellation, skipping and empty
results all fail. The existing policy and secret-scan jobs still run.

The prerequisite defaults to success only for unchanged legacy callers; its
presence alone does not prove another job ran. Review the actual needs binding,
required-check identity and pinned workflow source. Do not substitute a literal
success, a lookalike verdict name or a dependency whose skip is treated as a
successful required check. Consumers must verify their own required contexts.

Deployment remains governed by the canonical instructions. Preserve an existing
manual-only protected-human route; do not add automatic deployment. Such a route
must require main and successful required checks/governance for the exact
deployed revision, with Ky retaining deployment authority.

Regression tests exercise actual fixture processes and the maintained CLI,
including failures, timeouts, mutation, omitted evidence and false readiness.
The published agent-evaluation fixtures remain synthetic and have separate
source-specific tests. No deployment or live provider is needed for either suite.
