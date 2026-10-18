"""Behavioral positive/negative controls for the maintained evidence runner."""
import copy
import datetime as dt
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "scripts" / "system_quality.py"
SPEC = importlib.util.spec_from_file_location("system_quality", SOURCE)
quality = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(quality)


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="quality-fixture-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        (self.root / "requirements.md").write_text("Synthetic fixture: a check must run and failures must remain failures.\n")
        (self.root / "program.py").write_text("print('fixture check actually executed')\n")
        self.contract = {
            "schema_version":1, "system_id":"fixture", "intended_use":"Isolated runner regression fixture",
            "environment":"offline-unit-fixture",
            "requirements":[{"path":"requirements.md", "sha256":quality.digest(self.root/"requirements.md")}],
            "checks":{"unit":{"command":["{python}","program.py"],"timeout_seconds":10,
                              "inputs":["program.py"],"scope":"Execute the synthetic positive control."}},
            "dimensions":{key:{"acceptance_criteria":["Known failed checks cannot pass."],
                               "check_ids":["unit"] if key=="correctness" else [],
                               "gaps":["No real-world outcomes were tested."],"next_check":"Run intended-use acceptance in a separate controlled environment."}
                          for key in quality.DIMENSIONS},
        }
        self.contract_path = self.root / "definition.json"
        self.save_contract()

    def save_contract(self):
        self.contract_path.write_text(json.dumps(self.contract))

    def run_checks(self):
        self.save_contract()
        quality.run(self.root,"definition.json","results")
        return quality.load(self.root/"results/assessment.json")

    def save_assessment(self, assessment):
        quality.write(self.root/"results/assessment.json",assessment)

    def validate(self, **kwargs):
        return quality.validate(self.root,"results/assessment.json",**kwargs)

    def rewrite_receipt(self, assessment, **updates):
        receipt_path = self.root/assessment["command_receipts"]["unit"]["path"]
        receipt = quality.load(receipt_path)
        receipt.update(updates)
        quality.write(receipt_path,receipt)
        ref = assessment["command_receipts"]["unit"]
        ref["sha256"] = quality.digest(receipt_path)
        assessment["dimensions"]["correctness"]["evidence"] = [copy.deepcopy(ref)]
        self.save_assessment(assessment)

    def test_real_success_keeps_other_dimensions_unknown(self):
        result=self.run_checks()
        self.assertTrue(result["pipeline_passed"])
        self.assertIs(result["readiness_established"],False)
        self.assertEqual(result["dimensions"]["correctness"]["status"],"partial")
        self.assertEqual(result["dimensions"]["operations"]["status"],"not_evaluated")
        self.assertEqual(len(result["dimensions"]),8)
        self.validate()

    def test_failed_process_preserves_receipt_and_fails_gate(self):
        (self.root/"program.py").write_text("raise SystemExit(7)\n")
        with self.assertRaisesRegex(quality.QualityError,"checks failed"):
            self.run_checks()
        assessment=quality.load(self.root/"results/assessment.json")
        self.assertFalse(assessment["pipeline_passed"])
        self.assertEqual(assessment["dimensions"]["correctness"]["status"],"failed")
        self.assertEqual(quality.load(self.root/"results/unit.json")["exit_code"],7)
        with self.assertRaises(quality.QualityError):self.validate()

    def test_missing_executable_is_a_real_failure(self):
        self.contract["checks"]["unit"]["command"]=["/nonexistent-quality-fixture-command"]
        with self.assertRaises(quality.QualityError):self.run_checks()
        self.assertEqual(quality.load(self.root/"results/unit.json")["exit_code"],127)

    def test_timeout_is_retained_and_cannot_pass(self):
        (self.root/"program.py").write_text("import time\ntime.sleep(20)\n")
        self.contract["checks"]["unit"]["timeout_seconds"]=1
        with self.assertRaises(quality.QualityError):self.run_checks()
        receipt=quality.load(self.root/"results/unit.json")
        self.assertTrue(receipt["timed_out"])
        self.assertEqual(receipt["exit_code"],124)

    def test_timeout_stops_descendant_that_ignores_sigterm(self):
        child="import signal,time;from pathlib import Path;signal.signal(signal.SIGTERM,signal.SIG_IGN);Path('ready').write_text('ready');time.sleep(2);Path('child-survived').write_text('unsafe')"
        (self.root/"program.py").write_text(
            "import subprocess,sys,time\nfrom pathlib import Path\n"
            "subprocess.Popen([sys.executable,'-c',"+repr(child)+"])\n"
            "while not Path('ready').exists():time.sleep(.01)\n"
            "time.sleep(20)\n")
        self.contract["checks"]["unit"]["timeout_seconds"]=1
        with self.assertRaises(quality.QualityError):self.run_checks()
        time.sleep(2)
        self.assertTrue((self.root/"ready").exists())
        self.assertFalse((self.root/"child-survived").exists())

    def test_successful_parent_cannot_leave_background_artifact_writer(self):
        child="import time;from pathlib import Path;Path('ready').write_text('ready');time.sleep(1);Path('late-write').write_text('unsafe')"
        (self.root/"program.py").write_text(
            "import subprocess,sys,time\nfrom pathlib import Path\n"
            "subprocess.Popen([sys.executable,'-c',"+repr(child)+"])\n"
            "while not Path('ready').exists():time.sleep(.01)\n")
        self.run_checks()
        time.sleep(1.5)
        self.assertFalse((self.root/"late-write").exists())

    def test_source_mutation_during_check_fails(self):
        (self.root/"program.py").write_text("from pathlib import Path\nPath('program.py').write_text('changed')\n")
        with self.assertRaises(quality.QualityError):self.run_checks()
        self.assertFalse(quality.load(self.root/"results/unit.json")["source_unchanged"])

    def test_definition_change_during_check_leaves_failed_assessment(self):
        (self.root/"program.py").write_text("from pathlib import Path\np=Path('definition.json')\np.write_text(p.read_text()+' ')\n")
        with self.assertRaisesRegex(quality.QualityError,"definition hash mismatch"):self.run_checks()
        assessment=quality.load(self.root/"results/assessment.json")
        self.assertFalse(assessment["pipeline_passed"])
        self.assertIn("hash mismatch",assessment["validation_error"])

    def test_atomic_writer_does_not_follow_preexisting_temporary_symlink(self):
        with tempfile.TemporaryDirectory() as external:
            preserved=Path(external)/"preserved.txt";preserved.write_text("preserve")
            (self.root/"results").mkdir()
            (self.root/"results/unit.json.tmp").symlink_to(preserved)
            quality.write(self.root/"results/unit.json",{"actual":"receipt"})
            self.assertEqual(preserved.read_text(),"preserve")
            self.assertEqual(quality.load(self.root/"results/unit.json"),{"actual":"receipt"})

    def test_all_eight_dimensions_are_required(self):
        for missing in quality.DIMENSIONS:
            with self.subTest(missing=missing):
                contract=copy.deepcopy(self.contract)
                del contract["dimensions"][missing]
                self.contract_path.write_text(json.dumps(contract))
                with self.assertRaises(quality.QualityError):quality.definition(self.root,self.contract_path)

    def test_unknown_dimension_is_rejected(self):
        self.contract["dimensions"]["readiness_score"]={}
        with self.assertRaises(quality.QualityError):self.run_checks()

    def test_reserved_and_case_colliding_check_ids_are_rejected(self):
        original=copy.deepcopy(self.contract["checks"]["unit"])
        for names in (["assessment"],["Assessment"],["unit","Unit"]):
            with self.subTest(names=names):
                self.contract["checks"]={name:copy.deepcopy(original) for name in names}
                self.contract["dimensions"]["correctness"]["check_ids"]=names
                with self.assertRaises(quality.QualityError):self.run_checks()
        self.contract["checks"]={"unit":original}

    def test_empty_criteria_are_rejected(self):
        self.contract["dimensions"]["security"]["acceptance_criteria"]=[""]
        with self.assertRaises(quality.QualityError):self.run_checks()

    def test_every_check_must_be_accounted_for(self):
        self.contract["dimensions"]["correctness"]["check_ids"]=[]
        with self.assertRaises(quality.QualityError):self.run_checks()

    def test_undefined_check_is_rejected(self):
        self.contract["dimensions"]["security"]["check_ids"]=["invented"]
        with self.assertRaises(quality.QualityError):self.run_checks()

    def test_timeout_is_required_and_boolean_is_not_integer(self):
        for bad in (None,0,-1,True,"10",3601):
            with self.subTest(timeout=bad):
                self.contract["checks"]["unit"]["timeout_seconds"]=bad
                self.save_contract()
                with self.assertRaises(quality.QualityError):quality.definition(self.root,self.contract_path)

    def test_requirements_change_invalidates_definition(self):
        (self.root/"requirements.md").write_text("materially changed scope\n")
        with self.assertRaisesRegex(quality.QualityError,"requirements changed"):self.run_checks()

    def test_relative_traversal_and_git_internals_are_rejected(self):
        for name in ("../outside.json","/tmp/outside.json",".git/config","a/../../outside","..\\outside"):
            with self.subTest(name=name):
                with self.assertRaises(quality.QualityError):quality.safe_path(self.root,name)

    def test_symlink_escape_is_rejected(self):
        with tempfile.TemporaryDirectory() as external:
            (self.root/"escape").symlink_to(external,target_is_directory=True)
            with self.assertRaises(quality.QualityError):quality.safe_path(self.root,"escape/proof.json")

    def test_input_glob_must_match_real_files(self):
        self.contract["checks"]["unit"]["inputs"]=["absent-*.py"]
        with self.assertRaises(quality.QualityError):self.run_checks()

    def test_output_cannot_overwrite_unowned_directory(self):
        (self.root/"results").mkdir()
        (self.root/"results/important.txt").write_text("preserve")
        with self.assertRaises(quality.QualityError):self.run_checks()
        self.assertEqual((self.root/"results/important.txt").read_text(),"preserve")

    def test_output_cannot_overlap_source(self):
        self.save_contract()
        with self.assertRaises(quality.QualityError):quality.run(self.root,"definition.json",".")

    def test_changed_input_after_pass_invalidates_evidence(self):
        self.run_checks()
        (self.root/"program.py").write_text("raise SystemExit(2)\n")
        with self.assertRaisesRegex(quality.QualityError,"inputs changed"):self.validate()

    def test_changed_evidence_bytes_are_rejected(self):
        self.run_checks()
        (self.root/"results/unit.json").write_text("{}")
        with self.assertRaisesRegex(quality.QualityError,"hash mismatch"):self.validate()

    def test_missing_receipt_cannot_be_hidden_by_a_pass_flag(self):
        assessment=self.run_checks()
        assessment["command_receipts"]={}
        self.save_assessment(assessment)
        with self.assertRaises(quality.QualityError):self.validate()

    def test_boolean_exit_status_is_rejected(self):
        assessment=self.run_checks()
        self.rewrite_receipt(assessment,exit_code=False)
        with self.assertRaisesRegex(quality.QualityError,"outcome types"):self.validate()

    def test_failed_receipt_cannot_be_relabelled_as_success(self):
        assessment=self.run_checks()
        self.rewrite_receipt(assessment,exit_code=9)
        with self.assertRaises(quality.QualityError):self.validate()

    def test_receipt_environment_cannot_change(self):
        assessment=self.run_checks()
        self.rewrite_receipt(assessment,environment="production")
        with self.assertRaises(quality.QualityError):self.validate()

    def test_revision_mismatch_is_rejected(self):
        assessment=self.run_checks()
        assessment["source"]["revision"]="a"*40
        self.save_assessment(assessment)
        with self.assertRaisesRegex(quality.QualityError,"revision mismatch"):self.validate()

    def test_old_or_future_evidence_is_rejected(self):
        for age in (-1,-3600,90000):
            with self.subTest(age=age):
                assessment=self.run_checks()
                assessment["recorded_at"]=(dt.datetime.now(dt.timezone.utc)-dt.timedelta(seconds=age)).isoformat()
                self.save_assessment(assessment)
                with self.assertRaises(quality.QualityError):self.validate()

    def test_missing_timezone_is_rejected(self):
        assessment=self.run_checks()
        assessment["recorded_at"]="2026-10-17T12:00:00"
        self.save_assessment(assessment)
        with self.assertRaises(quality.QualityError):self.validate()

    def test_gaps_and_next_check_cannot_disappear(self):
        for field,value in (("gaps",[]),("next_check","")):
            with self.subTest(field=field):
                assessment=self.run_checks()
                assessment["dimensions"]["operations"][field]=value
                self.save_assessment(assessment)
                with self.assertRaises(quality.QualityError):self.validate()

    def test_ci_cannot_promote_dimensions_or_claim_readiness(self):
        assessment=self.run_checks()
        assessment["dimensions"]["correctness"]["status"]="demonstrated"
        self.save_assessment(assessment)
        with self.assertRaises(quality.QualityError):self.validate()
        assessment=self.run_checks()
        assessment["readiness_established"]=True
        self.save_assessment(assessment)
        with self.assertRaises(quality.QualityError):self.validate()

    def test_readiness_mode_declines_ci_only_bundle(self):
        self.run_checks()
        with self.assertRaisesRegex(quality.QualityError,"independent"):self.validate(mode="readiness")

    def test_dimension_evidence_cannot_be_swapped(self):
        assessment=self.run_checks()
        assessment["dimensions"]["security"]["evidence"]=assessment["dimensions"]["correctness"]["evidence"]
        self.save_assessment(assessment)
        with self.assertRaisesRegex(quality.QualityError,"mapping mismatch"):self.validate()

    def test_duplicate_json_keys_are_rejected(self):
        self.contract_path.write_text('{"schema_version":1,"schema_version":1}')
        with self.assertRaisesRegex(quality.QualityError,"duplicate JSON key"):quality.load(self.contract_path)

    def test_cli_success_and_failure_status(self):
        for command,expected in ((["run","--definition","definition.json","--output-dir","results"],0),
                                 (["validate","--assessment","results/assessment.json","--mode","readiness"],1)):
            result=subprocess.run([sys.executable,str(SOURCE),*command,"--root",str(self.root)],capture_output=True,text=True,timeout=30)
            self.assertEqual(result.returncode,expected,result.stderr)

    def test_repeated_run_recovers_after_previous_failure(self):
        (self.root/"program.py").write_text("raise SystemExit(1)\n")
        with self.assertRaises(quality.QualityError):self.run_checks()
        (self.root/"program.py").write_text("print('recovered')\n")
        self.run_checks()
        self.validate()


if __name__=="__main__":
    unittest.main()
