#!/usr/bin/env bash
# Opt a repository into KyPython/ai-governance.
#
#   optin.sh <repo>              open a PR adding the governance caller workflow,
#                                the canonical AGENTS.md section and CODEOWNERS
#   optin.sh --protect <repo>    once "ai-governance / verdict" has passed, protect the
#                                default branch: PR required, required checks = repo CI that
#                                ran on the PR + verdict, strict, conversation resolution,
#                                linear history, no force-push/deletion, enforce on admins,
#                                0 approvals (checks are the gate; Ky merges).
#                                DRY_RUN=1 prints the plan without changing anything.
#
# <repo> is "name" (owner defaults to KyPython) or "owner/name".
# Auth: GITHUB_TOKEN (classic PAT: repo, workflow; admin on the repo for --protect). Never printed.
# Never merges, deletes, or changes visibility.
set -euo pipefail

GOV_REPO="KyPython/ai-governance"
BRANCH="governance/enforce-ai-governance"
CHECK="ai-governance / verdict"
ACTIONS_APP_ID=15368   # GitHub Actions app
TOKEN="${GITHUB_TOKEN:-}"
[ -n "$TOKEN" ] || { echo "Set GITHUB_TOKEN" >&2; exit 2; }
export TOKEN

MODE=optin; REPO=""
for a in "$@"; do
  case "$a" in
    --protect) MODE=protect ;;
    -h|--help) sed -n '2,17p' "$0"; exit 0 ;;
    *) REPO="$a" ;;
  esac
done
[ -n "$REPO" ] || { sed -n '2,17p' "$0"; exit 2; }
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
  # Protection model (Ky, 2026-10-03): PR required; required checks = the repo's own CI
  # that actually ran on a PR + "ai-governance / verdict"; strict up-to-date; conversation
  # resolution; linear history; no force-push/deletion; enforce on admins; 0 approvals
  # (checks are the gate, Ky merges). Only applied once the verdict has run successfully.
  REPO="$REPO" BRANCH="$BRANCH" CHECK="$CHECK" APP="$ACTIONS_APP_ID" DEFAULT_BRANCH="$DEFAULT_BRANCH" DRY_RUN="${DRY_RUN:-0}" python3 - <<'PY2'
