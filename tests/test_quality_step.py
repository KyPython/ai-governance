"""Execute the reusable Python quality step against controlled tool outcomes.

Traceability: ROLLOUT-4.1, ROLLOUT-4.3.
"""

from pathlib import Path
import subprocess
import tempfile
import unittest


WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/governance.yml"
STEP_NAME = "Install, lint, type-check, test, build"


def quality_script():
    """Extract the actual named run block without adding a YAML dependency."""
    lines = WORKFLOW.read_text().splitlines()
    step = next(i for i, line in enumerate(lines) if line.strip() == f"- name: {STEP_NAME}")
    run = next(i for i in range(step + 1, len(lines)) if lines[i].strip() == "run: |")
    indent = len(lines[run]) - len(lines[run].lstrip()) + 2
    script = []
    for line in lines[run + 1:]:
        if line.strip() and not line.startswith(" " * indent):
            break
        script.append(line[indent:] if line.strip() else "")
    return "\n".join(script) + "\n"


class PythonQualityStepTests(unittest.TestCase):
    def execute_step(self, failing=None, tests_present=True):
        temporary = tempfile.TemporaryDirectory(prefix="ai-quality-step-")
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        commands = root / "bin"
        commands.mkdir()
        (root / "requirements.txt").write_text("ruff\nmypy\n")
        if tests_present:
            (root / "tests").mkdir()
        for tool in ("python", "pip", "ruff", "mypy", "pytest"):
            executable = commands / tool
            status = 9 if tool == failing else 0
            executable.write_text(f"#!/bin/sh\nprintf 'CALL {tool}\\n'\nexit {status}\n")
            executable.chmod(0o755)
        summary = root / "summary.md"
        runner_temp = root / "runner-temp"
        runner_temp.mkdir()
        result = subprocess.run(
            ["/bin/bash", "-c", quality_script()],
            cwd=root,
            env={
                "PATH": f"{commands}:/usr/bin:/bin",
                "PM": "python",
                "REQUIRE_TESTS": "true",
                "GITHUB_STEP_SUMMARY": str(summary),
                "RUNNER_TEMP": str(runner_temp),
            },
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result, summary.read_text() if summary.exists() else ""

    def test_successful_tools_complete_with_success_summaries(self):
        # AQ-4: healthy partition; these are the real step's emitted summaries.
        result, summary = self.execute_step()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for message in ("ruff check passed", "mypy passed", "pytest passed"):
            self.assertIn(message, summary)

    def test_ruff_failure_stops_the_quality_step(self):
        # AQ-1: independent oracle is the failing executable's exit status.
        result, summary = self.execute_step(failing="ruff")
        self.assertEqual(result.returncode, 9, result.stdout + result.stderr)
        self.assertNotIn("ruff check passed", summary)
        self.assertNotIn("CALL mypy", result.stdout)
        self.assertNotIn("CALL pytest", result.stdout)

    def test_mypy_failure_stops_before_tests(self):
        # AQ-2
        result, summary = self.execute_step(failing="mypy")
        self.assertEqual(result.returncode, 9, result.stdout + result.stderr)
        self.assertNotIn("mypy passed", summary)
        self.assertNotIn("CALL pytest", result.stdout)

    def test_pytest_failure_fails_the_quality_step(self):
        # AQ-3
        result, summary = self.execute_step(failing="pytest")
        self.assertEqual(result.returncode, 9, result.stdout + result.stderr)
        self.assertNotIn("pytest passed", summary)

    def test_install_failure_remains_nonzero(self):
        # AQ-5: positive control for the fixture and pre-existing install behavior.
        result, _ = self.execute_step(failing="pip")
        self.assertEqual(result.returncode, 9, result.stdout + result.stderr)
        self.assertNotIn("CALL ruff", result.stdout)

    def test_required_missing_tests_remain_a_failure(self):
        # AQ-5: preserve the existing missing-test guard.
        result, _ = self.execute_step(tests_present=False)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("No tests found", result.stdout)


if __name__ == "__main__":
    unittest.main()
