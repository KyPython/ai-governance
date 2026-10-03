#!/usr/bin/env bash
# Opt a repository into KyPython/ai-governance.
#
#   optin.sh <repo>              open a PR adding the governance caller workflow,
#                                the canonical AGENTS.md section and CODEOWNERS
#   optin.sh --protect <repo>    after the PR's checks ran once, require
#                                "ai-governance / verdict" + 1 code-owner approval on main
#        [--strict-admins]       with --protect on a repo that has no protection yet:
#                                also enforce on admins (default: admin bypass allowed so
#                                Ky is never locked out)
#
# <repo> is "name" (owner defaults to KyPython) or "owner/name".
# Auth: GITHUB_TOKEN or GITHUB_RELAY_ISSUES_TOKEN (classic PAT: repo, workflow). Never printed.
# Never merges, deletes, or changes visibility.
set -euo pipefail

GOV_REPO="KyPython/ai-governance"
BRANCH="governance/enforce-ai-governance"
CHECK="ai-governance / verdict"
ACTIONS_APP_ID=15368
TOKEN="${GITHUB_TOKEN:-${GITHUB_RELAY_ISSUES_TOKEN:-}}"
[ -n "$TOKEN" ] || { echo "Set GITHUB_TOKEN or GITHUB_RELAY_ISSUES_TOKEN" >&2; exit 2; }
export TOKEN

MODE=optin; STRICT_ADMINS=false; REPO=""
for a in "$@"; do
  case "$a" in
    --protect) MODE=protect ;;
    --strict-admins) STRICT_ADMINS=true ;;
    -h|--help) sed -n '2,16p' "$0"; exit 0 ;;
    *) REPO="$a" ;;
  esac