import json, os, re, sys, urllib.request, urllib.error, urllib.parse
T=os.environ["TOKEN"]; R=os.environ["REPO"]; CHECK=os.environ["CHECK"]; APP=int(os.environ["APP"]); DB=os.environ["DEFAULT_BRANCH"]
def api(method, path, body=None, raw=False):
    req=urllib.request.Request("https://api.github.com"+path, method=method, data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization":"token "+T,"Accept":"application/vnd.github.raw" if raw else "application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"})
    try:
        with urllib.request.urlopen(req) as r:
            b=r.read(); return r.status, (b.decode() if raw else (json.loads(b) if b else None))
    except urllib.error.HTTPError as e:
        b=e.read()
        try: return e.code, json.loads(b)
        except Exception: return e.code, b.decode(errors="replace")
s,br=api("GET",f"/repos/{R}/branches/{urllib.parse.quote(os.environ['BRANCH'],safe='')}")
sha=br["commit"]["sha"] if s==200 else api("GET",f"/repos/{R}/commits/{DB}")[1]["sha"]
_,cr=api("GET",f"/repos/{R}/commits/{sha}/check-runs?per_page=100&filter=latest")
runs=[c for c in cr.get("check_runs",[]) if (c.get("app") or {}).get("id")==APP]
verdict=[c for c in runs if c["name"]==CHECK]
if not verdict or verdict[0]["conclusion"]!="success":
    print(f"NOT PROTECTED: '{CHECK}' has not passed on {sha[:7]} (state: {verdict[0]['conclusion'] if verdict else 'never ran'}).", file=sys.stderr); sys.exit(3)
_,wr=api("GET",f"/repos/{R}/actions/runs?head_sha={sha}&per_page=100")
suite={w["check_suite_id"]:w for w in wr.get("workflow_runs",[])}
wf_text={}
def path_filtered(path):
    if path not in wf_text:
        s,t=api("GET",f"/repos/{R}/contents/{path}?ref={sha}",raw=True); wf_text[path]=t if s==200 else ""
    return bool(re.search(r"^\s*(paths|paths-ignore|branches-ignore)\s*:", wf_text[path], re.M))
req, skipped = {CHECK}, []
for c in runs:
    if c["name"]==CHECK: continue
    w=suite.get((c.get("check_suite") or {}).get("id"))
    if not w: skipped.append(f"{c['name']} (no workflow run)"); continue
    if w["path"].endswith("/ai-governance.yml") or w["path"].endswith("/self-test.yml"): continue
    if path_filtered(w["path"]): skipped.append(f"{c['name']} (path/branch-filtered {w['path']})"); continue
    if w["event"]!="pull_request" and not re.search(r"^\s*(pull_request\s*:|pull_request\s*$|-\s*pull_request\s*$|on\s*:.*\bpull_request\b)", wf_text.get(w["path"],""), re.M):
        skipped.append(f"{c['name']} (does not run on pull_request)"); continue
    if c["conclusion"] not in ("success","skipped","neutral"): skipped.append(f"{c['name']} ({c['conclusion']} on PR - fix before requiring)"); continue
    req.add(c["name"])
s,prot=api("GET",f"/repos/{R}/branches/{DB}/protection")
if s==200:
    for c in (prot.get("required_status_checks") or {}).get("checks",[]):
        if c["context"] not in req: skipped.append(f"{c['context']} (previously required, did not run on PR - dropped)")
elif s==403:
    print(f"NOT PROTECTED: HTTP 403 {prot.get('message') if isinstance(prot,dict) else prot}", file=sys.stderr); sys.exit(4)
_,repo=api("GET",f"/repos/{R}")
linear = bool(repo.get("allow_squash_merge") or repo.get("allow_rebase_merge"))
body={"required_status_checks":{"strict":True,"checks":[{"context":c,"app_id":APP} for c in sorted(req)]},
      "enforce_admins":True,
      "required_pull_request_reviews":{"required_approving_review_count":0,"require_code_owner_reviews":False,"require_last_push_approval":False,"dismiss_stale_reviews":False},
      "restrictions":None,"required_linear_history":linear,"allow_force_pushes":False,"allow_deletions":False,
      "required_conversation_resolution":True,"block_creations":False,"lock_branch":False}
print(f"{R}@{DB}: required checks = {sorted(req)}")
for x in skipped: print(f"  not required: {x}")
if not linear: print("  linear history NOT required: repo allows neither squash nor rebase merges")
if os.environ.get("DRY_RUN")=="1":
    print("DRY RUN - protection not changed"); sys.exit(0)
s,resp=api("PUT",f"/repos/{R}/branches/{DB}/protection",body)
if s in (200,201):
    print(f"PROTECTED {R}@{DB} (HTTP {s}): PR required, 0 approvals, strict checks, conversation resolution, linear={linear}, no force-push/deletion, enforce_admins")
    sys.exit(0)
msg=resp.get("message") if isinstance(resp,dict) else resp
print(f"NOT PROTECTED: HTTP {s} {msg}" + (" (private repo on a free plan: needs GitHub Pro/Team or a public repo)" if s==403 else ""), file=sys.stderr)
sys.exit(4)
PY2
  exit $?
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

Systems thinking: event = AI agents open PRs here; pattern = governance lived only in LamportLogic; structure = no shared, versioned gate; intervention = SHA-pinned reusable gate + required checks; leading indicator = every PR shows \`$CHECK\`; transfer = same opt-in for every repo.

Once \`$CHECK\` has passed, the default branch is protected: PR required, this repo's CI + \`$CHECK\` required, strict, linear history, conversation resolution, no force-push/deletion, enforce on admins. Ky merges."
BODY=$(python3 -c 'import json,sys; print(json.dumps({"title":"ci(governance): enforce shared AI governance gate","head":sys.argv[1],"base":sys.argv[2],"body":sys.argv[3]}))' "$BRANCH" "$DEFAULT_BRANCH" "$PR_BODY")
URL=$(api POST "/repos/$REPO/pulls" "$BODY" | jget 'd.get("html_url") or d')
echo "Opened PR: $URL"
echo "Next: wait for the '$CHECK' check, then run: $0 --protect $REPO"
