import copy
import unittest

from infra.stack import build_template
from policy.validate import PolicyViolation, validate


class PolicyTests(unittest.TestCase):
    def test_baseline_template_satisfies_existing_guardrails(self) -> None:
        validate(build_template())

    def test_public_bucket_is_rejected(self) -> None:
        template = copy.deepcopy(build_template())
        public_block = template["Resources"]["ParcelRecordsBucket"]["Properties"][
            "PublicAccessBlockConfiguration"
        ]
        public_block["BlockPublicPolicy"] = False

        with self.assertRaisesRegex(PolicyViolation, "block every form of public access"):
            validate(template)

    def test_unencrypted_queue_is_rejected(self) -> None:
        template = copy.deepcopy(build_template())
        del template["Resources"]["ParcelEventsQueue"]["Properties"]["KmsMasterKeyId"]

        with self.assertRaisesRegex(PolicyViolation, "server-side encryption"):
            validate(template)


if __name__ == "__main__":
    unittest.main()
