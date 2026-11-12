"""Governance sweep: keep every repo Ky owns or admins on the shared gate (spec specs/governed-by-default, GBD-3).

Run by scripts/sweep.sh, which checks the skip list. For each non-archived, non-fork, non-empty repo:
  1. no gate and no opt-in branch: allow the shared paths in a "selected Actions" repo, then open the opt-in PR;
  2. gated: allow every ai-governance path the workflow uses (GBD-3.4), and keep one bump PR open while the
     pin differs from ai-governance main (GBD-3.3);
  3. verdict passed: apply the protection model (optin.sh --protect).
Never merges, changes visibility, deletes a repo, or changes a ruleset (GBD-3.5).
"""
import base64, json, os, re, subprocess, urllib.error, urllib.parse, urllib.request

T = os.environ["GITHUB_TOKEN"]; APPLY = os.environ.get("APPLY") == "1"; DIR = os.environ["DIR"]
API = os.environ.get("GITHUB_API_URL", "https://api.github.com").rstrip("/")
CHECK = "ai-governance / verdict"; BRANCH = "governance/enforce-ai-governance"
GOV = "KyPython/ai-governance"
CALLER = ".github/workflows/ai-governance.yml"
PATTERNS = [f"{GOV}/.github/workflows/governance.yml@*", f"{GOV}/.github/actions/*@*"]  # GBD-3.4
BUMP_PREFIX = "ci/bump-ai-governance"  # open PRs from ci/bump-ai-governance* into the default branch are reused
PIN_RE = re.compile(r"KyPython/ai-governance/\.github/workflows/governance\.yml@([0-9a-f]{40})")


