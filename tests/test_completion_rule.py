"""The completion-claim rule in the canonical governance section (spec: specs/completion-gate-wiring, CGW-4)."""
import os
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARKER = "<!-- AI-GOVERNANCE:v1"

# CGW-4.1: the rule's wording is the contract, so the whole sentence is pinned here.
RULE_13 = (
    "13. **Done means a VERIFIED completion gate.** When the task's spec has a completion contract "
    "(`specs/<slug>/completion-contract.json` or `.kiro/specs/<slug>/completion-contract.json`), run "
    "`python3 completion-gate/completion_gate.py <contract> --evidence <file>` before claiming completion. "
    "`completion-gate/` is at the root of `KyPython/ai-governance`; in any other repo, run it from a checkout of "
    "`KyPython/ai-governance` at the caller's pinned SHA. In the completion message, quote the verdict line, the "
    "evidence path and the contract hash (the evidence file's `contract_hash`). FAILED or UNKNOWN means the task "
    "is not done; say so in those words. When no contract exists, say \"no completion contract; not "
    "gate-verified\". Never write, edit or delete a contract, pass an `--audit` file you authored, or edit the gate."
)


def read(name):
    with open(os.path.join(ROOT, name), encoding="utf-8") as fh:
        return fh.read()


def optin_refresh_code():
    """The Python block optin.sh runs to insert or refresh the canonical section in a repo's AGENTS.md."""
    m = re.search(r"python3 - <<'PY'\n(.*?)\nPY\n", read("scripts/optin.sh"), re.S)
    assert m, "optin.sh AGENTS.md block not found"
    return m.group(1)


def run_refresh(agents_md, section):
    with tempfile.TemporaryDirectory() as d:
        if agents_md is not None:
            with open(os.path.join(d, "AGENTS.md"), "w", encoding="utf-8") as fh:
                fh.write(agents_md)
        subprocess.run([sys.executable, "-c", optin_refresh_code()], cwd=d, check=True,
                       env=dict(os.environ, SECTION=section, PYTHONDONTWRITEBYTECODE="1"))
        with open(os.path.join(d, "AGENTS.md"), encoding="utf-8") as fh:
            return fh.read()


class CompletionRule(unittest.TestCase):
    def test_CGW_4_1_rule_13_is_present_once_with_exact_wording(self):
        lines = read("AGENTS.governance.md").splitlines()
        self.assertEqual([l for l in lines if l.startswith("13. ")], [RULE_13])
        self.assertEqual(lines.index(RULE_13) - 1, next(i for i, l in enumerate(lines) if l.startswith("12. ")),
                         "rule 13 must follow rule 12 in the Rules list")

    def test_CGW_4_2_repo_agents_md_carries_the_canonical_section_unchanged(self):
        canonical = read("AGENTS.governance.md")
        agents = read("AGENTS.md")
        self.assertIn(MARKER, agents)
        self.assertEqual(agents[agents.index(MARKER):], canonical,
                         "AGENTS.md must carry AGENTS.governance.md word for word from the marker on")

    def test_CGW_4_2_optin_delivers_rule_to_new_and_existing_repos_without_duplicates(self):
        section = read("AGENTS.governance.md")
        old_section = "\n".join(l for l in section.splitlines() if not l.startswith("13. ")) + "\n"
        local = "\n## Repo-specific rules\n- Keep this local rule.\n"
        cases = {
            "no AGENTS.md": None,
            "AGENTS.md without the section": "# Agent rules\n\nLocal notes.\n",
            "older 12-rule copy": "# Agent rules\n\n" + old_section + local,
            "current copy, refreshed again": "# Agent rules\n\n" + section + local,
        }
        for name, before in cases.items():
            with self.subTest(case=name):
                after = run_refresh(before, section)
                self.assertEqual(after.count(RULE_13), 1, "rule 13 must appear exactly once")
                self.assertEqual(after.count(MARKER), 1)
                self.assertIn(section.rstrip() + "\n", after, "section must be delivered unchanged in wording")
                if before and "Repo-specific rules" in before:
                    self.assertIn(local.strip(), after, "repo-specific content must survive the refresh")
                twice = run_refresh(after, section)
                self.assertEqual(twice, after, "a second refresh must change nothing")


if __name__ == "__main__":
    unittest.main()
