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
python3 - <<'PY'
import json, os, subprocess, sys, urllib.request, urllib.error, urllib.parse
T=os.environ["GITHUB_TOKEN"]; APPLY=os.environ["APPLY"]=="1"; DIR=os.environ["DIR"]
CHECK="ai-governance / verdict"; BRANCH="governance/enforce-ai-governance"
PATTERN="KyPython/ai-governance/.github/workflows/governance.yml@*"
def api(method, path, body=None):
    req=urllib.request.Request("https://api.github.com"+path, method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization":"token "+T,"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"})
    try:
        with urllib.request.urlopen(req) as r:
            b=r.read(); return r.status, (json.loads(b) if b else None)
    except urllib.error.HTTPError as e:
        b=e.read()
        try: return e.code, json.loads(b)
        except Exception: return e.code, None
def pages(path):
    out, p = [], 1
    while True:
        s,d=api("GET", f"{path}{'&' if '?' in path else '?'}per_page=100&page={p}")
        if s!=200 or not d: return out
        out+=d; p+=1
        if len(d)<100: return out
skip={}
sf=os.environ["SKIP_FILE"]
if os.path.exists(sf):
    for line in open(sf):
        if line.strip() and not line.startswith("#"):
            parts=line.split(None,1); skip[parts[0]]=parts[1].strip() if len(parts)>1 else ""
me=api("GET","/user")[1]["login"]
owners={me}
for m in pages("/user/memberships/orgs?state=active"):
    if m.get("role")=="admin": owners.add(m["organization"]["login"])
repos=[r for r in pages("/user/repos?affiliation=owner,organization_member") if r["owner"]["login"] in owners]
def verdict_ok(repo, ref):
    s,c=api("GET", f"/repos/{repo}/commits/{urllib.parse.quote(ref,safe='')}/check-runs?check_name={urllib.parse.quote(CHECK)}&filter=latest")
    runs=(c or {}).get("check_runs",[]) if s==200 else []
    return (runs[0]["conclusion"] if runs else None)
import re, base64
def pin_has_role_gate(repo, ref):
    s,c=api("GET", f"/repos/{repo}/contents/.github/workflows/ai-governance.yml?ref={urllib.parse.quote(ref,safe='')}")
    if s!=200: return None
    m=re.search(r"KyPython/ai-governance/\.github/workflows/governance\.yml@([0-9a-f]{40})", base64.b64decode(c["content"]).decode())
    if not m: return False
    s,g=api("GET", f"/repos/KyPython/ai-governance/contents/.github/workflows/governance.yml?ref={m.group(1)}")
    return s==200 and "ROLES_URL" in base64.b64decode(g["content"]).decode()
def run(args):
    env=dict(os.environ, GITHUB_TOKEN=T)
    p=subprocess.run([os.path.join(DIR,"optin.sh"),*args], capture_output=True, text=True, env=env)
    return p.returncode, (p.stdout+p.stderr).strip().replace("\n"," | ")
rows=[]
for r in sorted(repos, key=lambda r:r["full_name"].lower()):
    fn, db = r["full_name"], r["default_branch"]
    if r["archived"]: rows.append((fn,"skip","archived")); continue
    if r["fork"]: rows.append((fn,"skip","fork")); continue
    if fn in skip: rows.append((fn,"skip",skip[fn])); continue
    if r.get("size",0)==0 and api("GET",f"/repos/{fn}/commits?per_page=1")[0]!=200:
        rows.append((fn,"skip","empty repo")); continue
    gated = api("GET", f"/repos/{fn}/contents/.github/workflows/ai-governance.yml?ref={db}")[0]==200 \
            or (fn=="KyPython/ai-governance")
    s,prot=api("GET", f"/repos/{fn}/branches/{db}/protection")
    required=[c["context"] for c in ((prot or {}).get("required_status_checks") or {}).get("checks",[])] if s==200 else []
    if s==200 and CHECK in required and (prot.get("enforce_admins") or {}).get("enabled"):
        branch_exists0 = api("GET", f"/repos/{fn}/branches/{urllib.parse.quote(BRANCH,safe='')}")[0]==200
        pin_ref = db if gated else (BRANCH if branch_exists0 else db)
        pin = True if fn=="KyPython/ai-governance" else pin_has_role_gate(fn, pin_ref)
        if pin is False:
            rows.append((fn,"stale-pin",f"protected, but the gate pinned on {pin_ref} predates the spec/role gate; bump the SHA in a PR")); continue
        rows.append((fn,"ok","protected; verdict required; spec/role gate pinned" + ("" if gated else " (opt-in PR not merged yet)"))); continue
    if s==403:
        prot_note="branch protection unavailable (private repo on free plan: needs Pro/Team or public)"
    else:
        prot_note=None
    branch_exists = api("GET", f"/repos/{fn}/branches/{urllib.parse.quote(BRANCH,safe='')}")[0]==200
    if not gated and not branch_exists:
        if not APPLY: rows.append((fn,"todo","would open opt-in PR")); continue
        s2,ap=api("GET", f"/repos/{fn}/actions/permissions")
        if s2==200 and ap.get("allowed_actions")=="selected":
            _,sel=api("GET", f"/repos/{fn}/actions/permissions/selected-actions")
            pats=(sel or {}).get("patterns_allowed",[])
            if PATTERN not in pats:
                api("PUT", f"/repos/{fn}/actions/permissions/selected-actions",
                    {"github_owned_allowed":sel.get("github_owned_allowed",True),"verified_allowed":sel.get("verified_allowed",False),"patterns_allowed":pats+[PATTERN]})
        rc,out=run([fn]); rows.append((fn,"opened" if rc==0 else "error",out)); continue
    ref = BRANCH if branch_exists else db
    v=verdict_ok(fn, ref)
    if v!="success":
        rows.append((fn,"pending",f"verdict on {ref}: {v or 'not run yet'}" + (f"; {prot_note}" if prot_note else ""))); continue
    if prot_note: rows.append((fn,"blocked",prot_note)); continue
    if not APPLY: rows.append((fn,"todo","would apply protection model")); continue
    rc,out=run(["--protect", fn]); rows.append((fn,"protected" if rc==0 else "error",out))
w=max(len(x[0]) for x in rows) if rows else 10
for fn,st,note in rows: print(f"{fn:<{w}}  {st:<9}  {note}")
print(f"\n{'APPLIED' if APPLY else 'REPORT ONLY (use --apply to write)'}: {len(rows)} repos")
PY
