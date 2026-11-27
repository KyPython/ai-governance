"""Shared test harness for the spec-author delegation check (SAD, specs/spec-author-delegation-check).

SAD task T2 (SAD-6.1 to SAD-6.4). This module holds fixtures and helpers only. It asserts no SAD behavior:
the tests that do are shipped by T4, T3 and T5 together with the behavior that makes them pass.

It reuses the real policy-job script from tests/test_policy.py (the `policy` step of
.github/workflows/governance.yml), so every scenario runs the actual gate, not a mock.
"""
import os
import tempfile
from pathlib import Path

from test_policy import GIT_ISOLATION, KIRO, KY, POLICY, Repo, sh

# Scenario -> the SAD task whose PR ships the test for it and turns it green (tasks.md, "Dependency order").
SCENARIO_TASK = {
    **{s: "T4" for s in ("A7", "A10", "P3")},
    **{s: "T3" for s in ("P1", "P2", "A1", "A2", "A3", "A4", "A5", "A6", "A8", "A9", "A11", "A14", "A15")},
    **{s: "T5" for s in ("A12", "A13")},
}

# A delegation-required, non-owner identity enrolled as spec author ("identity D" in scenarios.md).
DELEGATE = ("delegate-bot[bot]", "999+delegate-bot[bot]@users.noreply.github.com")

ROLES_WITH_DELEGATE = (
    "version: 1\nowner: KyPython\nspec_paths:\n  - specs/\n  - .kiro/specs/\nroles:\n"
    "  spec-author:\n    identities:\n      - KyPython\n      - kiro-agent[bot]\n      - delegate-bot[bot]\n"
    "  coder:\n    identities:\n      - cursor[bot]\n      - kiro-agent[bot]\n      - codex\n"
)

# Proposed file location per decision D3 on #238; the schema itself is T4's.
DELEGATIONS_PATH = "delegations.yml"


def delegation_yaml(records):
    """Render delegation records as YAML text. Each record is a dict; values are written as given."""
    lines = ["version: 1", "delegations:"]
    for rec in records:
        first = True
        for key, value in rec.items():
            if isinstance(value, (list, tuple)):
                rendered = "[" + ", ".join(str(v) for v in value) + "]"
            elif isinstance(value, bool):
                rendered = "true" if value else "false"
            else:
                rendered = str(value)
            lines.append(("  - " if first else "    ") + f"{key}: {rendered}")
            first = False
    return "\n".join(lines) + "\n"


class SadRepo(Repo):
    """A throwaway repo whose base branch can hold a delegation file introduced at a chosen time."""

    def __init__(self, base_files=None, roles=ROLES_WITH_DELEGATE):
        super().__init__(base_files)
        # Keep the harness role map outside the repo so it never shows up as a changed path in the PR diff.
        self.roles_tmp = tempfile.TemporaryDirectory()
        self.sad_roles = Path(self.roles_tmp.name) / "roles.yml"
        self.sad_roles.write_text(roles)

    def cleanup(self):
        self.roles_tmp.cleanup()
        self.tmp.cleanup()

    def commit_at(self, msg, when, author=KY, committer=None):
        """Commit with author and committer dates fixed to `when` (ISO 8601), so ordering is controlled."""
        committer = committer or author
        env = dict(os.environ, **GIT_ISOLATION, GIT_AUTHOR_NAME=author[0], GIT_AUTHOR_EMAIL=author[1],
                   GIT_COMMITTER_NAME=committer[0], GIT_COMMITTER_EMAIL=committer[1],
                   GIT_AUTHOR_DATE=when, GIT_COMMITTER_DATE=when)
        sh(self.dir, "git", "add", "-A")
        sh(self.dir, "git", "commit", "-q", "--allow-empty", "-m", msg, env=env)
        return sh(self.dir, "git", "rev-parse", "HEAD")

    def put_on_base(self, files, when, author=KY):
        """Add `files` to main at time `when`, then move the feature branch onto the new base."""
        sh(self.dir, "git", "checkout", "-q", "main")
        self.write(files)
        self.base = self.commit_at("base change", when, author)
        sh(self.dir, "git", "checkout", "-q", "-B", "feature", "main")
        return self.base

    def commit_time(self, sha):
        return sh(self.dir, "git", "show", "-s", "--format=%cI", sha)

    def run_policy(self, pr_created_at=None, script=None, **kwargs):
        """Run the real policy script. `pr_created_at` is passed as PR_CREATED_AT for the T3 check.

        `script` replaces the policy script only in harness self-tests, to prove a broken script is caught.
        """
        saved = os.environ.get("PR_CREATED_AT")
        try:
            if pr_created_at:
                os.environ["PR_CREATED_AT"] = pr_created_at
            kwargs.setdefault("roles", self.sad_roles)
            return self.policy(**kwargs) if script is None else _policy_with(self, script, **kwargs)
        finally:
            if saved is None:
                os.environ.pop("PR_CREATED_AT", None)
            else:
                os.environ["PR_CREATED_AT"] = saved


def _policy_with(repo, script, **kwargs):
    """Same as Repo.policy, with an explicit script body (used only by harness self-tests)."""
    import subprocess
    head = repo.commit("change", kwargs.get("author", KY), kwargs.get("committer"))
    summary = repo.dir / ".summary"
    env = dict(os.environ, **GIT_ISOLATION, EVENT_NAME="pull_request", PR_TITLE=kwargs.get("title", "docs(spec): x"),
               PR_BODY=kwargs.get("body", "Relates to #1"), PR_BASE_SHA=repo.base, PR_HEAD_SHA=head, PR_HEAD_REF="feature",
               PUSH_BEFORE="", PUSH_AFTER=head, REQUIRE_ISSUE="false", ENFORCE_TITLE="true", STC_MODE="off",
               BASELINE_MODE="changed", PR_AUTHOR=kwargs.get("opener", "KyPython"), REPO=kwargs.get("repo", "KyPython/demo"),
               ROLES_FILE=str(kwargs.get("roles", repo.sad_roles)), GITHUB_STEP_SUMMARY=str(summary), GITHUB_OUTPUT=os.devnull)
    p = subprocess.run(["python3", "-c", script], check=False, cwd=repo.dir, env=env, capture_output=True, text=True)
    summary.unlink(missing_ok=True)
    return p.returncode, p.stdout + p.stderr


__all__ = [
    "DELEGATE",
    "DELEGATIONS_PATH",
    "KIRO",
    "KY",
    "POLICY",
    "ROLES_WITH_DELEGATE",
    "SCENARIO_TASK",
    "SadRepo",
    "delegation_yaml",
]
