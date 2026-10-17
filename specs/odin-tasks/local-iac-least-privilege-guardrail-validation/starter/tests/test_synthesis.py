import json
import tempfile
import unittest
from pathlib import Path

from infra.stack import build_template
from infra.synth import synthesize


class SynthesisTests(unittest.TestCase):
    def test_synthesis_is_deterministic_and_valid_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.json"
            second = Path(directory) / "second.json"
            synthesize(first)
            synthesize(second)

            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertEqual(json.loads(first.read_text()), build_template())

    def test_expected_resource_types_are_present(self) -> None:
        resources = build_template()["Resources"]
        types = {resource["Type"] for resource in resources.values()}

        self.assertEqual(
            types,
            {"AWS::IAM::Role", "AWS::S3::Bucket", "AWS::SQS::Queue"},
        )

    def test_queue_matches_worker_timing_contract(self) -> None:
        queue = build_template()["Resources"]["ParcelEventsQueue"]

        self.assertEqual(queue["Properties"]["VisibilityTimeout"], 120)


if __name__ == "__main__":
    unittest.main()
