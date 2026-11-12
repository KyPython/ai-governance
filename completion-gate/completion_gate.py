#!/usr/bin/env python3
"""Completion Gate runner (Spec COMP + Amendment A1). Standard library only.

TRUST BOUNDARY (COMP-7.1): runs contract commands with the ambient permissions of the invoking user.
It is NOT an operating-system sandbox and provides no file, network or process isolation.
Only run contracts a human wrote. Fail-closed: any doubt yields UNKNOWN, never VERIFIED.
It never edits authorization scopes or the authorization gate (COMP-7.2).

Usage: completion_gate.py <contract.json> [--evidence FILE] [--audit FILE]
Exit:  0 VERIFIED, 1 FAILED or UNKNOWN, 2 usage error or missing/invalid contract.
"""
import argparse, contextlib, hashlib, json, os, signal, subprocess, sys, tempfile, time, uuid
from datetime import datetime, timezone
from contract_validator import FAIL_MAP, UNKNOWN_MAP, validate_contract, validate_file

S = {"active": [], "results": []}  # run state shared with the signal handler


def now(): return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_check(check):
    """Run one check in its own process group. 124 = timeout (whole group killed), 127 = could not run (A1-D3)."""
    t, start, out, err = time.monotonic(), now(), "", ""
    try:
        p = subprocess.Popen(check["command"], shell=True, stdout=-1, stderr=-1, text=True, errors="replace", start_new_session=True)
        S["active"].append(p)
        try: out, err = p.communicate(timeout=check["timeout_seconds"]); code = p.returncode
        except subprocess.TimeoutExpired:
            code = 124
            with contextlib.suppress(OSError): os.killpg(p.pid, signal.SIGKILL)
            with contextlib.suppress(subprocess.TimeoutExpired): out, err = p.communicate(timeout=5)
            err += f"\ncheck timed out after {check['timeout_seconds']} s"
        finally: S["active"].remove(p)
    except Exception as e: code, err = 127, f"could not run check: {e!r}"
    return {"check_id": check.get("check_id"), "command": check.get("command"), "timestamp_start": start, "timestamp_end": now(),
            "duration_seconds": round(time.monotonic() - t, 3), "exit_code": code, "passed": code == 0, "stdout": out, "stderr": err}


def run_all_checks(criteria):
    """Run checks sequentially; results so far stay visible to the signal handler."""
    S["results"] = []
    for c in criteria:
        S["results"].append(run_check(c))
    return S["results"]


def evaluate_verdict(results, contract, audit_data):
    """Pure. FAILED > UNKNOWN > VERIFIED. Reads exit_code only; any doubt is UNKNOWN (COMP-4, A1-I3, A1-I4)."""
    errs, audit, failed, ids = validate_contract(contract), {} if audit_data is None else audit_data, [], []
    unknown = (["contract invalid: " + "; ".join(errs[:3])] if errs else []) + ([] if isinstance(audit, dict) else ["audit data is not a JSON object"])
    audit = audit if isinstance(audit, dict) else {}
    for r in results if isinstance(results, list) else [None]:
        cid, code = (r.get("check_id"), r.get("exit_code")) if isinstance(r, dict) else (None, None)
        if not isinstance(cid, str) or type(code) is not int: unknown.append(f"malformed check result: {str(r)[:80]}"); continue
        ids.append(cid)
        if code in (124, 127): unknown.append(f"check {cid} {'timed out' if code == 124 else 'could not run'} (exit {code})")
        elif code: failed.append(f"check {cid} failed (exit {code})")
    if not errs and sorted(ids) != sorted(c["check_id"] for c in contract["completion_criteria"]):
        unknown.append(f"check results {sorted(ids)} do not match the declared checks")
    if not errs and contract.get("periodic_evidence") is not None and not (isinstance(audit.get("checkpoints"), list) and audit["checkpoints"]):
        unknown.append("periodic_evidence declared but no checkpoints supplied (W-3)")
    for flags, bucket in ((FAIL_MAP, failed), (UNKNOWN_MAP, unknown)):
        for k, meaning in flags.items():
            v = audit.get(k, False)
            if not isinstance(v, (bool, int, float, list, dict)): unknown.append(f"{k}: indeterminate value {v!r}")
            elif v: bucket.append(f"{k}: {meaning}")
    if failed or unknown: return ("FAILED" if failed else "UNKNOWN"), failed + unknown
    return "VERIFIED", [f"all {len(ids)} declared checks exited 0", "no violation or gap reported in audit data"]


