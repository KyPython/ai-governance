# Design: Stop agent-client-protocol 1.0.0 from breaking the eval tests

Spec ID: ACP

## Verified current state (2026-11-10, local venv, Python 3)

| `inspect-ai` | `agent-client-protocol` | `evals/delegation-judgment` pytest |
|---|---|---|
| 0.3.287 | 1.0.0 (what CI resolves today) | 2 failed, 31 passed (`acp.helpers` missing) |
| 0.3.287 | 0.12.1 | 33 passed |
| 0.3.289 (latest) | 1.0.0 | 33 passed |

The CI log for `system-quality` on #264 shows `Collecting agent-client-protocol>=0.12.0 (from inspect-ai==0.3.287...)`
and installs `agent_client_protocol-1.0.0`. PyPI lists `inspect-ai` 0.3.289 as latest; its
metadata still requires `agent-client-protocol>=0.12.0`.

## Decision

Add `agent-client-protocol==0.12.1` to `requirements.txt` and keep `inspect-ai==0.3.287`.

| Option | Result | Why not chosen |
|---|---|---|
| Pin `agent-client-protocol==0.12.1` (chosen) | One added line; restores the set the tests passed with before 2026-11-09 | Leaves `inspect-ai` one release behind; a later upgrade is separate work. |
| Bump to `inspect-ai==0.3.289` and pin `agent-client-protocol==1.0.0` | Also 33 passed locally | Two version changes; the rest of `evals/` has not been run against 0.3.289. |
| Leave unpinned and wait for upstream | No change | Every PR stays red, and the next release can break it again. |

Ky can choose the second option instead when merging; the requirements hold for either.

## Unknowns

- Whether other evals under `evals/` that CI does not run depend on `acp` 1.0 behavior.

## Human gates

- HOLD 1: Ky merges this spec-only PR.
- HOLD 2: Ky merges the one-task code PR after its review.
