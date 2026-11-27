"""Offline behavior test for the text scripts/optin.sh produces (ESE-15.1, ESE-15.6).

optin.sh is run end to end with stub `curl` and `git` programs on PATH, so no
network or real repository is touched. The stubs capture the contract file the
script writes and the pull-request body it POSTs. The test asserts on that
generated output, not on the script source.
"""

import json
import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "optin.sh"

CURL_STUB = r"""#!/usr/bin/env python3
import json, os, sys
a = sys.argv[1:]
url = a[-1]
out = a[a.index("-o") + 1] if "-o" in a else None
method = a[a.index("-X") + 1] if "-X" in a else "GET"
data = a[a.index("-d") + 1] if "-d" in a else None
code, body = "200", "{}"
if url.endswith("/branches/governance/enforce-ai-governance"):
    code = "404"
elif "/commits/" in url:
    body = json.dumps({"sha": "0" * 40})
elif "AGENTS.governance.md" in url:
    body = "<!-- AI-GOVERNANCE:v1 -->\n"
elif "ai-governance.yml" in url:
    body = "name: x\n"
elif url.endswith("/user"):
    body = json.dumps({"login": "tester", "id": 1})
elif method == "POST" and url.endswith("/pulls"):
    open(os.path.join(os.environ["CAPTURE"], "pr.json"), "w").write(data)
    body = json.dumps({"html_url": "https://example.invalid/pr/1"})
elif url.endswith("/repos/KyPython/target"):
    body = json.dumps({"default_branch": "main"})
if out:
    open(out, "w").write(body)
    sys.stdout.write(code)
else:
    sys.stdout.write(body)
"""

GIT_STUB = r"""#!/usr/bin/env python3
import os, shutil, sys
a = sys.argv[1:]
while a[:1] == ["-c"]:
    a = a[2:]
if a[:1] == ["clone"]:
    os.makedirs(os.path.join(a[-1], ".systems-thinking", "contracts"))
elif a[:1] == ["commit"]:
    d = ".systems-thinking/contracts"
    for n in os.listdir(d):
        shutil.copy(os.path.join(d, n), os.path.join(os.environ["CAPTURE"], "contract.json"))
"""


def run_optin():
    with tempfile.TemporaryDirectory() as d:
        bindir = Path(d, "bin")
        bindir.mkdir()
        for name, text in (("curl", CURL_STUB), ("git", GIT_STUB)):
            p = bindir / name
            p.write_text(text)
            p.chmod(p.stat().st_mode | stat.S_IEXEC)
        cap = Path(d, "cap")
        cap.mkdir()
        env = dict(os.environ, PATH=f"{bindir}{os.pathsep}{os.environ['PATH']}",
                   GITHUB_TOKEN="stub", CAPTURE=str(cap))
        res = subprocess.run(["bash", str(SCRIPT), "target"], capture_output=True,
                             text=True, timeout=60, env=env)
        out = {"result": res}
        if (cap / "contract.json").exists():
            out["contract"] = json.loads((cap / "contract.json").read_text())
        if (cap / "pr.json").exists():
            out["pr_body"] = json.loads((cap / "pr.json").read_text())["body"]
        return out


class OptinWording(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = run_optin()

    def test_ESE_15_6_optin_run_completes_with_stubs(self):
        r = self.out["result"]
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("contract", self.out)
        self.assertIn("pr_body", self.out)

    def test_ESE_15_6_generated_text_names_spec_author_as_enrolled_role(self):
        for label, text in (("contract intervention", self.out["contract"]["intervention"]),
                            ("PR body", self.out["pr_body"])):
            with self.subTest(label):
                self.assertNotIn("Kiro writes specs", text)
                plain = text.replace("`", "")
                self.assertIn("enrolled in roles.yml", plain)
                self.assertIn("Ky as owner override", plain)

    def test_ESE_15_1_generated_text_keeps_coders_and_merge_roles(self):
        self.assertIn("coders implement specs already on main", self.out["contract"]["intervention"])
        self.assertIn("Ky merges", self.out["pr_body"])


if __name__ == "__main__":
    unittest.main()