def api(method, path, body=None):
    req = urllib.request.Request(API + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": "token " + T, "Accept": "application/vnd.github+json",
                                          "X-GitHub-Api-Version": "2022-11-28"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            b = r.read(); return r.status, (json.loads(b) if b else None)
    except urllib.error.HTTPError as e:
        b = e.read()
        try: return e.code, json.loads(b)
        except Exception: return e.code, None
    except (urllib.error.URLError, TimeoutError, OSError) as e:  # network: report as a failed call, never as data
        return 599, {"message": f"network error: {e}"}


def pages(path):
    out, p = [], 1
    while True:
        s, d = api("GET", f"{path}{'&' if '?' in path else '?'}per_page=100&page={p}")
        if s != 200 or not d: return out
        out += d; p += 1
        if len(d) < 100: return out


def pages_strict(path):
    """Like pages(), but None if any page fails, so a transient error never reads as "nothing there"."""
    out, p = [], 1
    while True:
        s, d = api("GET", f"{path}{'&' if '?' in path else '?'}per_page=100&page={p}")
        if s != 200 or not isinstance(d, list): return None
        out += d; p += 1
        if len(d) < 100: return out


def q(ref):
    return urllib.parse.quote(ref, safe="")


def verdict_ok(repo, ref):
    s, c = api("GET", f"/repos/{repo}/commits/{q(ref)}/check-runs?check_name={q(CHECK)}&filter=latest")
    runs = (c or {}).get("check_runs", []) if s == 200 else []
    return runs[0]["conclusion"] if runs else None


class Unknown(Exception):
    """A read failed for a reason other than "not there" (network, 5xx, rate limit): never act on it."""


def caller(repo, ref):
    """(text, blob_sha) of the caller workflow on ref, or (None, None) when it does not exist (404 only)."""
    s, c = api("GET", f"/repos/{repo}/contents/{CALLER}?ref={q(ref)}")
    if s == 200:
        return base64.b64decode(c["content"]).decode(), c["sha"]
    if s == 404:
        return None, None
    raise Unknown(f"could not read {CALLER} on {ref} (HTTP {s})")


def pin_has_role_gate(pin):
    s, g = api("GET", f"/repos/{GOV}/contents/.github/workflows/governance.yml?ref={pin}")
    return s == 200 and "ROLES_URL" in base64.b64decode(g["content"]).decode()


def run_optin(args):
    env = dict(os.environ, GITHUB_TOKEN=T)
    p = subprocess.run([os.path.join(DIR, "optin.sh"), *args], capture_output=True, text=True, env=env)
    return p.returncode, (p.stdout + p.stderr).strip().replace("\n", " | ")


def allow_shared_paths(fn):
    """GBD-3.4: in a "selected Actions" repo, allow every ai-governance path. Returns a note or None."""
    s, ap = api("GET", f"/repos/{fn}/actions/permissions")
    if s != 200 or (ap or {}).get("allowed_actions") != "selected":
        return None
    s, sel = api("GET", f"/repos/{fn}/actions/permissions/selected-actions")
    if s != 200 or not isinstance((sel or {}).get("patterns_allowed"), list) \
            or not all(isinstance((sel or {}).get(k), bool) for k in ("github_owned_allowed", "verified_allowed")):
        return f"allow-list not changed: could not read it (HTTP {s})"  # never overwrite a list we could not read
    pats = sel["patterns_allowed"]
    missing = [p for p in PATTERNS if p not in pats]
    if not missing:
        return None
    if not APPLY:
        return "would allow " + ", ".join(missing)
    s, d = api("PUT", f"/repos/{fn}/actions/permissions/selected-actions",
               {"github_owned_allowed": sel["github_owned_allowed"],
                "verified_allowed": sel["verified_allowed"], "patterns_allowed": pats + missing})
    return ("allowed " if s in (200, 204) else f"could not allow (HTTP {s}) ") + ", ".join(missing)


def ensure_bump(fn, db, main_sha):
    """GBD-3.3: keep one open bump PR to main's SHA. Returns (status, note)."""
    prs = pages_strict(f"/repos/{fn}/pulls?state=all")
    if prs is None:
        return "error", "could not list pull requests; no bump PR opened this run"
    mine = [p for p in prs if (p.get("head") or {}).get("repo") and p["head"]["repo"]["full_name"] == fn
            and p["head"]["ref"].startswith(BUMP_PREFIX) and (p.get("base") or {}).get("ref") == db]
    open_prs = [p for p in mine if p.get("state") == "open"]
    branch = open_prs[0]["head"]["ref"] if open_prs else f"{BUMP_PREFIX}-{main_sha[:7]}"
    if not open_prs and any(p["head"]["ref"] == branch and p.get("state") == "closed" and not p.get("merged_at") for p in mine):
        return "declined", f"the bump PR for {main_sha[:7]} was closed without merging; not reopened"
    if not APPLY:
        return "todo", f"would bump the pin to {main_sha[:7]} on {branch}"
    text, blob = caller(fn, branch)
    if text is None:  # start the branch fresh from the default branch
        s, head = api("GET", f"/repos/{fn}/git/ref/heads/{q(db)}")
        sha = (head or {}).get("object", {}).get("sha") if s == 200 else None
        if not sha:
            return "error", f"could not read {db} (HTTP {s}); no bump PR opened"
        s, d = api("POST", f"/repos/{fn}/git/refs", {"ref": f"refs/heads/{branch}", "sha": sha})
        if s not in (200, 201):
            return "blocked", f"cannot create branch {branch}: {(d or {}).get('message', s)}"
        text, blob = caller(fn, branch)
    pins = set(PIN_RE.findall(text or ""))
    if len(pins) != 1:
        return "error", f"{branch}: expected one governance.yml pin, found {len(pins)}"
    if pins != {main_sha}:
        new = text.replace(f"governance.yml@{pins.pop()}", f"governance.yml@{main_sha}")
        s, d = api("PUT", f"/repos/{fn}/contents/{CALLER}", {
            "message": f"ci: bump ai-governance to {main_sha[:7]}", "branch": branch, "sha": blob,
            "content": base64.b64encode(new.encode()).decode()})
        if s not in (200, 201):
            return "blocked", f"cannot commit to {branch}: {(d or {}).get('message', s)}"
    if open_prs:
        return "bump-pr", f"bump PR open: {open_prs[0]['html_url']} (pin {main_sha[:7]})"
    body = (f"Bumps the shared governance pin to `{main_sha}` (ai-governance main). Opened by the governance "
            f"sweep (specs/governed-by-default, GBD-3.3). This PR's own `{CHECK}` run uses the new pin. Ky merges; "
            f"closing it without merging stops the sweep from reopening this SHA.")
    s, d = api("POST", f"/repos/{fn}/pulls", {"title": f"ci: bump ai-governance to {main_sha[:7]}",
                                              "head": branch, "base": db, "body": body})
    if s not in (200, 201):
        return "blocked", f"cannot open bump PR: {(d or {}).get('message', s)}"
    return "bump-pr", f"bump PR opened: {d['html_url']} (pin {main_sha[:7]})"


def main():
    skip = {}
    sf = os.environ.get("SKIP_FILE", "")
    if sf and os.path.exists(sf):
        for line in open(sf):
            if line.strip() and not line.startswith("#"):
                parts = line.split(None, 1); skip[parts[0]] = parts[1].strip() if len(parts) > 1 else ""
    s, user = api("GET", "/user")
    if s != 200 or not (user or {}).get("login"):
        msg = (f"the sweep could not reach GitHub (GET /user returned HTTP {s}); it will retry on the next run"
               if s == 599 or s >= 500 else f"the sweep token was rejected (GET /user returned HTTP {s}); replace SWEEP_TOKEN")
        print(f"::error::{msg[0].upper() + msg[1:]}.")
        if os.environ.get("RUNNER_TEMP"):
            open(os.path.join(os.environ["RUNNER_TEMP"], "sweep-failure"), "w").write(msg + "\n")
        raise SystemExit(3)
    me = user["login"]
    owners = {me}
    for m in pages("/user/memberships/orgs?state=active"):
        if m.get("role") == "admin": owners.add(m["organization"]["login"])
    repos = [r for r in pages("/user/repos?affiliation=owner,organization_member") if r["owner"]["login"] in owners]
    s, main = api("GET", f"/repos/{GOV}/commits/main")
    main_sha = (main or {}).get("sha") if s == 200 else None
    rows = []
    for r in sorted(repos, key=lambda r: r["full_name"].lower()):
        fn, db = r["full_name"], r["default_branch"]
        if r["archived"]: rows.append((fn, "skip", "archived")); continue
        if r["fork"]: rows.append((fn, "skip", "fork")); continue
        if fn in skip: rows.append((fn, "skip", skip[fn])); continue
        if r.get("size", 0) == 0 and api("GET", f"/repos/{fn}/commits?per_page=1")[0] != 200:
            rows.append((fn, "skip", "empty repo")); continue
        try:
            sweep_repo(fn, db, main_sha, rows)
        except Unknown as e:
            rows.append((fn, "error", f"{e}; stopped before any opt-in or protection change for this repo this run"))
    w = max(len(x[0]) for x in rows) if rows else 10
    for fn, st, note in rows:
        print(f"{fn:<{w}}  {st:<9}  {note}")
    print(f"\n{'APPLIED' if APPLY else 'REPORT ONLY (use --apply to write)'}: {len(rows)} repos")
    return rows


def sweep_repo(fn, db, main_sha, rows):
    """One repo. Raises Unknown before any write when a read is indeterminate."""
    text, _ = caller(fn, db)
    gated = text is not None or fn == GOV  # the gate repo calls its workflow locally (self-test.yml)
    notes, bump = [], None
    if text is not None:
        note = allow_shared_paths(fn)
        if note: notes.append(note)
        pins = set(PIN_RE.findall(text))
        if main_sha is None:
            notes.append("ai-governance main SHA unavailable; pin not checked")
        elif len(pins) != 1:
            notes.append(f"caller has {len(pins)} SHA pins of governance.yml; left alone, fix by hand")
        elif pins != {main_sha}:
            bump = ensure_bump(fn, db, main_sha)  # reported with the row below; never blocks protection
    def add(st, note):
        if bump:
            bst, bnote = bump
            st = bst if st == "ok" or bst in ("error", "blocked") else st
            note = "; ".join(x for x in (note, bnote) if x)
        rows.append((fn, st, "; ".join(notes + [note]) if note else "; ".join(notes)))
    s, prot = api("GET", f"/repos/{fn}/branches/{q(db)}/protection")
    if s not in (200, 403, 404):
        raise Unknown(f"could not read branch protection on {db} (HTTP {s})")
    required = [c["context"] for c in ((prot or {}).get("required_status_checks") or {}).get("checks", [])] if s == 200 else []
    if s == 200 and CHECK in required and (prot.get("enforce_admins") or {}).get("enabled"):
        if fn != GOV:
            ptext = text if text is not None else caller(fn, BRANCH)[0]
            m = PIN_RE.search(ptext or "")
            if ptext is not None and (not m or not pin_has_role_gate(m.group(1))):
                add("stale-pin", "protected, but the pinned gate predates the spec/role gate; bump the SHA in a PR"); return
        add("ok", "protected; verdict required; spec/role gate pinned" + ("" if gated else " (opt-in PR not merged yet)")); return
    prot_note = "branch protection unavailable (private repo on free plan: needs Pro/Team or public)" if s == 403 else None
    bs = api("GET", f"/repos/{fn}/branches/{q(BRANCH)}")[0]
    if bs not in (200, 404):
        raise Unknown(f"could not check branch {BRANCH} (HTTP {bs})")
    branch_exists = bs == 200
    if not gated and not branch_exists:
        if not APPLY: rows.append((fn, "todo", "would open opt-in PR")); return
        note = allow_shared_paths(fn)
        rc, out = run_optin([fn])
        rows.append((fn, "opened" if rc == 0 else "error", "; ".join(([note] if note else []) + [out]))); return
    ref = BRANCH if branch_exists else db
    v = verdict_ok(fn, ref)
    if v != "success":
        add("pending", "; ".join([f"verdict on {ref}: {v or 'not run yet'}"] + ([prot_note] if prot_note else []))); return
    if prot_note: add("blocked", prot_note); return
    if not APPLY: add("todo", "would apply protection model"); return
    rc, out = run_optin(["--protect", fn]); add("protected" if rc == 0 else "error", out)




if __name__ == "__main__":
    main()