done
[ -n "$REPO" ] || { sed -n '2,16p' "$0"; exit 2; }
[[ "$REPO" == */* ]] || REPO="KyPython/$REPO"

# api METHOD PATH [JSON]  -> prints body; HTTP status via $(st) (works inside $(...))
STATUS_FILE="$(mktemp)"
st() { cat "$STATUS_FILE"; }
api() {
  local out; out="$(mktemp)"
  curl -sS -o "$out" -w '%{http_code}' -X "$1" \
    -H "Authorization: token $TOKEN" -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    ${3:+-d "$3"} "https://api.github.com$2" > "$STATUS_FILE"
  cat "$out"; rm -f "$out"
}
jget() { python3 -c "import sys,json; d=json.load(sys.stdin); print(eval(sys.argv[1]))" "$1"; }
gitc() { git -c credential.helper= -c credential.helper='!f(){ echo username=x-access-token; echo "password=$TOKEN"; }; f' "$@"; }

DEFAULT_BRANCH=$(api GET "/repos/$REPO" | jget 'd.get("default_branch","")')
[ "$(st)" = 200 ] || { echo "Cannot read $REPO (HTTP $(st))" >&2; exit 1; }

if [ "$MODE" = protect ]; then
  # Only require the check once it has actually run, so the context name is real.
  HEAD_SHA=$(api GET "/repos/$REPO/commits/$BRANCH" | jget 'd.get("sha","")' 2>/dev/null || true)
  [ -n "$HEAD_SHA" ] || HEAD_SHA=$(api GET "/repos/$REPO/commits/$DEFAULT_BRANCH" | jget 'd["sha"]')
  RUNS=$(api GET "/repos/$REPO/commits/$HEAD_SHA/check-runs?check_name=$(python3 -c 'import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))' "$CHECK")" | jget 'd.get("total_count",0)')
  if [ "$RUNS" = 0 ]; then
    echo "Check \"$CHECK\" has not run on $REPO yet (looked at $HEAD_SHA). Open the opt-in PR first, wait for checks, then re-run." >&2
    exit 1
  fi
  PROT=$(api GET "/repos/$REPO/branches/$DEFAULT_BRANCH/protection")
  if [ "$(st)" = 200 ] && [ "$(echo "$PROT" | jget 'bool(d.get("required_status_checks"))')" = True ]; then
    BODY=$(echo "$PROT" | python3 -c "
import sys,json
d=json.load(sys.stdin)['required_status_checks']
checks=[{'context':c['context'],'app_id':c.get('app_id')} for c in d.get('checks',[])]
checks=[{k:v for k,v in c.items() if v is not None} for c in checks]
if not any(c['context']==sys.argv[1] for c in checks): checks.append({'context':sys.argv[1],'app_id':int(sys.argv[2])})
print(json.dumps({'strict':d.get('strict',True),'checks':checks}))" "$CHECK" "$ACTIONS_APP_ID")
    RESP=$(api PATCH "/repos/$REPO/branches/$DEFAULT_BRANCH/protection/required_status_checks" "$BODY")
    echo "PATCH required_status_checks -> HTTP $(st)"
  elif [ "$(st)" = 404 ] || [ "$(st)" = 200 ]; then
    if [ "$(st)" = 200 ]; then
      echo "Branch protection exists without required checks; add \"$CHECK\" in Settings > Branches to avoid overwriting it." >&2; exit 1
    fi
    ENFORCE=false; [ "$STRICT_ADMINS" = true ] && ENFORCE=true
    BODY=$(python3 -c "
import json,sys
print(json.dumps({
 'required_status_checks':{'strict':True,'checks':[{'context':sys.argv[1],'app_id':int(sys.argv[2])}]},
 'enforce_admins':sys.argv[3]=='true',
 'required_pull_request_reviews':{'required_approving_review_count':1,'require_code_owner_reviews':True,'dismiss_stale_reviews':True},
 'restrictions':None,'allow_force_pushes':False,'allow_deletions':False,'required_conversation_resolution':True}))" "$CHECK" "$ACTIONS_APP_ID" "$ENFORCE")
    RESP=$(api PUT "/repos/$REPO/branches/$DEFAULT_BRANCH/protection" "$BODY")
    echo "PUT branch protection -> HTTP $(st) (enforce_admins=$ENFORCE)"
  else
    RESP="$PROT"
  fi
  case "$(st)" in
    200|201) echo "Protected $REPO@$DEFAULT_BRANCH: PR + 1 code-owner approval + \"$CHECK\" required, no force-push/deletion." ;;
    403) echo "HTTP 403: $(echo "$RESP" | jget 'd.get("message")'). Private repos on GitHub Free cannot use branch protection; GitHub Pro (~\$4/mo) or a public repo is required." >&2; exit 1 ;;
    *) echo "HTTP $(st): $RESP" >&2; exit 1 ;;
  esac
  exit 0
fi

# ---- opt-in PR ----
api GET "/repos/$REPO/branches/$BRANCH" >/dev/null || true
[ "$(st)" = 404 ] || { echo "Branch $BRANCH already exists on $REPO; review that PR instead." >&2; exit 1; }
GOV_SHA=$(api GET "/repos/$GOV_REPO/commits/main" | jget 'd["sha"]')
SECTION=$(curl -fsS -H "Authorization: token $TOKEN" -H "Accept: application/vnd.github.raw" \
  "https://api.github.com/repos/$GOV_REPO/contents/AGENTS.governance.md?ref=$GOV_SHA")
TEMPLATE=$(curl -fsS -H "Authorization: token $TOKEN" -H "Accept: application/vnd.github.raw" \
  "https://api.github.com/repos/$GOV_REPO/contents/templates/ai-governance.yml?ref=$GOV_SHA")

WORK=$(mktemp -d); trap 'rm -rf "$WORK" "$STATUS_FILE"' EXIT
gitc clone -q --branch "$DEFAULT_BRANCH" "https://github.com/$REPO.git" "$WORK/repo"
cd "$WORK/repo"
LOGIN=$(api GET /user | jget 'd["login"]'); UID_=$(api GET /user | jget 'd["id"]')
git config user.name "$LOGIN"; git config user.email "${UID_}+${LOGIN}@users.noreply.github.com"
git checkout -q -b "$BRANCH"

mkdir -p .github/workflows
printf '%s\n' "${TEMPLATE//__AI_GOVERNANCE_SHA__/$GOV_SHA}" > .github/workflows/ai-governance.yml
[ "$DEFAULT_BRANCH" = main ] || sed -i "s/branches: \[main\]/branches: [$DEFAULT_BRANCH]/" .github/workflows/ai-governance.yml

export SECTION
python3 - <<'PY'
import os
from pathlib import Path
sec = os.environ["SECTION"].rstrip() + "\n"
p = Path("AGENTS.md")
if not p.exists():
    p.write_text("# Agent rules\n\n" + sec)
elif "AI-GOVERNANCE:v1" not in p.read_text():
    lines = p.read_text().splitlines(keepends=True)
    i = 1 if lines and lines[0].startswith("# ") else 0
    p.write_text("".join(lines[:i]) + ("\n" if i else "") + sec + "\n" + "".join(lines[i:]))
PY
if [ ! -f .github/CODEOWNERS ] && [ ! -f CODEOWNERS ] && [ ! -f docs/CODEOWNERS ]; then
  printf '# Every path requires human (Ky) review.\n* @%s\n' "$LOGIN" > .github/CODEOWNERS
fi
if [ -d .systems-thinking/contracts ]; then
  cat > ".systems-thinking/contracts/$(date +%F)-enforce-ai-governance.json" <<JSON
{
  "type": "SYSTEMS_THINKING_CONTRACT",
  "title": "Enforce shared AI governance gate",
  "scope": [".github/", "AGENTS.md"],
  "event": "AI coding agents (Kiro, Codex, Cursor, Grok Bot) open PRs in this repository.",
  "pattern": "Governance rules lived only in LamportLogic, so agent changes elsewhere could merge without the same checks.",
  "structure": "Each repository carried its own partial CI; there was no shared, versioned gate or required check binding agents to the rules.",
  "archetype": "Shifting the Burden: per-repo manual review compensates for a missing structural gate.",
  "intervention": "Call the SHA-pinned reusable workflow from KyPython/ai-governance and require its verdict check plus code-owner approval on main.",
  "leading_indicators": "Every PR shows a green or red 'ai-governance / verdict' check; no merge to main without it and Ky's approval.",
  "transfer": "Opt any repository in with ai-governance/scripts/optin.sh so all agent-touched repos share one gate."
}
JSON
fi
git add -A
git commit -q -m "ci(governance): enforce shared AI governance gate"
gitc push -q origin "$BRANCH"
PR_BODY="Opts this repo into the shared AI governance gate from [$GOV_REPO](https://github.com/$GOV_REPO) (pinned to \`$GOV_SHA\`).

- \`.github/workflows/ai-governance.yml\` calls the reusable gate (install, lint, type-check, test, build, policy, gitleaks) on PRs and pushes to \`$DEFAULT_BRANCH\`.
- \`AGENTS.md\` gains the canonical \`AI-GOVERNANCE:v1\` section all agents must follow.

After checks run once: \`optin.sh --protect $REPO\` makes \`$CHECK\` + 1 code-owner approval required. Do not merge without Ky's review."
BODY=$(python3 -c 'import json,sys; print(json.dumps({"title":"ci(governance): enforce shared AI governance gate","head":sys.argv[1],"base":sys.argv[2],"body":sys.argv[3]}))' "$BRANCH" "$DEFAULT_BRANCH" "$PR_BODY")
URL=$(api POST "/repos/$REPO/pulls" "$BODY" | jget 'd.get("html_url") or d')
echo "Opened PR: $URL"
echo "Next: wait for the '$CHECK' check, then run: $0 --protect $REPO"
