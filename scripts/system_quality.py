#!/usr/bin/env python3
"""Run scoped checks and validate eight-dimension CI evidence (Python 3.11+).

This tool validates CI evidence; it does not certify independent operational
outcomes, authorize a merge/deploy, or establish whole-system readiness.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile
import time

DIMENSIONS = (
    "correctness", "security", "reliability", "data_integrity",
    "observability", "delivery", "operations", "outcome_evidence",
)
STATUSES = {"demonstrated", "partial", "failed", "not_evaluated"}
MARKER = ".system-quality-output-v1"
CI_LIMIT = "Automated checks cover the declared scope; independent intended-use readiness is not established."


class QualityError(ValueError):
    """A malformed contract or invalid/failing evidence bundle."""


def require(condition, message):
    if not condition:
        raise QualityError(message)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip()) and "\x00" not in value


def strings(value, *, minimum=0):
    return isinstance(value, list) and len(value) >= minimum and all(nonempty(x) for x in value)


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def safe_path(root, value):
    require(nonempty(value), "path must be a nonempty relative path")
    require("\\" not in value, "backslashes are not portable relative paths")
    path = Path(value)
    require(not path.is_absolute() and ".." not in path.parts and ".git" not in path.parts,
            f"path is outside the permitted project scope: {value}")
    resolved = (root / path).resolve()
    require(resolved.is_relative_to(root), f"path escapes the project: {value}")
    return resolved


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load(path):
    require(path.is_file(), f"missing JSON document: {path.name}")
    require(path.stat().st_size <= 2 * 1024 * 1024, "JSON document exceeds 2MiB")
    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_pairs)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise QualityError(f"invalid JSON document: {path.name}") from error
    require(isinstance(value, dict), "JSON document must be an object")
    return value


def write(path, value):
    # Exclusive creation avoids following a pre-existing temporary-file symlink.
    descriptor, name = tempfile.mkstemp(prefix=".quality-", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(json.dumps(value, indent=2, sort_keys=True) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def check_time(value, maximum_age):
    require(nonempty(value), "recorded_at is missing")
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise QualityError("recorded_at is invalid") from error
    require(parsed.tzinfo is not None, "recorded_at must include a timezone")
    age = (dt.datetime.now(dt.timezone.utc) - parsed).total_seconds()
    require(0 <= age <= maximum_age, "evidence is stale or dated in the future")


def revision(root):
    try:
        result = subprocess.run(["git", "rev-parse", "--verify", "HEAD"], cwd=root,
                                text=True, capture_output=True, timeout=10, check=False)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise QualityError("could not establish source revision") from error
    return result.stdout.strip() if result.returncode == 0 else "unversioned"


def definition(root, path):
    data = load(path)
    require(type(data.get("schema_version")) is int and data["schema_version"] == 1, "unsupported definition schema_version")
    for key in ("system_id", "intended_use", "environment"):
        require(nonempty(data.get(key)), f"definition requires {key}")
    requirements = data.get("requirements")
    require(isinstance(requirements, list) and bool(requirements), "hashed governing requirements are required")
    seen = set()
    for item in requirements:
        require(isinstance(item, dict), "requirement must be an object")
        p = safe_path(root, item.get("path"))
        require(p.is_file(), "governing requirement file is missing")
        require(item.get("path") not in seen, "duplicate requirement path")
        seen.add(item["path"])
        require(item.get("sha256") == digest(p), f"governing requirements changed: {item['path']}")
    checks = data.get("checks")
    require(isinstance(checks, dict) and 1 <= len(checks) <= 64, "define between1 and64 checks")
    require(len({key.casefold() for key in checks}) == len(checks) and "assessment" not in {key.casefold() for key in checks},
            "check IDs collide with each other or a reserved assessment filename")
    for key, check in checks.items():
        require(isinstance(key, str) and re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_.-]{0,79}", key), "invalid check ID")
        require(isinstance(check, dict), f"check {key} must be an object")
        require(strings(check.get("command"), minimum=1), f"check {key} requires argv command")
        timeout = check.get("timeout_seconds")
        require(type(timeout) is int and 1 <= timeout <= 3600, f"check {key} requires a finite1..3600second timeout")
        require(strings(check.get("inputs"), minimum=1), f"check {key} requires scoped source inputs")
        require(nonempty(check.get("scope")), f"check {key} requires scope")
        require(safe_path(root, check.get("cwd", ".")).is_dir(), f"check {key} cwd is missing")
        for pattern in check["inputs"]:
            safe_path(root, pattern)
    dimensions = data.get("dimensions")
    require(isinstance(dimensions, dict) and set(dimensions) == set(DIMENSIONS), "exactly all eight dimensions are required")
    covered = set()
    for key, item in dimensions.items():
        require(isinstance(item, dict), f"dimension {key} must be an object")
        require(strings(item.get("acceptance_criteria"), minimum=1), f"dimension {key} needs acceptance criteria")
        require(strings(item.get("gaps")), f"dimension {key} gaps must be a string array")
        require(nonempty(item.get("next_check")), f"dimension {key} needs next_check")
        ids = item.get("check_ids")
        require(strings(ids) and len(ids) == len(set(ids)), f"dimension {key} check_ids must be unique strings")
        require(set(ids) <= set(checks), f"dimension {key} names an undefined check")
        covered.update(ids)
    require(covered == set(checks), "every declared check must map to a dimension")
    return data


def inputs(root, patterns):
    result = {}
    for pattern in patterns:
        matches = [p for p in root.glob(pattern) if p.is_file()]
        require(bool(matches), f"input pattern matched no files: {pattern}")
        for candidate in matches:
            relative = candidate.relative_to(root).as_posix()
            path = safe_path(root, relative)
            result[relative] = digest(path)
            require(len(result) <= 10000, "source input set exceeds10000files")
    return dict(sorted(result.items()))


def argv(check):
    return [sys.executable if value == "{python}" else value for value in check["command"]]


def execute(root, check):
    started = time.monotonic()
    timeout = False
    spawn_error = None
    try:
        process = subprocess.Popen(argv(check), cwd=safe_path(root, check.get("cwd", ".")),
                                   start_new_session=True)
        try:
            code = process.wait(timeout=check["timeout_seconds"])
        except subprocess.TimeoutExpired:
            timeout = True
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                pass
            # The parent may exit on SIGTERM while descendants ignore it.
            # Always finish terminating the owned group, not just the parent.
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
            code = 124
        finally:
            # Checks are bounded jobs. A finished parent must not leave an
            # owned background process writing evidence after it was hashed.
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
    except OSError as error:
        code = 127
        spawn_error = type(error).__name__
    return dict(exit_code=code, timed_out=timeout, spawn_error=spawn_error,
                duration_seconds=round(time.monotonic() - started, 3))


def prepare_output(root, name, source_files):
    path = safe_path(root, name)
    require(path != root and not any(p == path or path in p.parents for p in source_files),
            "output directory overlaps source inputs")
    marker = safe_path(root, (path / MARKER).relative_to(root).as_posix())
    if path.exists():
        require(path.is_dir() and marker.is_file() and marker.read_text() == "system-quality-v1\n",
                "output directory already exists and is not owned by system-quality")
    else:
        path.mkdir(parents=True)
        marker.write_text("system-quality-v1\n")
    return path


def reference(root, path, data, scope):
    return dict(kind="command", path=path.relative_to(root).as_posix(), sha256=digest(path),
                scope=scope, revision=data["source"]["revision"], environment=data["environment"], recorded_at=now())


def run(root, definition_name, output_name):
    path = safe_path(root, definition_name)
    data = definition(root, path)
    definition_hash = digest(path)
    snapshots = {key: inputs(root, check["inputs"]) for key, check in data["checks"].items()}
    source_files = {safe_path(root, p) for values in snapshots.values() for p in values}
    source_files.add(path)
    source_files.update(safe_path(root, r["path"]) for r in data["requirements"])
    out = prepare_output(root, output_name, source_files)
    data = {**data, "source": {"revision": revision(root)}}
    receipts = {}
    failed = set()
    for key, check in data["checks"].items():
        print(f"system-quality: running {key} ({check['scope']})", flush=True)
        outcome = execute(root, check)
        try:
            unchanged = inputs(root, check["inputs"]) == snapshots[key] and revision(root) == data["source"]["revision"]
        except QualityError:
            unchanged = False
        receipt = dict(schema_version=1, system_id=data["system_id"], check_id=key,
                       revision=data["source"]["revision"], environment=data["environment"], recorded_at=now(),
                       command=check["command"], resolved_command=argv(check), scope=check["scope"],
                       input_hashes=snapshots[key], source_unchanged=unchanged, **outcome)
        target = out / (key + ".json")
        write(target, receipt)
        receipts[key] = reference(root, target, data, check["scope"])
        if outcome["exit_code"] != 0 or outcome["timed_out"] or not unchanged:
            failed.add(key)
            print(f"system-quality: {key} failed: exit_code={outcome['exit_code']} "
                  f"timed_out={outcome['timed_out']} source_unchanged={unchanged}", file=sys.stderr, flush=True)
    dimensions = {}
    for key, item in data["dimensions"].items():
        status = "failed" if failed.intersection(item["check_ids"]) else "partial" if item["check_ids"] else "not_evaluated"
        dimensions[key] = dict(status=status, acceptance_criteria=item["acceptance_criteria"],
                               check_ids=item["check_ids"], evidence=[receipts[c] for c in item["check_ids"]],
                               gaps=list(dict.fromkeys(item["gaps"] + [CI_LIMIT])), next_check=item["next_check"])
    assessment = dict(schema_version=1, system_id=data["system_id"], intended_use=data["intended_use"],
                      environment=data["environment"], source=data["source"], recorded_at=now(),
                      definition={"path":path.relative_to(root).as_posix(), "sha256":definition_hash},
                      requirements=data["requirements"], command_receipts=receipts, dimensions=dimensions,
                      pipeline_passed=not failed, readiness_established=False)
    write(out / "assessment.json", assessment)
    if failed:
        raise QualityError("declared checks failed: " + ", ".join(sorted(failed)))
    try:
        validate(root, (out / "assessment.json").relative_to(root).as_posix(), 86400, "ci")
    except QualityError as error:
        assessment["pipeline_passed"] = False
        assessment["validation_error"] = str(error)
        write(out / "assessment.json", assessment)
        raise
    print("system-quality: declared checks and evidence passed; readiness_established=false")


def validate(root, assessment_name, maximum_age=86400, mode="ci"):
    require(type(maximum_age) is int and 1 <= maximum_age <= 31 * 86400, "maximum evidence age is invalid")
    assessment = load(safe_path(root, assessment_name))
    require(type(assessment.get("schema_version")) is int and assessment["schema_version"] == 1, "unsupported assessment schema_version")
    ref = assessment.get("definition")
    require(isinstance(ref, dict), "definition reference is required")
    path = safe_path(root, ref.get("path"))
    require(path.is_file() and ref.get("sha256") == digest(path), "definition hash mismatch")
    data = definition(root, path)
    for key in ("system_id", "intended_use", "environment", "requirements"):
        require(assessment.get(key) == data[key], f"assessment {key} does not match definition")
    require(assessment.get("source") == {"revision":revision(root)}, "assessment source revision mismatch")
    check_time(assessment.get("recorded_at"), maximum_age)
    refs = assessment.get("command_receipts")
    require(isinstance(refs, dict) and set(refs) == set(data["checks"]), "every declared command receipt is required")
    failed = set()
    for key, check in data["checks"].items():
        ref = refs[key]
        require(isinstance(ref, dict) and ref.get("kind") == "command", "command evidence reference is invalid")
        for field in ("scope", "revision", "environment", "recorded_at"):
            require(nonempty(ref.get(field)), f"evidence requires {field}")
        require(ref["revision"] == assessment["source"]["revision"] and ref["environment"] == data["environment"] and ref["scope"] == check["scope"], "evidence context mismatch")
        check_time(ref["recorded_at"], maximum_age)
        receipt_path = safe_path(root, ref.get("path"))
        require(receipt_path.is_file() and ref.get("sha256") == digest(receipt_path), "command evidence hash mismatch")
        receipt = load(receipt_path)
        for field, expected in (("schema_version",1),("system_id",data["system_id"]),("check_id",key),
                                ("revision",assessment["source"]["revision"]),("environment",data["environment"]),
                                ("command",check["command"]),("scope",check["scope"])):
            require(receipt.get(field) == expected and (field != "schema_version" or type(receipt.get(field)) is int), f"command receipt {field} mismatch")
        check_time(receipt.get("recorded_at"), maximum_age)
        require(type(receipt.get("exit_code")) is int and type(receipt.get("timed_out")) is bool, "invalid command outcome types")
        require(receipt.get("input_hashes") == inputs(root, check["inputs"]), "command source inputs changed")
        require(type(receipt.get("source_unchanged")) is bool, "source_unchanged outcome is missing")
        if receipt["exit_code"] != 0 or receipt["timed_out"] or not receipt["source_unchanged"]:
            failed.add(key)
    dimensions = assessment.get("dimensions")
    require(isinstance(dimensions, dict) and set(dimensions) == set(DIMENSIONS), "exactly all eight assessed dimensions are required")
    for key, expected in data["dimensions"].items():
        item = dimensions[key]
        require(isinstance(item, dict) and item.get("status") in STATUSES, f"invalid dimension {key}")
        status = "failed" if failed.intersection(expected["check_ids"]) else "partial" if expected["check_ids"] else "not_evaluated"
        require(item["status"] == status, "CI evidence cannot be promoted to independently demonstrated readiness")
        require(item.get("acceptance_criteria") == expected["acceptance_criteria"] and item.get("check_ids") == expected["check_ids"], "dimension acceptance/check mapping mismatch")
        require(item.get("evidence") == [refs[c] for c in expected["check_ids"]], "dimension evidence mapping mismatch")
        require(strings(item.get("gaps"), minimum=1) and set(expected["gaps"]) <= set(item["gaps"]), "unresolved gaps must remain visible")
        require(item.get("next_check") == expected["next_check"], "dimension next_check mismatch")
    require(assessment.get("pipeline_passed") is (not failed), "pipeline outcome contradicts command evidence")
    require(assessment.get("readiness_established") is False, "CI alone cannot establish system readiness")
    require(not failed, "failed/timed-out commands cannot pass the evidence gate")
    require(mode == "ci", "readiness requires independent intended-use evidence; this CI bundle does not certify it")
    return assessment


def main(argv_values=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    execute_parser = commands.add_parser("run", help="execute declared scoped checks and retain actual evidence")
    execute_parser.add_argument("--root", default=".")
    execute_parser.add_argument("--definition", default=".quality/system.json")
    execute_parser.add_argument("--output-dir", default=".quality-results")
    verify = commands.add_parser("validate", help="validate an actual CI evidence bundle, not overall readiness")
    verify.add_argument("--root", default=".")
    verify.add_argument("--assessment", default=".quality-results/assessment.json")
    verify.add_argument("--max-age-seconds", type=int, default=86400)
    verify.add_argument("--mode", choices=("ci", "readiness"), default="ci")
    args = parser.parse_args(argv_values)
    root = Path(args.root).resolve()
    try:
        require(root.is_dir(), "project root does not exist")
        if args.action == "run":
            run(root, args.definition, args.output_dir)
        else:
            validate(root, args.assessment, args.max_age_seconds, args.mode)
            print("system-quality: CI evidence valid; readiness_established=false")
    except (QualityError, OSError) as error:
        print(f"system-quality: FAIL: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
