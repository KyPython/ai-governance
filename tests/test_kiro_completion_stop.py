"""The Kiro Stop hook script (spec: specs/completion-gate-wiring, CGW-5.1 to CGW-5.4)."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "scripts" / "kiro_completion_stop.py"


def git(*args, cwd):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "init.defaultBranch=main", *args],
                   cwd=cwd, check=True, capture_output=True)


def contract(*commands):
    c = json.loads((ROOT / "completion-gate/tests/fixtures/contract_valid.json").read_text())
    c["completion_criteria"] = [{"check_id": f"CHK-{i}", "command": cmd, "timeout_seconds": 60}
                                for i, cmd in enumerate(commands, 1)]
    return c


def py(code):
    return f"{sys.executable} -c {json.dumps(code)}"


class World:
    """A task repo cloned from a bare origin, and a gate repo whose origin/main holds completion-gate/."""

    def __init__(self, test, main_contract=None, gate_main=None):
        d = tempfile.TemporaryDirectory(prefix="kiro-stop-")
        test.addCleanup(d.cleanup)
        self.root = Path(d.name)
        self.evidence = self.root / "evidence"
        # gate repo
        gw = self.root / "gate-work"
        shutil.copytree(ROOT / "completion-gate", gw / "completion-gate", ignore=shutil.ignore_patterns("__pycache__"))
        if gate_main is not None:
            (gw / "completion-gate/completion_gate.py").write_text(gate_main)
        git("init", "-q", cwd=gw); git("add", ".", cwd=gw); git("commit", "-q", "-m", "gate", cwd=gw)
        git("clone", "-q", "--bare", str(gw), str(self.root / "gate.git"), cwd=self.root)
        git("clone", "-q", str(self.root / "gate.git"), str(self.root / "gate"), cwd=self.root)
        git("checkout", "-q", "-b", "some-other-branch", cwd=self.root / "gate")
        # The checked-out branch carries a committed sabotaged gate: only origin/main may be used.
        (self.root / "gate/completion-gate/completion_gate.py").write_text("raise SystemExit('checked-out branch must not be used')\n")
        git("commit", "-q", "-am", "sabotage", cwd=self.root / "gate")
        # task repo: main has the spec and (optionally) its contract
        tw = self.root / "task-work"
        (tw / "specs/demo").mkdir(parents=True)
        (tw / "specs/demo/requirements.md").write_text("# demo\n")
        if main_contract is not None:
            (tw / "specs/demo/completion-contract.json").write_text(json.dumps(main_contract))
        git("init", "-q", cwd=tw); git("add", ".", cwd=tw); git("commit", "-q", "-m", "spec", cwd=tw)
        git("clone", "-q", "--bare", str(tw), str(self.root / "task.git"), cwd=self.root)
        git("clone", "-q", str(self.root / "task.git"), str(self.root / "task"), cwd=self.root)
        self.task = self.root / "task"

    def commit(self, message):
        (self.task / "work.txt").write_text(message)
        git("add", ".", cwd=self.task)
        git("commit", "-q", "-m", message, cwd=self.task)

    def run(self, event=None, cwd=None):
        env = dict(os.environ, COMPLETION_GATE_REPO=str(self.root / "gate"),
                   COMPLETION_GATE_EVIDENCE_DIR=str(self.evidence), PYTHONDONTWRITEBYTECODE="1")
        stdin = json.dumps(event if event is not None else {"hook_event_name": "stop", "cwd": str(self.task)})
        r = subprocess.run([sys.executable, str(HOOK)], input=stdin, cwd=cwd or self.root, env=env,
                           capture_output=True, text=True, timeout=180)
        return r

    def tree(self):
        return sorted(str(p.relative_to(self.task)) for p in self.task.rglob("*") if ".git" not in p.parts)


class KiroStopHook(unittest.TestCase):
    def test_CGW_5_1_runs_the_main_branch_contract_and_shows_the_verdict(self):
        w = World(self, main_contract=contract(py("pass")))
        w.commit("feat: work\n\nSpec: specs/demo")
        r = w.run()
        self.assertEqual(r.returncode, 0, r.stderr)
        line = r.stdout.strip()
        self.assertTrue(line.startswith("completion gate: VERIFIED for specs/demo | evidence "), line)
        ev_path = line.split("| evidence ")[1].split(" |")[0]
        ev = json.loads(Path(ev_path).read_text())
        self.assertEqual(ev["verdict"], "VERIFIED")
        self.assertIn("contract_hash " + ev["contract_hash"], line)

    def test_CGW_5_1_failed_contract_says_the_task_is_not_done(self):
        w = World(self, main_contract=contract(py("import sys; sys.exit(4)")))
        w.commit("fix: x\n\nSpec: specs/demo")
        line = w.run().stdout.strip()
        self.assertIn("FAILED for specs/demo", line)
        self.assertIn("the task is not done", line)

    def test_CGW_5_1_local_edits_to_the_contract_do_not_loosen_it(self):
        w = World(self, main_contract=contract(py("import sys; sys.exit(1)")))
        (w.task / "specs/demo/completion-contract.json").write_text(json.dumps(contract(py("pass"))))
        w.commit("feat: loosen\n\nSpec: specs/demo")
        self.assertIn("FAILED for specs/demo", w.run().stdout)

    def test_CGW_5_1_gate_comes_from_origin_main_not_the_checked_out_branch(self):
        w = World(self, main_contract=contract(py("pass")))
        w.commit("feat: work\n\nSpec: specs/demo")
        self.assertIn("VERIFIED for specs/demo", w.run().stdout)  # the gate checkout's working tree is sabotaged

    def test_CGW_5_2_verified_needs_gate_exit_zero_and_the_contract_hash(self):
        right_hash = "'sha256:' + hashlib.sha256(open(sys.argv[1], 'rb').read()).hexdigest()"
        liars = {"right hash, exits 1": (right_hash, "1"), "wrong hash, exits 0": ("'sha256:' + '0' * 64", "0")}
        for name, (digest, code) in liars.items():
            with self.subTest(case=name):
                liar = ("import hashlib, json, sys\nev = sys.argv[sys.argv.index('--evidence') + 1]\n"
                        "json.dump({'verdict': 'VERIFIED', 'contract_hash': %s, 'verdict_reasons': []}, open(ev, 'w'))\n"
                        "sys.exit(%s)\n" % (digest, code))
                w = World(self, main_contract=contract(py("pass")), gate_main=liar)
                w.commit("feat: work\n\nSpec: specs/demo")
                out = w.run().stdout
                self.assertIn("UNKNOWN for specs/demo", out)
                self.assertNotIn("VERIFIED for", out)

    def test_CGW_5_2_non_object_evidence_is_not_gate_verified(self):
        liar = "import sys\nopen(sys.argv[sys.argv.index('--evidence') + 1], 'w').write('[1]')\n"
        w = World(self, main_contract=contract(py("pass")), gate_main=liar)
        w.commit("feat: work\n\nSpec: specs/demo")
        out = w.run().stdout
        self.assertIn("not gate-verified: the gate's evidence is not a JSON object", out)

    def test_CGW_5_2_unresolvable_cases_report_not_gate_verified(self):
        cases = {
            "no spec line": ("feat: work", None, "no completion contract; not gate-verified"),
            "two specs": ("feat: work\n\nSpec: specs/demo\nSpec: specs/other", None, "exactly one spec folder"),
            "spec outside spec dirs": ("feat: work\n\nSpec: src/app", None, "exactly one spec folder"),
            "no contract on main": ("feat: work\n\nSpec: specs/demo", None, "is not on origin/"),
        }
        for name, (message, _, expect) in cases.items():
            with self.subTest(case=name):
                w = World(self)
                w.commit(message)
                r = w.run()
                self.assertEqual(r.returncode, 0)
                self.assertIn(expect, r.stdout)
                self.assertNotIn("VERIFIED", r.stdout)

    def test_CGW_5_2_missing_gate_and_non_repo_and_bad_input_never_verify(self):
        w = World(self, main_contract=contract(py("pass")))
        w.commit("feat: work\n\nSpec: specs/demo")
        env = dict(os.environ, COMPLETION_GATE_REPO=str(w.root / "nowhere"), COMPLETION_GATE_EVIDENCE_DIR=str(w.evidence))
        r = subprocess.run([sys.executable, str(HOOK)], input=json.dumps({"cwd": str(w.task)}), env=env,
                           capture_output=True, text=True, timeout=60)
        self.assertIn("not gate-verified: cannot read completion-gate/", r.stdout)
        r = w.run(event={"cwd": str(w.root)})  # not a git repository
        self.assertIn("not gate-verified: not in a git repository", r.stdout)
        env = dict(os.environ, COMPLETION_GATE_REPO=str(w.root / "gate"), COMPLETION_GATE_EVIDENCE_DIR=str(w.evidence))
        r = subprocess.run([sys.executable, str(HOOK)], input="not json", cwd=w.task, env=env,
                           capture_output=True, text=True, timeout=180)
        self.assertEqual(r.returncode, 0)
        self.assertIn("VERIFIED for specs/demo", r.stdout, "bad stdin falls back to the current directory")

    def test_CGW_5_3_writes_only_its_evidence_and_never_blocks(self):
        w = World(self, main_contract=contract(py("import sys; sys.exit(1)")))
        w.commit("feat: work\n\nSpec: specs/demo")
        before = w.tree()
        status_before = subprocess.run(["git", "status", "--porcelain"], cwd=w.task, capture_output=True, text=True).stdout
        r = w.run()
        self.assertEqual(r.returncode, 0, "the hook must never block the agent")
        self.assertEqual(w.tree(), before)
        self.assertEqual(subprocess.run(["git", "status", "--porcelain"], cwd=w.task, capture_output=True, text=True).stdout,
                         status_before)
        self.assertEqual(len(list(w.evidence.glob("*.json"))), 1)

    def test_CGW_5_4_readme_lists_the_hook_and_the_rule_only_agents(self):
        text = (ROOT / "completion-gate/README.md").read_text()
        self.assertIn("## Agent wiring (CGW-5)", text)
        rule_only = text[text.index("- **Agents with no hook wired here (rule-only locally):**"):text.index("## Limits")]
        for agent in ("Codex", "Antigravity", "Cursor", "Claude Code", "Copilot", "Grok Bot"):
            self.assertIn(agent, rule_only)
        self.assertIn("scripts/kiro_completion_stop.py", text)


if __name__ == "__main__":
    unittest.main()
