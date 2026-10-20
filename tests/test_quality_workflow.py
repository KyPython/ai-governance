"""Execute the actual reusable workflow's install step with fixture package tools."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest


WORKFLOW=Path(__file__).resolve().parents[1]/".github/workflows/governance.yml"


def workflow_step(marker):
    lines=WORKFLOW.read_text().splitlines()
    start=lines.index(marker)
    block=next(i for i in range(start,len(lines)) if lines[i]=="        run: |")+1
    end=next((i for i in range(block,len(lines)) if lines[i].strip() and not lines[i].startswith("          ")),len(lines))
    return textwrap.dedent("\n".join(lines[block:end]))+"\n"


class InstallFailureControls(unittest.TestCase):
    def fixture(self, pyproject=None, install_failure=False, setup=False):
        temporary=tempfile.TemporaryDirectory(prefix="quality-install-fixture-")
        self.addCleanup(temporary.cleanup)
        root=Path(temporary.name)
        binaries=root/"bin";binaries.mkdir()
        # No network/package installation: every pip invocation uses this local
        # executable. Non-pip Python calls (tomllib) use the real interpreter.
        pip=binaries/"pip"
        pip.write_text("#!"+sys.executable+"\n"+textwrap.dedent("""
            import json,os,sys
            with open(os.environ['QUALITY_FIXTURE_CALLS'],'a') as stream:
                stream.write(json.dumps(sys.argv[1:])+'\\n')
            if '-e' in sys.argv and os.environ.get('QUALITY_FIXTURE_INSTALL_FAIL')=='1':
                raise SystemExit(13)
        """))
        pip.chmod(0o755)
        python=binaries/"python"
        python.write_text("#!"+sys.executable+"\n"+textwrap.dedent("""
            import os,sys
            from pathlib import Path
            if sys.argv[1:3]==['-m','pip']:
                os.execv(str(Path(__file__).with_name('pip')),['pip',*sys.argv[3:]])
            os.execv(sys.executable,[sys.executable,*sys.argv[1:]])
        """))
        python.chmod(0o755)
        if pyproject is not None:(root/"pyproject.toml").write_text(pyproject)
        if setup:(root/"setup.py").write_text("raise RuntimeError('must not actually install fixture')")
        script=root/"step.sh";script.write_text(workflow_step("      - name: Install, lint, type-check, test, build"))
        environment={"PATH":str(binaries)+os.pathsep+os.defpath,"PM":"python","REQUIRE_TESTS":"false",
                     "GITHUB_STEP_SUMMARY":str(root/"summary"),"QUALITY_FIXTURE_CALLS":str(root/"calls"),
                     "QUALITY_FIXTURE_INSTALL_FAIL":"1" if install_failure else "0"}
        result=subprocess.run(["/bin/bash",str(script)],cwd=root,env=environment,capture_output=True,text=True,timeout=20)
        calls=[json.loads(line) for line in (root/"calls").read_text().splitlines()]
        return result,calls

    def test_install_failure_stops_actual_workflow_step(self):
        result,calls=self.fixture('[project]\nname="fixture"\nversion="0.0.0"\n',True)
        self.assertEqual(result.returncode,13,result.stderr)
        self.assertIn(["install","-e","."],calls)
        self.assertNotIn(["install","ruff","mypy","pytest"],calls)

    def test_declared_extra_is_selected_without_a_fallback_install(self):
        result,calls=self.fixture('[project]\nname="fixture"\nversion="0.0.0"\n[project.optional-dependencies]\ndev=[]\n',True)
        self.assertEqual(result.returncode,13,result.stderr)
        self.assertEqual([call for call in calls if "-e" in call],[["install","-e",".[dev]"]])

    def test_tool_only_pyproject_is_not_a_failed_package_install(self):
        result,calls=self.fixture('[tool.pytest.ini_options]\naddopts="-q"\n',True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertFalse(any("-e" in call for call in calls))

    def test_legacy_setup_install_failure_is_not_ignored(self):
        result,calls=self.fixture(install_failure=True,setup=True)
        self.assertEqual(result.returncode,13,result.stderr)


class VerdictControls(unittest.TestCase):
    def verdict(self,quality="success",policy="success",secrets="success",run_quality="true",definition="",prerequisite="success"):
        with tempfile.TemporaryDirectory(prefix="quality-verdict-fixture-") as directory:
            root=Path(directory)
            script=root/"verdict.sh";script.write_text(workflow_step("      - id: v"))
            environment={"PATH":os.defpath,"QUALITY":quality,"POLICY":policy,"SECRETS":secrets,"RUN_QUALITY":run_quality,
                         "SYSTEM_QUALITY_DEFINITION":definition,"PREREQUISITE_RESULT":prerequisite,"GITHUB_OUTPUT":str(root/"output"),"GITHUB_STEP_SUMMARY":str(root/"summary")}
            result=subprocess.run(["/bin/bash",str(script)],cwd=root,env=environment,capture_output=True,text=True,timeout=10)
            return result,(root/"output").read_text()

    def test_required_jobs_fail_closed(self):
        for key in ("quality","policy","secrets"):
            for status in ("failure","cancelled","skipped"):
                with self.subTest(job=key,status=status):
                    result,output=self.verdict(**{key:status})
                    self.assertNotEqual(result.returncode,0)
                    self.assertIn("verdict=fail",output)

    def test_successful_scoped_checks_do_not_require_skipping_quality(self):
        result,output=self.verdict(definition=".quality/system.json")
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn("verdict=pass",output)

    def test_explicit_legacy_external_quality_can_still_skip(self):
        result,output=self.verdict(quality="skipped",run_quality="false")
        self.assertEqual(result.returncode,0,result.stderr)

    def test_evidence_opt_in_cannot_silently_skip_its_quality_job(self):
        result,output=self.verdict(quality="skipped",run_quality="false",definition=".quality/system.json")
        self.assertNotEqual(result.returncode,0)
        self.assertIn("verdict=fail",output)

    def test_external_prerequisite_must_be_actual_success(self):
        for value in ("failure","skipped","cancelled","","SUCCESS"):
            with self.subTest(value=value):
                result,output=self.verdict(quality="skipped",run_quality="false",prerequisite=value)
                self.assertNotEqual(result.returncode,0)
                self.assertIn("verdict=fail",output)


if __name__=="__main__":unittest.main()
