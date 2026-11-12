#!/usr/bin/env bash
# sweep.sh: enforce KyPython/ai-governance on every repo the token's user owns or admins.
#
#   sweep.sh            report only (default, no writes)
#   sweep.sh --apply    open opt-in PRs and apply the protection model
#                       (requires a skip list: $SWEEP_SKIP or sweep.sh's dir/sweep.skip)
#
# For each non-archived, non-fork, non-empty repo of the user and of every org where the
# user is an admin (minus sweep.skip):
#   1. No gate on the default branch and no opt-in branch: open the opt-in PR (optin.sh).
#      If the repo restricts Actions to "selected", allow the shared workflow first.
#   2. Once "ai-governance / verdict" has passed (on the opt-in branch or the default
#      branch), apply the protection model with optin.sh --protect. Required: PR; repo CI that
#      ran on a PR + verdict; strict; conversation resolution; linear history; no
#      force-push/deletion; enforce on admins; 0 approvals.
#   3. Already protected with the verdict required: left alone, but the pinned gate SHA is checked.
#      A pin older than the spec/role gate (no roles.yml support) is reported as "stale-pin".
#   4. Gated repos (specs/governed-by-default, GBD-3): in a "selected Actions" repo, allow every
#      KyPython/ai-governance path the workflow uses (workflows and actions); while the pin differs
#      from ai-governance main, keep exactly one bump PR open (an existing ci/bump-ai-governance*
#      PR is updated, not duplicated).
# The logic lives in scripts/sweep.py.
#   Set AI_GOVERNANCE_REF to pin new opt-ins to a ref other than main (e.g. an unmerged gate PR).
# Never merges, deletes, or changes visibility. Private repos on free plans report the 403.
#
# AUTH: runs with whatever GITHUB_TOKEN is configured, and every PR/commit is authored as that
# token's user. It needs repo + workflow scope plus admin on each repo for protection. Use a
# token you're comfortable having open PRs and change branch protection everywhere.
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${GITHUB_TOKEN:?Set GITHUB_TOKEN}"
APPLY=0; [ "${1:-}" = "--apply" ] && APPLY=1
SKIP_FILE="${SWEEP_SKIP:-$DIR/sweep.skip}"
if [ "$APPLY" = 1 ] && [ ! -f "$SKIP_FILE" ]; then
  echo "Refusing --apply without a skip list ($SKIP_FILE). Create it (it may be empty) after reviewing repos whose own rules forbid AI edits." >&2
  exit 2
fi
export APPLY DIR SKIP_FILE
exec python3 "$DIR/sweep.py"
