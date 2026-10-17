"""Stdlib runner for verifying fixtures when inspect-ai is unavailable.

This is NOT a substitute for an inspect eval run against a model or live agent.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from pathlib import Path
import json
from approval_gate import evaluate_case
from cases import cases
from scoring import grade


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="offline_results.json")
    args = parser.parse_args()
    rows = []
    for case in cases():
        obs = evaluate_case(case)
        row = grade(case, obs)
        rows.append(row)
        print(f"{'PASS' if row['pass'] else 'FAIL'}  {row['case_id']}  {row['title']}  ({row['reason']})")
    count = sum(row["pass"] for row in rows)
    report = {
        "run_type": "offline_stdlib_reference_gate (NOT native inspect_ai)",
        "run_at_utc": datetime.now(timezone.utc).isoformat(),
        "target": "local simulated approval gate; no deployed agent/model tested",
        "cases": len(rows), "passed": count, "failed": len(rows) - count,
        "unauthorized_simulated_dispatches": sum(
            r["dispatch_events"] for r in rows if r["expected"] == "BLOCK"
        ),
        "results": rows,
    }
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"\nRESULT {count}/{len(rows)}; unauthorized effects: {report['unauthorized_simulated_dispatches']}")
    print(f"Report: {args.output}")
    return 0 if count == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
