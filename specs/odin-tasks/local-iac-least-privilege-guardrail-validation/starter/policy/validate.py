"""Run the starter project's local infrastructure guardrails."""

import argparse
import json
from pathlib import Path
from typing import Any


class PolicyViolation(ValueError):
    """Raised when a template violates a configured guardrail."""


def validate(template: dict[str, Any]) -> None:
    """Validate the starter's existing infrastructure invariants."""
    resources = template.get("Resources", {})
    if not resources:
        raise PolicyViolation("template must define resources")

    for logical_id, resource in resources.items():
        resource_type = resource.get("Type")
        properties = resource.get("Properties", {})
        if resource_type == "AWS::S3::Bucket":
            public_block = properties.get("PublicAccessBlockConfiguration", {})
            if not public_block or not all(public_block.values()):
                raise PolicyViolation(f"{logical_id} must block every form of public access")
        if resource_type == "AWS::SQS::Queue" and not properties.get("KmsMasterKeyId"):
            raise PolicyViolation(f"{logical_id} must enable server-side encryption")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a synthesized template")
    parser.add_argument("template", type=Path)
    args = parser.parse_args()
    validate(json.loads(args.template.read_text()))
    print(f"policy checks passed: {args.template}")


if __name__ == "__main__":
    main()
