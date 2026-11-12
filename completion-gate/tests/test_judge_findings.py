"""Regression tests for the three defects the bake-off judge found in the Kiro entry (bakeoff/RESULT.md)."""
import json, os, shlex, signal, subprocess, sys, tempfile, time, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GATE = os.path.join(ROOT, "completion_gate.py")
sys.path.insert(0, ROOT)
import completion_gate  # noqa: E402

with open(os.path.join(ROOT, "tests", "fixtures", "contract_valid.json")) as f:
    BASE = json.load(f)


def contract(d, command="true", timeout=20):
    c = dict(BASE, completion_criteria=[{"check_id": "A", "command": command, "timeout_seconds": timeout}])
    p = os.path.join(d, "c.json")
    json.dump(c, open(p, "w"))
    return p


def cli(args, cwd):
    return subprocess.run([sys.executable, GATE, *args], cwd=cwd, capture_output=True, text=True, timeout=60,
                          env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))


class TestJudgeFindings(unittest.TestCase):
    def test_empty_audit_path_is_unknown_not_ignored(self):  # A1-I2/A1-I3: was fail-open
        with tempfile.TemporaryDirectory() as d:
            r = cli([contract(d), "--evidence", "e.json", "--audit", ""], d)
            self.assertEqual(r.returncode, 1, r.stderr)
            self.assertEqual(json.load(open(os.path.join(d, "e.json")))["verdict"], "UNKNOWN")

    def test_abbreviated_flags_rejected(self):  # A1-I2: unknown flag -> exit 2
        with tempfile.TemporaryDirectory() as d:
            for flag in ("--evid", "--aud", "--he"):
                with self.subTest(flag=flag):
                    r = cli([contract(d), flag, "x.json"], d)
                    self.assertEqual(r.returncode, 2)
                    self.assertFalse(os.path.exists(os.path.join(d, "x.json")))

    def test_signal_handler_ignores_further_signals(self):  # COMP-6.3: no re-entry during the evidence write
        seen = []
        real = completion_gate.finish
        old = {s: signal.getsignal(s) for s in (signal.SIGINT, signal.SIGTERM)}
        completion_gate.finish = lambda v, r: seen.append([signal.getsignal(s) for s in (signal.SIGINT, signal.SIGTERM)])
        try:
            with self.assertRaises(SystemExit):
                completion_gate.on_signal(signal.SIGTERM, None)
        finally:
            completion_gate.finish = real
            for s, h in old.items():
                signal.signal(s, h)
        self.assertEqual(seen, [[signal.SIG_IGN, signal.SIG_IGN]])

    def test_double_sigterm_still_writes_unknown_once(self):
        with tempfile.TemporaryDirectory() as d:
            cmd = "%s -c %s" % (shlex.quote(sys.executable), shlex.quote("import time;time.sleep(30)"))
            p = subprocess.Popen([sys.executable, GATE, contract(d, cmd, 60), "--evidence", "e.json"], cwd=d,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                 env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
            time.sleep(1.0)
            p.send_signal(signal.SIGTERM); p.send_signal(signal.SIGTERM)
            out, err = p.communicate(timeout=20)
            self.assertEqual(p.returncode, 1, err)
            ev = json.load(open(os.path.join(d, "e.json")))
            self.assertEqual(ev["verdict"], "UNKNOWN")
            self.assertEqual(sorted(os.listdir(d)), ["c.json", "e.json"])


if __name__ == "__main__":
    unittest.main()
