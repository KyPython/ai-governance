"""Command-line synthesis for the synthetic infrastructure."""

import argparse
import json
from pathlib import Path

from infra.stack import build_template


def synthesize(output: Path) -> None:
    """Write the template in a stable, reviewable representation."""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(build_template(), indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Synthesize the parcel indexer template")
    parser.add_argument("--output", type=Path, default=Path("build/template.json"))
    args = parser.parse_args()
    synthesize(args.output)


if __name__ == "__main__":
    main()
