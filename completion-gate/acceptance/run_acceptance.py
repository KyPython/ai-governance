#!/usr/bin/env python3
"""Run the neutral Completion Gate acceptance suite against one entry directory.

usage: python3 run_acceptance.py <entry_dir> <out.json>

Writes {"entry", "total", "passed", "failed", "errors", "hard_gate_violations", "results"}.
The suite runs in a child process (own session, wall-clock bounded) so a hostile or broken entry
cannot crash this runner. Tests the child never reported are recorded as "error". If the entry
cannot be imported, every test is "error".
"""
import io
import json
import os
import signal
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SUITE_TIMEOUT = 170  # seconds; whole suite must stay under 3 minutes
RANK = {"pass": 0, "fail": 1, "error": 2}


def _flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            for t in _flatten(item):
                yield t
        else:
            yield item


def _name(test):
    return getattr(test, "test_case", test).id().split(".")[-1]


def load_suite():
    sys.path.insert(0, HERE)
    sys.dont_write_bytecode = True
    import test_acceptance
    return unittest.defaultTestLoader.loadTestsFromModule(test_acceptance)


class Rec(unittest.TestResult):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.res = {}

    def _set(self, test, status):
        n = _name(test)
        if RANK[status] >= RANK.get(self.res.get(n, "pass"), 0):
            self.res[n] = status

    def addSuccess(self, test):
        self.res.setdefault(_name(test), "pass")

    def addFailure(self, test, err):
        self._set(test, "fail")

    def addError(self, test, err):
        self._set(test, "error")

    def addSkip(self, test, reason):
        self._set(test, "error")  # suite never skips; a skip would hide a gap

    def addExpectedFailure(self, test, err):
        self._set(test, "error")

    def addUnexpectedSuccess(self, test):
        self._set(test, "error")

    def addSubTest(self, test, subtest, err):
        if err is None:
            return
        self._set(test, "fail" if issubclass(err[0], AssertionError) else "error")


def child(entry, out_path):
    os.environ["ENTRY_DIR"] = entry
    suite = load_suite()
    rec = Rec()
    suite.run(rec)
    with open(out_path, "w") as fh:
        json.dump(rec.res, fh)


def parent(entry, out_path):
    entry = os.path.abspath(entry)
    os.environ["ENTRY_DIR"] = entry
    env = dict(os.environ, ENTRY_DIR=entry, PYTHONDONTWRITEBYTECODE="1")
    ids = sorted(_name(t) for t in _flatten(load_suite()))
    results = {i: "error" for i in ids}
    note = None
    fd, tmp_json = tempfile.mkstemp(prefix="acc-res-", suffix=".json")
    os.close(fd)
    os.unlink(tmp_json)
    proc = subprocess.Popen([sys.executable, os.path.abspath(__file__), "--child", entry, tmp_json],
                            env=env, cwd=tempfile.gettempdir(), start_new_session=True,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        proc.wait(timeout=SUITE_TIMEOUT)
    except subprocess.TimeoutExpired:
        note = "suite exceeded %d s; unreported tests recorded as error" % SUITE_TIMEOUT
    finally:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except OSError:
            pass
        try:
            proc.wait(timeout=10)
        except Exception:
            pass
    if os.path.exists(tmp_json):
        try:
            with open(tmp_json) as fh:
                for k, v in json.load(fh).items():
                    if k in results and v in RANK:
                        results[k] = v
        except (ValueError, OSError):
            note = "child result file unreadable"
        finally:
            os.unlink(tmp_json)
    elif note is None:
        note = "child produced no results (crashed); all tests recorded as error"
    failed = sorted(k for k, v in results.items() if v == "fail")
    errors = sorted(k for k, v in results.items() if v == "error")
    report = {"entry": entry, "total": len(results),
              "passed": sum(1 for v in results.values() if v == "pass"),
              "failed": failed, "errors": errors,
              "hard_gate_violations": sorted(k for k, v in results.items()
                                             if k.endswith("_HARDGATE") and v != "pass"),
              "results": results}
    if note:
        report["note"] = note
    with open(out_path, "w") as fh:
        json.dump(report, fh, indent=2, sort_keys=True)
    print("entry=%s total=%d passed=%d failed=%d errors=%d hard_gate_violations=%d"
          % (entry, report["total"], report["passed"], len(failed), len(errors),
             len(report["hard_gate_violations"])))
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--child":
        child(sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 3:
        sys.exit(parent(sys.argv[1], sys.argv[2]))
    else:
        sys.stderr.write("usage: python3 run_acceptance.py <entry_dir> <out.json>\n")
        sys.exit(2)