def build_evidence(contract, checks, verdict, reasons, audit_data, t0):
    """Evidence record (COMP-3). Audit flags and security events are retained verbatim (W-4)."""
    a, c = (x if isinstance(x, dict) else {} for x in (audit_data, contract))
    ra, cps = a.get("reasoning_audit"), a.get("checkpoints")
    sec = {"deny_events": [], "bypasses_detected": 0, "credential_grants_used": [], "external_sends": []}
    ev = {"run_id": "run-" + uuid.uuid4().hex[:12], "task_id": str(c.get("task_id", "UNKNOWN")), "timestamp_start": t0 or now(),
          "contract_hash": "sha256:" + hashlib.sha256(json.dumps(contract, sort_keys=True, default=str).encode()).hexdigest(),
          "timestamp_end": now(), "checks": checks, "verdict": verdict, "verdict_reasons": list(reasons),
          "security_audit": {**sec, **{k: a[k] for k in (*sec, *FAIL_MAP, *UNKNOWN_MAP) if k in a}},
          "reasoning_audit": {"reasoning_transparency": "UNKNOWN", "self_override_suspected": False, **(ra if isinstance(ra, dict) else {})},
          "checkpoints": cps if isinstance(cps, list) else []}
    return {**ev, "configuration": a["configuration"]} if isinstance(a.get("configuration"), dict) else ev


def write_evidence(path, data):
    """Atomic write (temp file + os.replace). On failure dump to stdout with verdict UNKNOWN and exit 1 (COMP-6.4)."""
    tmp = None
    try:
        text = json.dumps(data, indent=2)
        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(path)), prefix=".evidence-", suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f: f.write(text)
        os.replace(tmp, path)
    except (OSError, TypeError, ValueError) as e:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)
        reasons = list(data.get("verdict_reasons", [])) + [f"evidence write failed: {e}"]
        print(json.dumps(dict(data, verdict="UNKNOWN", verdict_reasons=reasons), indent=2, default=str)); sys.exit(1)


def finish(verdict, reasons):
    """Build and write this run's evidence; the hash covers the contract file's raw bytes."""
    ev = dict(build_evidence(S["contract"], S["results"], verdict, reasons, S["audit"], S["t0"]), contract_hash=S["hash"])
    write_evidence(S["path"] or f"evidence-{ev['run_id']}.json", ev)
    return S["path"] or f"evidence-{ev['run_id']}.json"


def on_signal(signum, frame):
    """COMP-6.3 / A1-I6: ignore further signals, kill every running check's process group, record UNKNOWN, exit 1."""
    for s in (signal.SIGINT, signal.SIGTERM): signal.signal(s, signal.SIG_IGN)  # no re-entry during the write
    for p in list(S["active"]):
        with contextlib.suppress(OSError): os.killpg(p.pid, signal.SIGKILL)
    finish("UNKNOWN", [f"interrupted by signal {signal.Signals(signum).name}"]); sys.exit(1)


def main(argv):
    ap = argparse.ArgumentParser(prog="completion_gate.py", add_help=False, allow_abbrev=False)
    for flag in ("contract", "--evidence", "--audit"):
        ap.add_argument(flag)
    ap.add_argument("-h", "--help", action="store_true")
    try: a = ap.parse_args(argv)
    except SystemExit: return 2  # argparse has already written the usage error to stderr
    if a.help:
        ap.print_usage(sys.stderr)
        return 2
    try: raw = open(a.contract, "rb").read()
    except OSError: raw = None
    status, _, errs = validate_file(a.contract)
    S.update(results=[], t0=now(), path=a.evidence, contract=None if status else json.loads(raw), audit=None,
             hash="sha256:" + (hashlib.sha256(raw).hexdigest() if raw is not None else "unavailable"))
    if status:
        print("completion_gate: invalid contract: " + "; ".join(errs), file=sys.stderr)
        finish("UNKNOWN", errs)
        return 2
    if a.audit is not None:  # an empty path is an unreadable audit file (UNKNOWN), never "no audit"
        try: S["audit"] = json.load(open(a.audit, encoding="utf-8"))
        except (OSError, ValueError) as e: S["audit"] = f"unreadable audit file: {e}"
        S["audit"] = S["audit"] if isinstance(S["audit"], dict) else [S["audit"]]  # non-object audit -> UNKNOWN
    for s in (signal.SIGINT, signal.SIGTERM): signal.signal(s, on_signal)
    verdict, reasons = evaluate_verdict(run_all_checks(S["contract"]["completion_criteria"]), S["contract"], S["audit"])
    print(f"{verdict} {finish(verdict, reasons)}")
    return 0 if verdict == "VERIFIED" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
