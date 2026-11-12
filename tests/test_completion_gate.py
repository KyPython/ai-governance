"""Repo-level checks for the imported Completion Gate (spec: specs/completion-gate-wiring, CGW-1).

The gate's own tests and its frozen acceptance suite run unchanged as subprocesses. The acceptance suite's
superseded 60-line test is excluded here and replaced by the 120-counted-line check (A1-D1, CGW-1.4).
"""
import ast
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import tokenize
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GATE_DIR = os.path.join(ROOT, "completion-gate")
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
SUPERSEDED = {"test_A1_D1_line_budget_le_60"}  # replaced by test_CGW_1_4_A1_D1_line_budget_le_120


def counted_lines(path):
    """A1-D1: lines that are not blank, comment-only, or docstring lines."""
    raw = open(path, "rb").read()
    doc = set()
    for node in ast.walk(ast.parse(raw)):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
                doc.update(range(first.lineno, first.end_lineno + 1))
    skip = {tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT,
            tokenize.ENDMARKER, tokenize.ENCODING}
    code = set()
    for tok in tokenize.tokenize(io.BytesIO(raw).readline):
        if tok.type not in skip:
            code.update(range(tok.start[0], tok.end[0] + 1))
    return len(code - doc)


class CompletionGateImport(unittest.TestCase):
    def test_CGW_1_1_layout(self):
        for rel in ("completion_gate.py", "contract_validator.py", "completion_aggregator.py", "README.md",
                    "schemas/completion-contract-v1.json", "schemas/completion-evidence-v1.json",
                    "tests/test_contract_schema.py", "tests/test_judge_findings.py",
                    "acceptance/test_acceptance.py", "acceptance/run_acceptance.py", "SHA256SUMS"):
            self.assertTrue(os.path.isfile(os.path.join(GATE_DIR, rel)), rel)

    def test_CGW_1_2_checksums_cover_every_file_and_match(self):
        listed = {}
        with open(os.path.join(GATE_DIR, "SHA256SUMS"), encoding="utf-8") as fh:
            for line in fh:
                digest, rel = line.rstrip("\n").split("  ", 1)
                listed[rel] = digest
        on_disk = set()
        for dirpath, dirnames, files in os.walk(GATE_DIR):
            dirnames[:] = [d for d in dirnames if d != "__pycache__"]
            for f in files:
                rel = os.path.relpath(os.path.join(dirpath, f), GATE_DIR)
                if rel != "SHA256SUMS" and not f.endswith(".pyc"):
                    on_disk.add(rel)
        self.assertEqual(sorted(on_disk), sorted(listed), "SHA256SUMS must list exactly the imported files")
        for rel, digest in listed.items():
            with open(os.path.join(GATE_DIR, rel), "rb") as fh:
                self.assertEqual(hashlib.sha256(fh.read()).hexdigest(), digest, rel)

    def test_CGW_1_4_gate_unit_tests_pass(self):
        r = subprocess.run([sys.executable, "-m", "unittest", "discover", "tests"], cwd=GATE_DIR, env=ENV,
                           capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])

    def test_CGW_1_4_acceptance_suite_no_hard_gate_violations(self):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "acceptance.json")
            subprocess.run([sys.executable, os.path.join(GATE_DIR, "acceptance", "run_acceptance.py"), GATE_DIR, out],
                           cwd=d, env=ENV, capture_output=True, text=True, timeout=400)
            report = json.load(open(out, encoding="utf-8"))
        self.assertGreaterEqual(report["total"], 125, "acceptance suite ran fewer tests than frozen")
        self.assertEqual(report["hard_gate_violations"], [])
        self.assertEqual(report["errors"], [])
        self.assertEqual(sorted(report["failed"]), sorted(SUPERSEDED),
                         "only the superseded 60-line test may fail; if it now passes, update this test")

    def test_CGW_1_4_A1_D1_line_budget_le_120(self):
        n = counted_lines(os.path.join(GATE_DIR, "completion_gate.py"))
        self.assertLessEqual(n, 120, "completion_gate.py has %d counted lines (A1-D1 limit 120)" % n)


if __name__ == "__main__":
    unittest.main()
