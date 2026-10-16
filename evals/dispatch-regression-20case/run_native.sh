#!/usr/bin/env bash
# Invoke Inspect from this script's directory, regardless of the caller's cwd.
set -euo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"
if ! command -v inspect >/dev/null 2>&1; then
  echo "inspect command not found. Activate the Python environment with inspect-ai installed." >&2
  exit 127
fi
if [[ ! -f approval_eval.py ]]; then
  echo "approval_eval.py missing in $HERE. Restore the complete repository checkout and retry." >&2
  exit 1
fi
mkdir -p logs
exec inspect eval ./approval_eval.py --model none --log-dir ./logs "$@"
