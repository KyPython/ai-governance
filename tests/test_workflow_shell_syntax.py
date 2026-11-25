"""Every shell `run:` script in the workflows and composite actions must pass `bash -n`.

Specs: specs/completion-gate-wiring (CGW-3.4 verdict step), specs/governed-by-default (GBD-3.1 failed sweep reporting).
A merge that corrupts a workflow script (as happened to sweep.yml and the governance verdict step) is caught here,
without network, secrets or running any script: `bash -n` only parses.
"""
import re
import subprocess
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
EXPRESSION = re.compile(r"\$\{\{.*?\}\}", re.DOTALL)
SHELLS = {"bash", "sh"}


def is_shell_step(step):
    shell = step.get("shell")
    if shell is None:
        return True  # default runner shell is bash on the Linux runners
    return Path(str(shell).split()[0]).name in SHELLS


def shell_steps(path):
    """Yield (job, step label, script) for each shell `run:` step in a workflow or composite action."""
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if "jobs" in doc:
        groups = [(name, job.get("steps") or []) for name, job in doc["jobs"].items()]
    else:
        groups = [("(composite)", (doc.get("runs") or {}).get("steps") or [])]
    for job, steps in groups:
        for i, step in enumerate(steps, 1):
            if isinstance(step.get("run"), str) and is_shell_step(step):
                label = step.get("name") or step.get("id") or f"step {i}"
                yield job, label, step["run"]


def bash_errors(path, only_step_id=None):
    problems = []
    doc_steps = list(shell_steps(path))
    for job, label, script in doc_steps:
        if only_step_id is not None and label != only_step_id:
            continue
        text = EXPRESSION.sub("GHX", script) + "\n"
        r = subprocess.run(["bash", "-n"], input=text, capture_output=True, text=True, timeout=30)
        if r.returncode:
            problems.append(f"{path.relative_to(ROOT)} job={job} step={label!r}: {r.stderr.strip()}")
    return problems, len(doc_steps)


def all_files():
    return sorted((ROOT / ".github/workflows").glob("*.yml")) + sorted((ROOT / ".github/actions").glob("*/action.yml"))


class WorkflowShellSyntax(unittest.TestCase):
    def test_CGW_3_4_verdict_step_script_is_valid_shell(self):
        """CGW-3.4: the governance verdict step (id: v) must parse as shell so the required-completion check can run."""
        problems, _ = bash_errors(ROOT / ".github/workflows/governance.yml", only_step_id="v")
        self.assertEqual(problems, [], "\n".join(problems))
        self.assertTrue(any(label == "v" for _, label, _ in shell_steps(ROOT / ".github/workflows/governance.yml")),
                        "verdict step (id: v) not found")

    def test_GBD_3_1_sweep_workflow_scripts_are_valid_shell(self):
        """GBD-3.1: the daily sweep workflow's scripts must parse, otherwise a failed sweep cannot be reported."""
        problems, count = bash_errors(ROOT / ".github/workflows/sweep.yml")
        self.assertGreater(count, 0, "no shell steps found in sweep.yml")
        self.assertEqual(problems, [], "\n".join(problems))

    def test_CGW_3_4_all_workflow_and_action_scripts_are_valid_shell(self):
        """CGW-3.4 / GBD-3.1: no workflow or composite-action shell step may have a syntax error."""
        problems, total = [], 0
        for path in all_files():
            p, n = bash_errors(path)
            problems += p
            total += n
        self.assertGreater(total, 0)
        self.assertEqual(problems, [], "\n".join(problems))


if __name__ == "__main__":
    unittest.main()
