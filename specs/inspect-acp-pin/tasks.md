# Tasks: Stop agent-client-protocol 1.0.0 from breaking the eval tests

Spec ID: ACP

One coder, one PR, reviewed by a different agent. No task edits `specs/`.

- [ ] 1. Add `agent-client-protocol==0.12.1` to `requirements.txt` (ACP-1.1, ACP-2.1). In a fresh virtual environment, run `python3 -m pip install -r requirements.txt`, record both installed versions, then run `python3 -m pytest -q` in `evals/delegation-judgment` (ACP-1.2) and at the repository root (ACP-2.2). Record pass and fail counts and compare any root failure against `8da4ed4`.
- [ ] 2. On the code PR, confirm `ai-governance / quality` and `system-quality` show no `acp.helpers` error (ACP-1.3), and that no test file changed (ACP-1.4).
