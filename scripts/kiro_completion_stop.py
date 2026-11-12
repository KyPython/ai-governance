#!/usr/bin/env python3
"""Kiro `Stop` hook: run the completion gate for the task in the current repo (spec specs/completion-gate-wiring, CGW-5).

The hook's own code never blocks the agent and writes nothing except its evidence file (CGW-5.3); the contract's
commands, like any contract, run in the working tree and can do whatever they do (CGW-6.1). It always exits 0
and prints one result: the verdict line, evidence path and contract hash, or "not gate-verified" with the
reason (CGW-5.2). It never prints VERIFIED unless the gate itself returned VERIFIED for the contract it ran.

How it resolves the task (CGW-5.1):
- spec: the `Spec:` line in the HEAD commit message, parsed with the policy spec gate's rule;
- contract: `<spec>/completion-contract.json` read from the repo's `origin/<default branch>`, as CI does
  (never the working tree, so a local edit cannot loosen it);
- gate: `completion-gate/` from `KyPython/ai-governance`'s `origin/main`, exported with `git archive` from the
  local checkout named by COMPLETION_GATE_REPO (default ~/ai-governance), whatever branch it has checked out.

Limits: it does not fetch, so the contract and gate are only as fresh as each checkout's last `git fetch`; the gate is
the local `origin/main`, not a pinned SHA; only the HEAD commit's Spec line is read; there is no caching, so a slow
contract runs at every stop (GATE_TIMEOUT seconds at most).
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
import time

SPEC_DIRS = ("specs", ".kiro/specs")
EVIDENCE_DIR = os.path.expanduser(os.environ.get("COMPLETION_GATE_EVIDENCE_DIR", "~/.local/share/completion-gate/evidence"))
GATE_REPO = os.path.expanduser(os.environ.get("COMPLETION_GATE_REPO", "~/ai-governance"))
GATE_TIMEOUT = 600


def git(*args, cwd):
    try:
        r = subprocess.run(["git", *args], cwd=cwd, capture_output=True)
    except OSError:  # missing directory or no git
        return None
    return r.stdout if r.returncode == 0 else None


def say(text):
    print("completion gate: " + text)
    return 0


def spec_from_message(message):
    """Same Spec-line rule as the policy spec gate (governance.yml); returns the single valid spec or a reason."""
    folders = set()
    for m in re.finditer(r"(?im)^\W*specs?\W*:[\s*`]*([\w./-]+)", message):
        folders.add(re.sub(r"/(requirements|design|tasks)\.md$", "", m.group(1)).strip("/"))
    valid = sorted(f for f in folders
                   if any(f.startswith(d + "/") and f.count("/") == d.count("/") + 1 for d in SPEC_DIRS)
                   and re.fullmatch(r"[A-Za-z0-9_-][A-Za-z0-9._-]*", f.rsplit("/", 1)[-1]))
    if not folders:
        return None, "the HEAD commit message has no Spec: line"
    if len(valid) != 1 or len(folders) != 1:
        return None, "the HEAD commit message must name exactly one spec folder (found %s)" % ", ".join(sorted(folders))
    return valid[0], None


def main():
    try:
        event = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        event = {}
    cwd = event.get("cwd") if isinstance(event, dict) and isinstance(event.get("cwd"), str) else os.getcwd()
    top = git("rev-parse", "--show-toplevel", cwd=cwd)
    if top is None:
        return say("not gate-verified: not in a git repository")
    root = top.decode().strip()
    message = (git("log", "-1", "--format=%B", cwd=root) or b"").decode("utf-8", "replace")
    spec, why = spec_from_message(message)
    if spec is None:
        return say("no completion contract; not gate-verified (%s)" % why)
    head = (git("symbolic-ref", "--short", "refs/remotes/origin/HEAD", cwd=root) or b"").decode().strip()
    if not head:  # no origin/HEAD: use whichever of origin/main or origin/master exists
        head = next((b for b in ("origin/main", "origin/master") if git("rev-parse", "--verify", "-q", b, cwd=root)), "origin/main")
    contract = git("show", "%s:%s/completion-contract.json" % (head, spec), cwd=root)
    if contract is None:
        return say("no completion contract; not gate-verified (%s/completion-contract.json is not on %s)" % (spec, head))
    tar = git("archive", "--format=tar", "origin/main", "completion-gate", cwd=GATE_REPO)
    if tar is None:
        return say("not gate-verified: cannot read completion-gate/ from origin/main in %s" % GATE_REPO)
    with tempfile.TemporaryDirectory(prefix="completion-gate-") as work:
        path = os.path.join(work, "gate.tar")
        with open(path, "wb") as fh:
            fh.write(tar)
        with tarfile.open(path) as t:
            members = t.getmembers()
            if any(m.name.startswith(("/", "..")) or "/../" in m.name or not (m.isfile() or m.isdir()) for m in members):
                return say("not gate-verified: unexpected entries in the completion-gate archive")
            t.extractall(work, members=members)
        cpath = os.path.join(work, "contract.json")
        with open(cpath, "wb") as fh:
            fh.write(contract)
        os.makedirs(EVIDENCE_DIR, exist_ok=True)
        sha = (git("rev-parse", "--short=12", "HEAD", cwd=root) or b"unknown").decode().strip()
        evidence = os.path.join(EVIDENCE_DIR, "%s-%s-%s.json" % (os.path.basename(root), sha, time.strftime("%Y%m%dT%H%M%S")))
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        try:
            r = subprocess.run([sys.executable, "-E", "-s", "-B", os.path.join(work, "completion-gate", "completion_gate.py"),
                                cpath, "--evidence", evidence], cwd=root, capture_output=True, text=True, env=env,
                               timeout=GATE_TIMEOUT)
        except subprocess.TimeoutExpired:
            return say("not gate-verified: the gate did not finish within %d s" % GATE_TIMEOUT)
    want = "sha256:" + hashlib.sha256(contract).hexdigest()
    try:
        with open(evidence, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return say("not gate-verified: the gate wrote no readable evidence (exit %s)" % r.returncode)
    if not isinstance(data, dict):
        return say("not gate-verified: the gate's evidence is not a JSON object (exit %s)" % r.returncode)
    verdict = data.get("verdict")
    if verdict not in ("VERIFIED", "FAILED", "UNKNOWN") or (verdict == "VERIFIED" and (r.returncode != 0 or data.get("contract_hash") != want)):
        verdict = "UNKNOWN"
    reasons = data.get("verdict_reasons") if isinstance(data.get("verdict_reasons"), list) else []
    note = "" if verdict == "VERIFIED" else " - the task is not done (%s)" % "; ".join(str(x)[:200] for x in reasons[:3])
    return say("%s for %s | evidence %s | contract_hash %s%s" % (verdict, spec, evidence, data.get("contract_hash", want), note))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # never block the agent; never claim verification on a crash
        print("completion gate: not gate-verified: hook error %s" % type(exc).__name__)
        sys.exit(0)
